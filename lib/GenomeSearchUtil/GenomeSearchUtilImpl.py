# -*- coding: utf-8 -*-
#BEGIN_HEADER
from GenomeSearchUtil.GenomeSearchUtilIndexer import GenomeSearchUtilIndexer
#END_HEADER


class GenomeSearchUtil:
    '''
    Module Name:
    GenomeSearchUtil

    Module Description:
    A KBase module: GenomeSearchUtil
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kbaseapps/GenomeSearchUtil"
    GIT_COMMIT_HASH = "195ee6934de8fdc6842319025f891fbde15da170"
    
    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.indexer = GenomeSearchUtilIndexer(config)
        #END_CONSTRUCTOR
        pass
    

    def search(self, ctx, params):
        """
        :param params: instance of type "SearchOptions" -> structure:
           parameter "ref" of String, parameter "query" of String, parameter
           "sort_by" of list of type "column_sorting" -> tuple of size 2:
           parameter "column" of String, parameter "ascending" of type
           "boolean" (Indicates true or false values, false = 0, true = 1
           @range [0,1]), parameter "start" of Long, parameter "limit" of Long
        :returns: instance of type "SearchResult" (num_found - number of all
           items found in query search (with only part of it returned in
           "features" list).) -> structure: parameter "query" of String,
           parameter "start" of Long, parameter "features" of list of type
           "FeatureData" -> structure: parameter "feature_id" of String,
           parameter "aliases" of mapping from String to list of String,
           parameter "function" of String, parameter "location" of list of
           type "Location" -> structure: parameter "contig_id" of String,
           parameter "start" of Long, parameter "strand" of String, parameter
           "length" of Long, parameter "feature_type" of String, parameter
           "global_location" of type "Location" -> structure: parameter
           "contig_id" of String, parameter "start" of Long, parameter
           "strand" of String, parameter "length" of Long, parameter
           "num_found" of Long
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN search
        result = self.indexer.search(ctx["token"], params.get("ref", None), 
                                     params.get("query", None), params.get("sort_by", None),
                                     params.get("start", None), params.get("limit", None),
                                     params.get("num_found", None))
        #END search

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method search return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK", 'message': "", 'version': self.VERSION, 
                     'git_url': self.GIT_URL, 'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
