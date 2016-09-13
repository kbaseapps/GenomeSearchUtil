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

from biokbase.workspace.client import Workspace as workspaceService
from GenomeSearchUtil.GenomeSearchUtilImpl import GenomeSearchUtil
from GenomeSearchUtil.GenomeSearchUtilServer import MethodContext


class GenomeSearchUtilTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        user_id = requests.post(
            'https://kbase.us/services/authorization/Sessions/Login',
            data='token={}&fields=user_id'.format(token)).json()['user_id']
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
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('GenomeSearchUtil'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.cfg['genome-index-dir'] = cls.cfg['scratch']
        cls.cfg['debug'] = "1"
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = GenomeSearchUtil(cls.cfg)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_GenomeSearchUtil_" + str(suffix)
        self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    # NOTE: According to Python unittest naming rules test method names should start from 'test'.
    def test_search(self):
        public_ws = "KBasePublicGenomesV5"
        genome_ids = ["kb|g.0", "kb|g.3899", "kb|g.166832", "kb|g.166828", "kb|g.166814", "kb|g.166802", "kb|g.140106"]
        for genome_id in genome_ids:
            self.check_genome(public_ws + "/" + genome_id)

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
        #for feature in ret["features"]:
        #    print(json.dumps(feature))

    def test_genome_with_no_feature_locations(self):
        genome_ref = "KBaseExampleData/Transcriptome_Sbi_shoots_ABA_upregulated"
        ret = self.getImpl().search(self.getContext(), {"ref": genome_ref, "query": "Sb01g000360.1.CDS",
                "sort_by": [["feature_id", True]]})[0]
        self.assertTrue("num_found" in ret)
        self.assertEqual(ret["num_found"],1)

        ret = self.getImpl().search_region(self.getContext(), {"ref": genome_ref,
                "query_contig_id": "", "query_region_start": 100,
                "query_region_length": 10000, "page_limit": 5,
                "num_found": ret["num_found"]})[0]
        self.assertTrue("num_found" in ret)
        self.assertEqual(ret["num_found"],0)

    def test_search_region(self):
        ref = "KBasePublicGenomesV5/kb|g.0"
        ret = self.getImpl().search_region(self.getContext(), {"ref": ref,
                "query_contig_id": "kb|g.0.c.1", "query_region_start": 1000000,
                "query_region_length": 10000, "page_limit": 5})[0]
        print("Features found in region: " + str(ret["num_found"]))
        self.assertEqual(10, ret["num_found"])
        self.getImpl().search_region(self.getContext(), {"ref": ref,
                "query_contig_id": "kb|g.0.c.1", "query_region_start": 1000000,
                "query_region_length": 10000, "page_limit": 5, 
                "num_found": ret["num_found"]})[0]
