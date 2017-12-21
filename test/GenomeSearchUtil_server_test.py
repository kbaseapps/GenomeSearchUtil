# -*- coding: utf-8 -*-
import unittest
import os
import json
import time
import requests
import subprocess

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint
import shutil
import os

from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from biokbase.workspace.client import Workspace as workspaceService
from GenomeSearchUtil.GenomeSearchUtilImpl import GenomeSearchUtil
from GenomeSearchUtil.GenomeSearchUtilServer import MethodContext
from GenomeSearchUtil.authclient import KBaseAuth as _KBaseAuth


class GenomeSearchUtilTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('GenomeSearchUtil'):
            cls.cfg[nameval[0]] = nameval[1]
        authServiceUrl = cls.cfg.get('auth-service-url',
                "https://kbase.us/services/authorization/Sessions/Login")
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'GenomeSearchUtil',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.cfg['genome-index-dir'] = cls.cfg['scratch']
        cls.cfg['debug'] = "1"
        cls.scratch = cls.cfg['scratch']
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = GenomeSearchUtil(cls.cfg)
        suffix = int(time.time() * 1000)
        cls.wsName = "test_SaveGenomeTest_" + str(suffix)
        cls.wsClient.create_workspace({'workspace': cls.wsName})
        cls.banno_ref = cls.load_genome_direct(
            'data/b.anno.2.genome.json', 'b.anno.2',
            contigset_filename='data/b.anno.2.contigs.json')
        cls.rhodo_ref = cls.load_genome_direct(
            'data/rhodobacter.json', 'rhodobacter',
            contigset_filename='data/rhodobacter_contigs.json')
        cls.eco_ref = cls.load_genome_direct(
            'data/new_ecoli_genome.json', 'ecoli',
            'data/e_coli_assembly.fasta', gtype="NewTempGenomes.Genome")

    @classmethod
    def load_genome_direct(cls, filename, obj_name, assembly_filename=None,
                           contigset_filename=None,
                           gtype='KBaseGenomes.Genome'):
        data = json.load(open(filename, 'r'))

        if assembly_filename:
            au = AssemblyUtil(os.environ['SDK_CALLBACK_URL'])
            assembly_file_path = os.path.join(cls.scratch,
                                              os.path.basename(
                                                  assembly_filename))
            shutil.copy(assembly_filename, assembly_file_path)
            assembly_ref = au.save_assembly_from_fasta({
                'workspace_name': cls.wsName,
                'assembly_name': obj_name + '.assembly',
                'file': {'path': assembly_file_path}
            })
            pprint('created test assembly: ' + assembly_ref)
            data['assembly_ref'] = assembly_ref

        if contigset_filename:
            contig_data = json.load(open(contigset_filename))
            info = cls.wsClient.save_objects({
                'workspace': cls.wsName, 'objects': [
                    {
                        'type': "KBaseGenomes.ContigSet",
                        'name': obj_name + ".contigs",
                        'data': contig_data}
                ]})[0]
            contig_ref = str(info[6]) + '/' + str(info[0]) + '/' + str(info[4])
            data['contigset_ref'] = contig_ref

        # save to ws
        save_info = {
            'workspace': cls.wsName,
            'objects': [{
                'type': gtype,
                'data': data,
                'name': obj_name + '.genome'
            }]
        }
        result = cls.wsClient.save_objects(save_info)
        info = result[0]
        ref = str(info[6]) + '/' + str(info[0]) + '/' + str(info[4])
        print('created test genome: ' + ref + ' from file ' + filename)
        return ref

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        return self.__class__.wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def check_genome(self, ref):
        query = "dehydrogenase"
        data = self.getWsClient().get_object_subset([{"ref": ref, "included": [
                "/scientific_name"]}])[0]
        genome_name = data["data"]["scientific_name"]
        print("\nGenome " + genome_name + ":")
        ret = self.getImpl().search(self.getContext(), {"ref": ref, "query": query,
                "sort_by": [["feature_id", True]]})[0]
        self.assertTrue("num_found" in ret)
        print("And with loading skipped:")
        ret = self.getImpl().search(self.getContext(), {"ref": ref, "query": query,
                "sort_by": [["feature_type", False], ["contig_id", True], ["start", False]]})[0]
        print("And with both loading and sorting skipped:")
        ret = self.getImpl().search(self.getContext(), {"ref": ref, "query": query,
                "sort_by": [["feature_type", False], ["contig_id", True], ["start", False]],
                "num_found": ret["num_found"]})[0]
        print("Features found for query [" + query + "]: " + str(ret["num_found"]))

    def test_custom_genome_features(self):
        ret = self.getImpl().search(self.getContext(),
                                    {"ref": self.banno_ref,
                                     "query": "",
                                     "sort_by": [["feature_id", True]]})[0]
        self.assertEqual(ret["num_found"], 5017)
        self.check_genome(self.banno_ref)

    def test_custom_genome_contigs(self):
        ret = self.getImpl().search_contigs(self.getContext(),
                                            {"ref": self.banno_ref,
                                             "query": "",
                                             "sort_by": [["length", False]]}
                                            )[0]
        self.assertTrue("num_found" in ret)
        self.assertEqual(ret["num_found"], 102)
        ret = self.getImpl().search_contigs(self.getContext(),
                                            {"ref": self.banno_ref,
                                             "query": "kb|g.240002.c.45",
                                             "sort_by": [["length", False]]}
                                            )[0]
        self.assertTrue("num_found" in ret)
        self.assertEqual(ret["num_found"], 1)


    def test_custom_genome_ontologies(self):
        ret = self.getImpl().search(self.getContext(),
                                    {"ref": self.banno_ref,
                                     "query": "SSO:000009137",
                                     "limit": 1})[0]
        self.assertEqual(ret["num_found"], 486)
        self.assertEqual(len(ret["features"]), 1)
        self.assertTrue("hypothetical protein" in ret["features"][0]
            ["ontology_terms"]["SSO:000009137"])

    def test_rhodobacter_genome_features(self):
        ret = self.getImpl().search(self.getContext(),
                                    {"ref": self.rhodo_ref,
                                     "query": "",
                                     "sort_by": [["feature_id", True]]})[0]
        self.assertEqual(ret["num_found"], 4158)
        self.check_genome(self.rhodo_ref)

    def test_rhodobacter_genome_contigs(self):
        ret = self.getImpl().search_contigs(self.getContext(),
                                            {"ref": self.rhodo_ref,
                                             "query": "",
                                             "sort_by": [["length", False]]}
                                            )[0]
        self.assertTrue("num_found" in ret)
        self.assertEqual(ret["num_found"], 304)
        ret = self.getImpl().search_contigs(self.getContext(),
                                            {"ref": self.banno_ref,
                                             "query": "NODE_14_length_34118_cov_5.00684_ID_27",
                                             "sort_by": [["length", False]]}
                                            )[0]
        self.assertTrue("num_found" in ret)
        self.assertEqual(ret["num_found"], 1)

    def test_rhodobacter_genome_regions(self):
        ret = self.getImpl().search_region(self.getContext(),
                                           {"ref": self.rhodo_ref,
                                            "query_contig_id": "NODE_48_length_21448_cov_4.91263_ID_95",
                                            "query_region_start": 0,
                                            "query_region_length": 10000,
                                            "page_start": 1,
                                            "page_limit": 5})[0]
        self.assertEqual(len(ret["features"]), 5)
        self.assertEqual(ret['features'][0]['feature_id'], 'kb|g.220339.CDS.2')
        self.assertEqual(ret['num_found'], 12)

    def test_new_ecoli_genome_features(self):
        ret = self.getImpl().search(self.getContext(),
                                    {"ref": self.eco_ref,
                                     "query": "",
                                     "sort_by": [["feature_id", True]]})[0]
        self.assertEqual(ret["num_found"], 8638)
        # type query
        ret = self.getImpl().search(self.getContext(),
                                    {"ref": self.eco_ref,
                                     "query": "gene",
                                     "sort_by": [["feature_id", True]]})[0]
        self.assertEqual(ret["num_found"], 4371)
        # alias query
        ret = self.getImpl().search(self.getContext(),
                                    {"ref": self.eco_ref,
                                     "query": "thrL",
                                     "sort_by": [["feature_id", True]]})[0]
        self.assertEqual(ret["num_found"], 2)
        self.check_genome(self.eco_ref)

    def test_new_ecoli_genome_contigs(self):
        ret = self.getImpl().search_contigs(self.getContext(),
                                            {"ref": self.eco_ref,
                                             "query": "",
                                             "sort_by": [["length", False]]}
                                            )[0]
        self.assertTrue("num_found" in ret)
        self.assertEqual(ret["num_found"], 1)

    def test_new_ecoli_genome_regions(self):
        ret = self.getImpl().search_region(self.getContext(),
                                           {"ref": self.eco_ref,
                                            "query_contig_id": "NC_000913.3",
                                            "query_region_start": 0,
                                            "query_region_length": 10000,
                                            "page_start": 1,
                                            "page_limit": 5})[0]
        self.assertEqual(len(ret["features"]), 5)
        self.assertEqual(ret['features'][0]['feature_id'], 'b0001_CDS_1')
        self.assertEqual(ret['num_found'], 20)

    def test_new_ecoli_genome_ontologies(self):
        ret = self.getImpl().search(self.getContext(),
                                    {"ref": self.eco_ref,
                                     "query": "GO:0009088 gene",
                                     "limit": 1})[0]
        self.assertEqual(ret["num_found"], 8)
        self.assertEqual(len(ret["features"]), 1)
        print("MEH", ret["features"][0])
        self.assertTrue("threonine biosynthetic process" in ret["features"][0]
            ["ontology_terms"]["GO:0009088"])
