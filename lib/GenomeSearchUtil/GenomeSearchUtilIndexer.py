# -*- coding: utf-8 -*-
import os
import json
import time
import subprocess
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
        self.ws_url = config['workspace-url']
        self.genome_index_dir = config['genome-index-dir']
        if not os.path.isdir(self.genome_index_dir):
            os.makedirs(self.genome_index_dir)
    
    def search(self, token, ref, query, sort_by, start, limit):
        # TODO: to try to switch to gzipped version of TSV 
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

    def save_tsv(self, features, target_file_path):
        with open(target_file_path, 'w') as outfile:
            pos = 0
            for feature in features:
                locations = feature["location"]
                obj = {"p": pos}
                if len(locations) > 1:
                    obj["l"] = locations
                pos += 1
                obj_json = json.dumps(obj)  # TODO: it needs to be packed better
                location = locations[0]  # TODO: switch to min/max of gene positions
                ft_id = self.to_text(feature, "id")
                ft_type = self.to_text(feature, "type")
                contig_id = location[0]
                ft_start = str(location[1])
                ft_strand = location[2]
                ft_length = str(location[3])
                ft_aliases = self.to_text(feature, "aliases")
                ft_function = self.to_text(feature, "function").replace("\t", " ")
                outfile.write("\t".join(x for x in 
                                        [obj_json, ft_id, ft_type, contig_id,
                                         ft_start, ft_strand, ft_length, ft_aliases, 
                                         ft_function]) + "\n")

    def check_cache(self, ref, token):
        ws_client = workspaceService(self.ws_url, token=token)
        info = ws_client.get_object_info_new({"objects": [{"ref": ref}]})[0]
        inner_ref = str(info[6]) + "_" + str(info[0]) + "_" + str(info[4])
        index_file = os.path.join(self.genome_index_dir, inner_ref + ".tsv")
        if not os.path.isfile(index_file):
            print("    Loading WS object...")
            t1 = time.time()
            genome = ws_client.get_object_subset([{"ref": ref, "included": [
                    "/features/[*]/id", "/features/[*]/type", 
                    "/features/[*]/function", "/features/[*]/aliases", 
                    "/features/[*]/location"]}])[0]["data"]
            self.save_tsv(genome["features"], index_file)
            print("    (time=" + str(time.time() - t1) + ")")
        return inner_ref

    def get_sorted_file_path(self, inner_ref, sort_by):
        input_file = os.path.join(self.genome_index_dir, inner_ref + ".tsv")
        if not os.path.isfile(input_file):
            raise ValueError("File not found: " + input_file)
        if len(sort_by) == 0:
            return input_file
        sorting_suffix = ""
        cmd = ["sort"]
        for column_sorting in sort_by:
            col_name = column_sorting[0]
            col_props = self.column_props_map[col_name]
            col_pos = str(col_props["col"])
            ascending_order = column_sorting[1]
            sorting_suffix += col_pos + ('a' if ascending_order else 'd')
            sort_arg = "-k" + col_pos + "," + col_pos + col_props["type"]
            if not ascending_order:
                sort_arg += "r"
            cmd.append(sort_arg)
        output_file = os.path.join(self.genome_index_dir, inner_ref + "_" + 
                                   sorting_suffix + ".tsv")
        if not os.path.isfile(output_file):
            print("    Sorting...")
            t1 = time.time()
            cmd.extend(["-o", output_file, input_file])
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            retval = p.wait()
            # TODO: check retval and throw an error including p.stdout and p.stderr
            print("    (time=" + str(time.time() - t1) + ")")
        return output_file

    def filter_query(self, index_file, query, start, limit):
        print("    Filtering...")
        t1 = time.time()
        if not start:
            start = 0;
        fcount = 0
        features = []
        # TODO: support skipping to start and use limit for features
        with open(index_file) as infile:
            for line in infile:
                line2 = line[line.index('\t') + 1:]
                if query in line2.lower():
                    items = line.rstrip().split('\t')
                    fcount += 1
                    # TODO: features should be unpacked properly
                    features.append({"feature_id": items[1], "function": items[8],
                            "feature_type": items[2], "aliases": items[7].split(','),
                            "location": [{"contig_id": items[3], "start": int(items[4]),
                                          "strand": items[5], "length": int(items[6])}]})
        print("    (time=" + str(time.time() - t1) + ")")
        return {"num_found": fcount, "start": start, "features": features}
