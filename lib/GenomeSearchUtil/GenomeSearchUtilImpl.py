# -*- coding: utf-8 -*-
#BEGIN_HEADER
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
    GIT_URL = ""
    GIT_COMMIT_HASH = ""
    
    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
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
           "features" list).) -> structure: parameter "start" of Long,
           parameter "features" of list of type "FeatureData" -> structure:
           parameter "feature_id" of String, parameter "aliases" of mapping
           from String to list of String, parameter "function" of String,
           parameter "location" of list of type "Location" -> structure:
           parameter "contig_id" of String, parameter "start" of Long,
           parameter "strand" of String, parameter "length" of Long,
           parameter "feature_type" of String, parameter "num_found" of Long
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN search
        result = {}
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
