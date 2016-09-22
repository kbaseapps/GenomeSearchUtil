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
    GIT_COMMIT_HASH = "837128eb9392ef02296a4b33d69686424cbf030a"
    
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
        :param params: instance of type "SearchOptions" (num_found - optional
           field which when set informs that there is no need to perform full
           scan in order to count this value because it was already done
           before; please don't set this value with 0 or any guessed number
           if you didn't get right value previously.) -> structure: parameter
           "ref" of String, parameter "query" of String, parameter "sort_by"
           of list of type "column_sorting" -> tuple of size 2: parameter
           "column" of String, parameter "ascending" of type "boolean"
           (Indicates true or false values, false = 0, true = 1 @range
           [0,1]), parameter "start" of Long, parameter "limit" of Long,
           parameter "num_found" of Long
        :returns: instance of type "SearchResult" (num_found - number of all
           items found in query search (with only part of it returned in
           "features" list).) -> structure: parameter "query" of String,
           parameter "start" of Long, parameter "features" of list of type
           "FeatureData" (aliases - mapping from alias name (key) to set of
           alias sources (value), global_location - this is location-related
           properties that are under sorting whereas items in "location"
           array are not, feature_idx - legacy field keeping the position of
           feature in feature array in legacy Genome object, ontology_terms -
           mapping from term ID (key) to term name (value).) -> structure:
           parameter "feature_id" of String, parameter "aliases" of mapping
           from String to list of String, parameter "function" of String,
           parameter "location" of list of type "Location" -> structure:
           parameter "contig_id" of String, parameter "start" of Long,
           parameter "strand" of String, parameter "length" of Long,
           parameter "feature_type" of String, parameter "global_location" of
           type "Location" -> structure: parameter "contig_id" of String,
           parameter "start" of Long, parameter "strand" of String, parameter
           "length" of Long, parameter "feature_idx" of Long, parameter
           "ontology_terms" of mapping from String to String, parameter
           "num_found" of Long
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN search
        result = self.indexer.search(ctx["token"], 
                                     params.get("ref", None), 
                                     params.get("query", None), 
                                     params.get("sort_by", None),
                                     params.get("start", None), 
                                     params.get("limit", None),
                                     params.get("num_found", None))
        #END search

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method search return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def search_region(self, ctx, params):
        """
        :param params: instance of type "SearchRegionOptions" (num_found -
           optional field which when set informs that there is no need to
           perform full scan in order to count this value because it was
           already done before; please don't set this value with 0 or any
           guessed number if you didn't get right value previously.) ->
           structure: parameter "ref" of String, parameter "query_contig_id"
           of String, parameter "query_region_start" of Long, parameter
           "query_region_length" of Long, parameter "page_start" of Long,
           parameter "page_limit" of Long, parameter "num_found" of Long
        :returns: instance of type "SearchRegionResult" (num_found - number
           of all items found in query search (with only part of it returned
           in "features" list).) -> structure: parameter "query_contig_id" of
           String, parameter "query_region_start" of Long, parameter
           "query_region_length" of Long, parameter "page_start" of Long,
           parameter "features" of list of type "FeatureData" (aliases -
           mapping from alias name (key) to set of alias sources (value),
           global_location - this is location-related properties that are
           under sorting whereas items in "location" array are not,
           feature_idx - legacy field keeping the position of feature in
           feature array in legacy Genome object, ontology_terms - mapping
           from term ID (key) to term name (value).) -> structure: parameter
           "feature_id" of String, parameter "aliases" of mapping from String
           to list of String, parameter "function" of String, parameter
           "location" of list of type "Location" -> structure: parameter
           "contig_id" of String, parameter "start" of Long, parameter
           "strand" of String, parameter "length" of Long, parameter
           "feature_type" of String, parameter "global_location" of type
           "Location" -> structure: parameter "contig_id" of String,
           parameter "start" of Long, parameter "strand" of String, parameter
           "length" of Long, parameter "feature_idx" of Long, parameter
           "ontology_terms" of mapping from String to String, parameter
           "num_found" of Long
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN search_region
        result = self.indexer.search_region(ctx["token"], 
                                            params.get("ref", None), 
                                            params.get("query_contig_id", None), 
                                            params.get("query_region_start", None),
                                            params.get("query_region_length", None),
                                            params.get("page_start", None), 
                                            params.get("page_limit", None),
                                            params.get("num_found", None))
        #END search_region

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method search_region return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def search_contigs(self, ctx, params):
        """
        :param params: instance of type "SearchContigsOptions" (num_found -
           optional field which when set informs that there is no need to
           perform full scan in order to count this value because it was
           already done before; please don't set this value with 0 or any
           guessed number if you didn't get right value previously.) ->
           structure: parameter "ref" of String, parameter "query" of String,
           parameter "sort_by" of list of type "column_sorting" -> tuple of
           size 2: parameter "column" of String, parameter "ascending" of
           type "boolean" (Indicates true or false values, false = 0, true =
           1 @range [0,1]), parameter "start" of Long, parameter "limit" of
           Long, parameter "num_found" of Long
        :returns: instance of type "SearchContigsResult" (num_found - number
           of all items found in query search (with only part of it returned
           in "features" list).) -> structure: parameter "query" of String,
           parameter "start" of Long, parameter "contigs" of list of type
           "ContigData" (global_location - this is location-related
           properties that are under sorting whereas items in "location"
           array are not feature_idx - legacy field keeping the position of
           feature in feature array in legacy Genome object.) -> structure:
           parameter "contig_id" of String, parameter "length" of Long,
           parameter "feature_count" of Long, parameter "num_found" of Long
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN search_contigs
        result = self.indexer.search_contigs(ctx["token"], 
                                             params.get("ref", None), 
                                             params.get("query", None), 
                                             params.get("sort_by", None),
                                             params.get("start", None), 
                                             params.get("limit", None),
                                             params.get("num_found", None))
        #END search_contigs

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method search_contigs return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK", 'message': "", 'version': self.VERSION, 
                     'git_url': self.GIT_URL, 'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
