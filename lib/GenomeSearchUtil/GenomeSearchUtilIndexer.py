# -*- coding: utf-8 -*-
import os
import json
import time
import subprocess
import traceback
import string
import tempfile
from biokbase.workspace.client import Workspace as workspaceService
from GenomeSearchUtil.CombinedLineIterator import CombinedLineIterator
from itertools import product


def _eval_structured_query(split_line, structured_query, prop_dict):
    if not isinstance(structured_query, dict):
        raise ValueError('structured_query should be a dictionary object')
    conditions = []
    for key, val in structured_query.items():
        if key == "$not":
            conditions.append(not _eval_structured_query(split_line, val, prop_dict))
        elif key == "$or":
            conditions.append(any(_eval_structured_query(split_line, x, prop_dict) for x in val))
        elif key == "$and":
            conditions.append(all(_eval_structured_query(split_line, x, prop_dict) for x in val))
        elif key in prop_dict:
            # have to adjust to account for the clipped line
            conditions.append(split_line[prop_dict[key]['col']-2] == val)
        else:
            raise ValueError("Unrecognised field in query {}. Should be one of {} or $and, $or "
                             "or $not".format(key, ", ".join(prop_dict.keys())))
    return all(conditions)


class GenomeSearchUtilIndexer:

    def __init__(self, config):
        self.feature_column_props_map = {
            "feature_id": {"col": 2, "type": ""},
            "feature_type": {"col": 3, "type": ""},
            "contig_id": {"col": 4, "type": ""},
            "start": {"col": 5, "type": "n"},
            "strand": {"col": 6, "type": ""},
            "length": {"col": 7, "type": "n"},
            "function": {"col": 9, "type": ""}
        }
        self.contig_column_props_map = {
            "contig_id": {"col": 1, "type": ""}, 
            "length": {"col": 2, "type": "n"}, 
            "feature_count": {"col": 3, "type": "n"}
        }
        self.ws_url = config["workspace-url"]
        self.genome_index_dir = config["genome-index-dir"]
        if not os.path.isdir(self.genome_index_dir):
            os.makedirs(self.genome_index_dir)
        self.debug = "debug" in config and config["debug"] == "1"
        self.max_sort_mem_size = 250000
        self.unicode_comma = u"\uFF0C"
    
    def search(self, token, ref, query, structured_query, sort_by, start, limit, num_found):
        if query is None:
            query = ""
        if start is None:
            start = 0
        if limit is None:
            limit = 50
        if self.debug:
            print("Search: genome={}, query=[{}], structured_query=[{}] sort-by=[{}], start={}, "
                  "limit={}".format(ref, query, structured_query, self.get_sorting_code(
                        self.feature_column_props_map, sort_by), start, limit))
        t1 = time.time()
        inner_chsum = self.check_feature_cache(ref, token)
        index_iter = self.get_feature_sorted_iterator(inner_chsum, sort_by)
        ret = self.filter_feature_query(index_iter, query, structured_query, start, limit,
                                        num_found)
        if self.debug:
            print("    (overall-time=" + str(time.time() - t1) + ")")
        return ret

    def to_text(self, mapping, key):
        if key not in mapping or mapping[key] is None:
            return ""
        value = mapping[key]
        if isinstance(value, list):
            return ",".join(str(x[1]) if isinstance(x, list) else str(x)
                            for x in value)
        return str(value)

    def save_feature_tsv(self, genome, inner_chsum):
        features = []
        for feat_array in (('features', 'gene'), ('mrnas', 'mRNA'),
                           ('cdss', 'CDS'), ('non_coding_features', 'gene')):
            for i, feat in enumerate(genome.get(feat_array[0], [])):
                if 'type' not in feat:
                    feat['type'] = feat_array[1]
                feat['src_arr'] = feat_array[0]
                feat['index'] = i
                features.append(feat)
        outfile = tempfile.NamedTemporaryFile(dir=self.genome_index_dir,
                prefix=inner_chsum + "_ftr_", suffix=".tsv", delete=False)
        with outfile:
            pos = 0
            for feature in features:
                obj = {"p": feature['index'], 'arr': feature['src_arr']}
                pos += 1
                ft_id = self.to_text(feature, "id")
                ft_type = self.to_text(feature, "type")
                contig_id = ""
                ft_strand = ""
                ft_start = ""
                ft_length = ""
                if "location" in feature:
                    locations = feature["location"]
                    if len(locations)>0:
                        contig_id = locations[0][0]
                        ft_strand = locations[0][2]
                        ft_start = None
                        ft_length = None
                        if len(locations) == 1:
                            ft_start = str(locations[0][1])
                            ft_length = str(locations[0][3])
                        else:
                            ft_fwd = ft_strand == '+'
                            ft_min = None
                            ft_max = None
                            loc_to_save = []
                            for loc in locations:
                                if loc[0] == contig_id and loc[2] == ft_strand:
                                    loc_min = loc[1] if ft_fwd else (loc[1] - loc[3] + 1)
                                    loc_max = loc[1] if not ft_fwd else (loc[1] + loc[3] - 1)
                                    if ft_min is None or ft_min > loc_min:
                                        ft_min = loc_min
                                    if ft_max is None or ft_max < loc_max:
                                        ft_max = loc_max
                                    loc_to_save.append([loc[1], loc[3]])
                                else:
                                    loc_to_save.append(loc)
                            ft_start = str(ft_min if ft_fwd else ft_max)
                            ft_length = str(ft_max + 1 - ft_min)
                            obj["l"] = loc_to_save
                obj_json = json.dumps(obj)
                ft_aliases = self.to_text(feature, "aliases")
                ft_function = self.to_text(feature, "function").replace("\t", " ")
                if 'functions' in feature:
                    ft_function = self.to_text(feature, "functions"
                                               ).replace("\t", " ")
                ontology_terms = []
                if "ontology_terms" in feature:
                    for ont_type in feature["ontology_terms"]:
                        ont_map = feature["ontology_terms"][ont_type]
                        for term_id in ont_map:
                            # new genome type
                            if 'ontologies_present' in genome:
                                term_name = genome['ontologies_present'].get(
                                    ont_type, {}).get(term_id, "")
                            else:
                                term_name = ont_map[term_id].get("term_name", "")
                            ontology_terms.append(term_id.replace(",", self.unicode_comma))
                            ontology_terms.append(term_name.replace(",", self.unicode_comma))
                ft_ontology = ",".join(x for x in ontology_terms if x)
                line = u"\t".join(x for x in 
                                  [obj_json, ft_id, ft_type, contig_id,
                                   ft_start, ft_strand, ft_length, ft_aliases, 
                                   ft_function, ft_ontology]) + u"\n"
                outfile.write(line.encode("utf-8"))
        subprocess.Popen(["gzip", outfile.name],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        os.rename(outfile.name + ".gz", os.path.join(self.genome_index_dir, 
                                                     inner_chsum + "_ftr.tsv.gz"))

    def check_feature_cache(self, ref, token):
        ws_client = workspaceService(self.ws_url, token=token)
        info = ws_client.get_object_info_new({"objects": [{"ref": ref}]})[0]
        inner_chsum = info[8]
        index_file = os.path.join(self.genome_index_dir, inner_chsum + "_ftr.tsv.gz")
        if not os.path.isfile(index_file):
            if self.debug:
                print("    Loading WS object...")
            t1 = time.time()
            incl = [x+y for x, y in product(
                ['features/[*]/', 'cdss/[*]/', 'mrnas/[*]/',
                 'non_coding_features/[*]/'],
                ["id", "type", "function", "functions", "aliases", "location",
                 "ontology_terms"])] + ['ontologies_present']
            genome = ws_client.get_objects2({"objects": [{"ref": ref,
                                                          "included": incl}]
                                             })["data"][0]["data"]
            self.save_feature_tsv(genome, inner_chsum)
            if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return inner_chsum

    def get_column_props(self, column_props_map, col_name):
        if col_name not in column_props_map:
            raise ValueError("Unknown column name '" + col_name + "', " +
                             "please use one of " + str(column_props_map.keys()))
        return column_props_map[col_name]

    def get_sorting_code(self, column_props_map, sort_by):
        ret = ""
        if sort_by is None or len(sort_by) == 0:
            return ret
        for column_sorting in sort_by:
            col_name = column_sorting[0]
            col_props = self.get_column_props(column_props_map, col_name)
            col_pos = str(col_props["col"])
            ascending_order = column_sorting[1]
            ret += col_pos + ('a' if ascending_order else 'd')
        return ret

    def get_feature_sorted_iterator(self, inner_chsum, sort_by):
        return self.get_sorted_iterator(inner_chsum, sort_by, "ftr", 
                                        self.feature_column_props_map)

    def get_sorted_iterator(self, inner_chsum, sort_by, item_type, 
                            column_props_map):
        input_file = os.path.join(self.genome_index_dir, inner_chsum + "_" + 
                                  item_type + ".tsv.gz")
        if not os.path.isfile(input_file):
            raise ValueError("File not found: " + input_file)
        if sort_by is None or len(sort_by) == 0:
            return CombinedLineIterator(input_file)
        cmd = "gunzip -c \"" + input_file + "\" | sort -f -t\\\t"
        for column_sorting in sort_by:
            col_name = column_sorting[0]
            col_props = self.get_column_props(column_props_map, col_name)
            col_pos = str(col_props["col"])
            ascending_order = column_sorting[1]
            sort_arg = "-k" + col_pos + "," + col_pos + col_props["type"]
            if not ascending_order:
                sort_arg += "r"
            cmd += " " + sort_arg
        fname = (inner_chsum + "_" + item_type + "_" +
                 self.get_sorting_code(column_props_map, sort_by))
        final_output_file = os.path.join(self.genome_index_dir, fname + ".tsv.gz")
        if not os.path.isfile(final_output_file):
            if self.debug:
                print("    Sorting...")
            t1 = time.time()
            need_to_save = os.path.getsize(input_file) > self.max_sort_mem_size
            if need_to_save:
                outfile = tempfile.NamedTemporaryFile(dir = self.genome_index_dir,
                        prefix = fname + "_", suffix = ".tsv.gz", delete=False)
                outfile.close()
                output_file = outfile.name
                cmd += " | gzip -c > \"" + output_file + "\""
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
            if not need_to_save:
                if self.debug:
                    print("    (time=" + str(time.time() - t1) + ")")
                return CombinedLineIterator(p)
            else:
                p.wait()
                os.rename(output_file, final_output_file)
                if self.debug:
                    print("    (time=" + str(time.time() - t1) + ")")
        return CombinedLineIterator(final_output_file)

    def filter_feature_query(self, index_iter, query, structured_query, start, limit, num_found):
        query_words = str(query).lower().translate(
                string.maketrans("\r\n\t,", "    ")).split()
        if self.debug:
                print("    Filtering...")
        t1 = time.time()
        fcount = 0
        features = []
        with index_iter:
            for line in index_iter:
                line2 = line[line.index('\t') + 1:]
                if self._eval_line(line2, query_words, structured_query):
                    if start <= fcount < start + limit:
                        features.append(self.unpack_feature(line.rstrip('\n')))
                    fcount += 1
                    if num_found is not None and fcount >= start + limit:
                        # Having shortcut when real num_found was already known
                        fcount = num_found
                        break
        if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return {"num_found": fcount, "start": start, "features": features,
                "query": query}

    def _eval_line(self, line, all_query, structured_query=None):
        if not all(word in line.lower() for word in all_query):
            return False
        if structured_query:
            return _eval_structured_query(line.split('\t'), structured_query,
                                          self.feature_column_props_map)
        return True

    def unpack_feature(self, line, items = None):
        try:
            if items is None:
                items = line.split('\t')
            contig_id = items[3]
            strand = items[5]
            gloc = {}
            if contig_id and strand and items[4] and items[6]:
                gloc = {"contig_id": contig_id, "start": int(items[4]),
                        "strand": strand, "length": int(items[6])}
            obj = json.loads(items[0])
            location = []
            if "l" in obj:
                for loc in obj["l"]:
                    if len(loc) == 4:
                        location.append({"contig_id": loc[0], "start": loc[1],
                                         "strand": loc[2], "length": loc[3]})
                    else:
                        location.append({"contig_id": contig_id, "start": loc[0],
                                         "strand": strand, "length": loc[1]})
            else:
                location.append(gloc)
            aliases = {}
            for alias in items[7].split(','):
                if alias:
                    aliases[alias] = []
            ontology_terms = {}
            ontology_iter = iter(items[9].split(','))
            while True:
                try:
                    term_id = next(ontology_iter).replace(self.unicode_comma, ",")
                    term_name = next(ontology_iter).replace(self.unicode_comma, ",")
                    ontology_terms[term_id] = term_name
                except StopIteration:
                    break
            return {"location": location, "feature_id": items[1],
                    "feature_type": items[2], "global_location": gloc,
                    "aliases": aliases, "function": items[8], 
                    "feature_idx": obj["p"], "feature_array": obj['arr'],
                    "ontology_terms": ontology_terms}
        except:
            raise ValueError("Error parsing feature from: [" + line + "]\n" +
                             "Cause: " + traceback.format_exc())

    def search_region(self, token, ref, query_contig_id, query_region_start,
                      query_region_length, page_start, page_limit, num_found):
        if query_contig_id is None:
            raise ValueError("Parameter 'query_contig_id' should be set");
        if query_region_start is None:
            raise ValueError("Parameter 'query_region_start' should be set");
        if query_region_length is None:
            raise ValueError("Parameter 'query_region_length' should be set");
        if page_start is None:
            page_start = 0
        if page_limit is None:
            page_limit = 50
        if self.debug:
            print("Search region: genome=" + ref + ", query=[" +
                  query_contig_id + ":" + str(query_region_start) + "+" + 
                  str(query_region_length) + "], page_start=" + 
                  str(page_start) + ", page_limit=" + str(page_limit))
        t1 = time.time()
        inner_chsum = self.check_feature_cache(ref, token)
        sort_by = [["contig_id", True], ["start", True]]
        index_iter = self.get_feature_sorted_iterator(inner_chsum, sort_by)
        ret = self.filter_query_region(index_iter, query_contig_id,
                                       query_region_start, query_region_length,
                                       page_start, page_limit, num_found)
        contig = self.get_contig(token, ref, query_contig_id)
        ret["contig_length"] = None if not contig else contig["length"]
        if self.debug:
            print("    (overall-time=" + str(time.time() - t1) + ")")
        return ret

    def filter_query_region(self, index_iter, query_contig_id, query_region_start,
                            query_region_length, page_start, page_limit, num_found):
        if self.debug:
                print("    Filtering region...")
        query = self.get_region(query_region_start, "+", query_region_length)
        t1 = time.time()
        fcount = 0
        features = []
        with index_iter:
            for line in index_iter:
                items = line.rstrip('\n').split('\t')
                contig_id = items[3]
                start = items[4]
                strand = items[5]
                length = items[6]
                if contig_id and strand and start and length:
                    if contig_id == query_contig_id and self.intersect(query,
                            self.get_region(int(start), strand, int(length))):
                        if fcount >= page_start and fcount < page_start + page_limit:
                            features.append(self.unpack_feature(line.rstrip('\n')))
                        fcount += 1
                        if num_found is not None and fcount >= page_start + page_limit:
                            # Having shortcut when real num_found was already known
                            fcount = num_found
                            break
        if self.debug:
            print("    (time=" + str(time.time() - t1) + ")")
        return {"num_found": fcount, "page_start": page_start, 
                "features": features, "query_contig_id": query_contig_id, 
                "query_region_start": query_region_start, 
                "query_region_length": query_region_length}

    def intersect(self, region1, region2):
        return max(region1[0], region2[0]) <= min(region1[1], region2[1])

    def get_region(self, start, strand, length):
        fwd = strand == '+'
        loc_min = start if fwd else (start - length + 1)
        loc_max = start if not fwd else (start + length - 1)
        return [loc_min, loc_max]

    def search_contigs(self, token, ref, query, sort_by, start, limit, num_found):
        if query is None:
            query = ""
        if start is None:
            start = 0
        if limit is None:
            limit = 50
        if self.debug:
            print("Search contigs: genome=" + ref + ", query=[" + query + "], " +
                  "sort-by=[" + self.get_sorting_code(self.contig_column_props_map, 
                  sort_by) + "], start=" + str(start) + ", limit=" + str(limit))
        t1 = time.time()
        inner_chsum = self.check_contig_cache(ref, token)
        index_iter = self.get_contig_sorted_iterator(inner_chsum, sort_by)
        ret = self.filter_contig_query(index_iter, query, start, limit, num_found)
        if self.debug:
            print("    (overall-time=" + str(time.time() - t1) + ")")
        return ret

    def check_contig_cache(self, gref, token):
        ws_client = workspaceService(self.ws_url, token=token)
        info = ws_client.get_object_info_new({"objects": [{"ref": gref}]})[0]
        inner_chsum = info[8]
        index_file = os.path.join(self.genome_index_dir, inner_chsum + "_ctg.tsv.gz")
        if not os.path.isfile(index_file):
            t1 = time.time()
            genome = ws_client.get_objects2({"objects": [{"ref": gref, "included":
                    ["/contigset_ref", "/assembly_ref"]}]})["data"][0]["data"]
            ctg_ref = None
            ctg_incl = None
            if "contigset_ref" in genome:
                if self.debug:
                    print("    Loading contigs from ContigSet...")
                ctg_ref = genome["contigset_ref"]
                ctg_incl = ["/contigs/[*]/id", "/contigs/[*]/length"]
            elif "assembly_ref" in genome:
                if self.debug:
                    print("    Loading contigs from Assembly...")
                ctg_ref = genome["assembly_ref"]
                ctg_incl = ["/contigs/*/length"]
            # We allow now Genome objects without contigs. Just skip errors.
            contigs = {}
            if ctg_ref:
                assembly = ws_client.get_objects2({"objects": [{"included": ctg_incl,
                        "ref": gref, "obj_ref_path": [ctg_ref]}]})["data"][0]["data"]
                if "contigset_ref" in genome:
                    for ctg in assembly["contigs"]:
                        contigs[ctg["id"]] = [ctg["length"], 0]
                else:
                    for ctg_id in assembly["contigs"]:
                        contigs[ctg_id] = [assembly["contigs"][ctg_id]["length"], 0]
                if self.debug:
                    print("    (time=" + str(time.time() - t1) + ")")
            inner_chsum = self.check_feature_cache(gref, token)
            # Reading features without sorting and grouping by contig_id
            index_iter = self.get_feature_sorted_iterator(inner_chsum, None)
            if self.debug:
                print("    Grouping features...")
            t1 = time.time()
            with index_iter:
                for line in index_iter:
                    items = line.rstrip('\n').split('\t')
                    contig_id = items[3]
                    if not contig_id:
                        continue
                    values = None
                    if contig_id in contigs:
                        values = contigs[contig_id]
                    else:
                        raise ValueError("Contig id=" + contig_id + " is not found")
                    values[1] += 1
            self.save_contig_tsv(contigs, inner_chsum)
            if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return inner_chsum

    def save_contig_tsv(self, contigs, inner_chsum):
        # contigs is a map having structure like: 
        # {<contig-id>: [<length>, <feature-count>]}
        outfile = tempfile.NamedTemporaryFile(dir = self.genome_index_dir,
                prefix = inner_chsum + "_ctg_", suffix = ".tsv", delete=False)
        with outfile:
            for contig_id in contigs:
                values = contigs[contig_id]
                outfile.write("\t".join(x for x in [contig_id, str(values[0]),
                                                    str(values[1])]) + "\n")
        subprocess.Popen(["gzip", outfile.name],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        os.rename(outfile.name + ".gz", os.path.join(self.genome_index_dir, 
                                                     inner_chsum + "_ctg.tsv.gz"))

    def get_contig_sorted_iterator(self, inner_chsum, sort_by):
        return self.get_sorted_iterator(inner_chsum, sort_by, "ctg", 
                                        self.contig_column_props_map)

    def filter_contig_query(self, index_iter, query, start, limit, num_found):
        query_words = str(query).lower().translate(
                string.maketrans("\r\n\t,", "    ")).split()
        if self.debug:
                print("    Filtering...")
        t1 = time.time()
        fcount = 0
        contigs = []
        with index_iter:
            for line in index_iter:
                if all(word in line.lower() for word in query_words):
                    if fcount >= start and fcount < start + limit:
                        contigs.append(self.unpack_contig(line.rstrip('\n')))
                    fcount += 1
                    if num_found is not None and fcount >= start + limit:
                        # Having shortcut when real num_found was already known
                        fcount = num_found
                        break
        if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return {"num_found": fcount, "start": start, "contigs": contigs,
                "query": query}

    def unpack_contig(self, line, items = None):
        try:
            if items is None:
                items = line.split('\t')
            contig_id = items[0]
            length = int(items[1])
            feature_count = int(items[2])
            return {"contig_id": contig_id, "length": length, 
                    "feature_count": feature_count}
        except:
            raise ValueError("Error parsing feature from: [" + line + "]\n" +
                             "Cause: " + traceback.format_exc())

    def get_contig(self, token, ref, contig_id):
        t1 = time.time()
        inner_chsum = self.check_contig_cache(ref, token)
        ret = None
        with self.get_contig_sorted_iterator(inner_chsum, None) as index_iter:
            if self.debug:
                print("    Looking for contig id=" + contig_id + ", genome=" + ref)
            for line in index_iter:
                contig = self.unpack_contig(line.rstrip('\n'))
                if contig["contig_id"] == contig_id:
                    ret = contig
                    break
        if self.debug:
            print("    (time=" + str(time.time() - t1) + ")")
        return ret
