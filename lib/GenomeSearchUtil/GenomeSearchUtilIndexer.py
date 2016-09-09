# -*- coding: utf-8 -*-
import os
import json
import time
import subprocess
import gzip
import io
import traceback
import string
import tempfile
from biokbase.workspace.client import Workspace as workspaceService

class GenomeSearchUtilIndexer:

    def __init__(self, config):
        self.column_props_map = {
            "feature_id": {"col": 2, "type": ""}, 
            "feature_type": {"col": 3, "type": ""}, 
            "contig_id": {"col": 4, "type": ""}, 
            "start": {"col": 5, "type": "n"}, 
            "strand": {"col": 6, "type": ""}, 
            "length": {"col": 7, "type": "n"}, 
            "function": {"col": 9, "type": ""}
        }
        self.ws_url = config["workspace-url"]
        self.genome_index_dir = config["genome-index-dir"]
        if not os.path.isdir(self.genome_index_dir):
            os.makedirs(self.genome_index_dir)
        self.debug = True  #"debug" in config and config["debug"] == "1"
    
    def search(self, token, ref, query, sort_by, start, limit, num_found):
        if query is None:
            query = ""
        if start is None:
            start = 0
        if limit is None:
            limit = 50
        if self.debug:
            print("Search: genome=" + ref + ", query=[" +
                  query + "], sort-by=[" + self.get_sorting_code(sort_by) +
                  "], start=" + str(start) + ", limit=" + str(limit))
        t1 = time.time()
        inner_chsum = self.check_cache(ref, token)
        index_file = self.get_sorted_file_path(inner_chsum, sort_by)
        ret = self.filter_query(index_file, query, start, limit, num_found)
        if self.debug:
            print("    (overall-time=" + str(time.time() - t1) + ")")
        return ret

    def to_text(self, mapping, key):
        if key not in mapping or mapping[key] is None:
            return ""
        value = mapping[key]
        if type(value) is list:
            return ",".join(str(x) for x in value if x)
        return str(value)

    def save_tsv(self, features, inner_chsum):
        #target_file_path = os.path.join(self.genome_index_dir, inner_chsum + ".tsv")
        outfile = tempfile.NamedTemporaryFile(dir = self.genome_index_dir,
                prefix = inner_chsum + "_", suffix = ".tsv", delete=False)
        with outfile:
            pos = 0
            for feature in features:
                locations = feature["location"]
                obj = {"p": pos}
                pos += 1
                ft_id = self.to_text(feature, "id")
                ft_type = self.to_text(feature, "type")
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
                outfile.write("\t".join(x for x in 
                                        [obj_json, ft_id, ft_type, contig_id,
                                         ft_start, ft_strand, ft_length, ft_aliases, 
                                         ft_function]) + "\n")
        subprocess.Popen(["gzip", outfile.name],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        os.rename(outfile.name + ".gz", os.path.join(self.genome_index_dir, 
                                                     inner_chsum + ".tsv.gz"))

    def check_cache(self, ref, token):
        ws_client = workspaceService(self.ws_url, token=token)
        info = ws_client.get_object_info_new({"objects": [{"ref": ref}]})[0]
        inner_chsum = info[8]
        index_file = os.path.join(self.genome_index_dir, inner_chsum + ".tsv.gz")
        if not os.path.isfile(index_file):
            if self.debug:
                print("    Loading WS object...")
            t1 = time.time()
            genome = ws_client.get_object_subset([{"ref": ref, "included": [
                    "/features/[*]/id", "/features/[*]/type", 
                    "/features/[*]/function", "/features/[*]/aliases", 
                    "/features/[*]/location"]}])[0]["data"]
            self.save_tsv(genome["features"], inner_chsum)
            if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return inner_chsum

    def get_column_props(self, col_name):
        if col_name not in self.column_props_map:
            raise ValueError("Unknown column name '" + col_name + "', " +
                    "please use one of " + str(self.column_props_map.keys()))
        return self.column_props_map[col_name]

    def get_sorting_code(self, sort_by):
        ret = ""
        if sort_by is None or len(sort_by) == 0:
            return ret
        for column_sorting in sort_by:
            col_name = column_sorting[0]
            col_props = self.get_column_props(col_name)
            col_pos = str(col_props["col"])
            ascending_order = column_sorting[1]
            ret += col_pos + ('a' if ascending_order else 'd')
        return ret

    def get_sorted_file_path(self, inner_chsum, sort_by):
        input_file = os.path.join(self.genome_index_dir, inner_chsum + ".tsv.gz")
        if not os.path.isfile(input_file):
            raise ValueError("File not found: " + input_file)
        if sort_by is None or len(sort_by) == 0:
            return input_file
        cmd = "gunzip -c \"" + input_file + "\" | sort -f -t\\\t"
        for column_sorting in sort_by:
            col_name = column_sorting[0]
            col_props = self.get_column_props(col_name)
            col_pos = str(col_props["col"])
            ascending_order = column_sorting[1]
            sort_arg = "-k" + col_pos + "," + col_pos + col_props["type"]
            if not ascending_order:
                sort_arg += "r"
            cmd += " " + sort_arg
        fname = inner_chsum + "_" + self.get_sorting_code(sort_by)
        final_output_file = os.path.join(self.genome_index_dir, fname + ".tsv.gz")
        if not os.path.isfile(final_output_file):
            outfile = tempfile.NamedTemporaryFile(dir = self.genome_index_dir,
                    prefix = fname + "_", suffix = ".tsv.gz", delete=False)
            outfile.close()
            output_file = outfile.name
            if self.debug:
                print("    Sorting...")
            t1 = time.time()
            cmd += " | gzip -c > \"" + output_file + "\""
            subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE).wait()
            os.rename(output_file, final_output_file)
            if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return final_output_file

    def filter_query(self, index_file, query, start, limit, num_found):
        query_words = str(query).lower().translate(
                string.maketrans("\r\n\t,", "    ")).split()
        if self.debug:
                print("    Filtering...")
        t1 = time.time()
        fcount = 0
        features = []
        with io.TextIOWrapper(io.BufferedReader(gzip.open(index_file))) as infile:
            for line in infile:
                line2 = line[line.index('\t') + 1:]
                if all(word in line2.lower() for word in query_words):
                    if fcount >= start and fcount < start + limit:
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

    def unpack_feature(self, line, items = None):
        try:
            if items is None:
                items = line.split('\t')
            contig_id = items[3]
            strand = items[5]
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
            return {"location": location, "feature_id": items[1],
                    "feature_type": items[2], "global_location": gloc,
                    "aliases": aliases, "function": items[8], 
                    "feature_idx": obj["p"]}
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
        inner_chsum = self.check_cache(ref, token)
        sort_by = [["contig_id", True], ["start", True]]
        index_file = self.get_sorted_file_path(inner_chsum, sort_by)
        ret = self.filter_query_region(index_file, query_contig_id,
                                       query_region_start, query_region_length,
                                       page_start, page_limit, num_found)
        if self.debug:
            print("    (overall-time=" + str(time.time() - t1) + ")")
        return ret

    def filter_query_region(self, index_file, query_contig_id, query_region_start,
                            query_region_length, page_start, page_limit, num_found):
        if self.debug:
                print("    Filtering region...")
        query = self.get_region(query_region_start, "+", query_region_length)
        t1 = time.time()
        fcount = 0
        features = []
        with io.TextIOWrapper(io.BufferedReader(gzip.open(index_file))) as infile:
            for line in infile:
                items = line.rstrip('\n').split('\t')
                if items[3] == query_contig_id and self.intersect(query,
                        self.get_region(int(items[4]), items[5], int(items[6]))):
                    if fcount >= page_start and fcount < page_start + page_limit:
                        features.append(self.unpack_feature(line.rstrip('\n')))
                    fcount += 1
                    if num_found is not None and fcount >= page_start + page_limit:
                        # Having shortcut when real num_found was already known
                        fcount = num_found
                        break
        if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return {"num_found": fcount, "page_start": page_start, "features": features,
                "query_contig_id": query_contig_id, 
                "query_region_start": query_region_start, 
                "query_region_length": query_region_length}

    def intersect(self, region1, region2):
        return max(region1[0], region2[0]) <= min(region1[1], region2[1])

    def get_region(self, start, strand, length):
        fwd = strand == '+'
        loc_min = start if fwd else (start - length + 1)
        loc_max = start if not fwd else (start + length - 1)
        return [loc_min, loc_max]