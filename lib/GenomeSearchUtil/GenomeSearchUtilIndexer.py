# -*- coding: utf-8 -*-
import os
import json
import time
import subprocess
import gzip
import io
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
        self.debug = "debug" in config and config["debug"] == "1"
    
    def search(self, token, ref, query, sort_by, start, limit):
        inner_ref = self.check_cache(ref, token)
        index_file = self.get_sorted_file_path(inner_ref, sort_by)
        return self.filter_query(index_file, query, start, limit)

    def to_text(self, mapping, key):
        if key not in mapping or mapping[key] is None:
            return ""
        value = mapping[key]
        if type(value) is list:
            return ",".join(str(x) for x in value if x)
        return str(value)

    def save_tsv(self, features, inner_ref):
        target_file_path = os.path.join(self.genome_index_dir, inner_ref + ".tsv")
        with open(target_file_path, 'w') as outfile:
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
        subprocess.Popen(["gzip", target_file_path], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

    def check_cache(self, ref, token):
        ws_client = workspaceService(self.ws_url, token=token)
        info = ws_client.get_object_info_new({"objects": [{"ref": ref}]})[0]
        inner_ref = str(info[6]) + "_" + str(info[0]) + "_" + str(info[4])
        index_file = os.path.join(self.genome_index_dir, inner_ref + ".tsv.gz")
        if not os.path.isfile(index_file):
            if self.debug:
                print("    Loading WS object...")
            t1 = time.time()
            genome = ws_client.get_object_subset([{"ref": ref, "included": [
                    "/features/[*]/id", "/features/[*]/type", 
                    "/features/[*]/function", "/features/[*]/aliases", 
                    "/features/[*]/location"]}])[0]["data"]
            self.save_tsv(genome["features"], inner_ref)
            if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return inner_ref

    def get_sorted_file_path(self, inner_ref, sort_by):
        input_file = os.path.join(self.genome_index_dir, inner_ref + ".tsv.gz")
        if not os.path.isfile(input_file):
            raise ValueError("File not found: " + input_file)
        if len(sort_by) == 0:
            return input_file
        sorting_suffix = ""
        cmd = "gunzip -c \"" + input_file + "\" | sort -t\\\t"
        for column_sorting in sort_by:
            col_name = column_sorting[0]
            col_props = self.column_props_map[col_name]
            col_pos = str(col_props["col"])
            ascending_order = column_sorting[1]
            sorting_suffix += col_pos + ('a' if ascending_order else 'd')
            sort_arg = "-k" + col_pos + "," + col_pos + col_props["type"]
            if not ascending_order:
                sort_arg += "r"
            cmd += " " + sort_arg
        output_file = os.path.join(self.genome_index_dir, inner_ref + "_" + 
                                   sorting_suffix + ".tsv.gz")
        if not os.path.isfile(output_file):
            if self.debug:
                print("    Sorting...")
            t1 = time.time()
            cmd += " | gzip -c > \"" + output_file + "\""
            subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE).wait()
            if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return output_file

    def filter_query(self, index_file, query, start, limit):
        if self.debug:
                print("    Filtering...")
        t1 = time.time()
        if start is None:
            start = 0
        if limit is None:
            limit = 50
        fcount = 0
        features = []
        with io.TextIOWrapper(io.BufferedReader(gzip.open(index_file))) as infile:
            for line in infile:
                line2 = line[line.index('\t') + 1:]
                if query in line2.lower():
                    if fcount >= start and fcount < start + limit:
                        items = line.rstrip().split('\t')
                        contig_id = items[3]
                        strand = items[5]
                        gloc = {"contig_id": contig_id, "start": int(items[4]),
                                      "strand": strand, "length": int(items[6])}
                        obj = json.loads(items[0])
                        location = []
                        if "l" in obj:
                            for loc in obj["l"]:
                                if len(loc) == 4:
                                    location.append(loc)
                                else:
                                    location.append([contig_id, loc[0], strand, loc[1]])
                        else:
                            location.append(gloc)
                        features.append({"location": location, "feature_id": items[1],
                                "feature_type": items[2], "global_location": gloc,
                                "aliases": items[7].split(','), "function": items[8]})
                    fcount += 1
        if self.debug:
                print("    (time=" + str(time.time() - t1) + ")")
        return {"num_found": fcount, "start": start, "features": features}
