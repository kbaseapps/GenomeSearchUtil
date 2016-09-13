/*
A KBase module: GenomeSearchUtil
*/

module GenomeSearchUtil {

    /*
        Indicates true or false values, false = 0, true = 1
        @range [0,1]
    */
    typedef int boolean;

    typedef tuple<string column, boolean ascending> column_sorting;

    /*
        num_found - optional field which when set informs that there
            is no need to perform full scan in order to count this
            value because it was already done before; please don't
            set this value with 0 or any guessed number if you didn't 
            get right value previously.
    */
    typedef structure {
        string ref;
        string query;
        list<column_sorting> sort_by;
        int start;
        int limit;
        int num_found;
    } SearchOptions;

    typedef structure {
        string contig_id;
        int start;
        string strand;
        int length;
    } Location;

    /*
        global_location - this is location-related properties that
            are under sorting whereas items in "location" array are not
        feature_idx - legacy field keeping the position of feature in
            feature array in legacy Genome object.
    */
    typedef structure {
        string feature_id;
        mapping <string, list<string>> aliases;
        string function;
        list<Location> location;
        string feature_type;
        Location global_location;
        int feature_idx;
    } FeatureData;

    /*
        num_found - number of all items found in query search (with 
            only part of it returned in "features" list).
    */
    typedef structure {
        string query;
        int start;
        list <FeatureData> features;
        int num_found;
    } SearchResult;

    funcdef search(SearchOptions params) returns (SearchResult result) authentication optional;

    /*
        num_found - optional field which when set informs that there
            is no need to perform full scan in order to count this
            value because it was already done before; please don't
            set this value with 0 or any guessed number if you didn't 
            get right value previously.
    */
    typedef structure {
        string ref;
        string query_contig_id;
        int query_region_start;
        int query_region_length;
        int page_start;
        int page_limit;
        int num_found;
    } SearchRegionOptions;

    /*
        num_found - number of all items found in query search (with 
            only part of it returned in "features" list).
    */
    typedef structure {
        string query_contig_id;
        int query_region_start;
        int query_region_length;
        int page_start;
        list <FeatureData> features;
        int num_found;
    } SearchRegionResult;

    funcdef search_region(SearchRegionOptions params) returns (SearchRegionResult result) authentication optional;

    /*
        num_found - optional field which when set informs that there
            is no need to perform full scan in order to count this
            value because it was already done before; please don't
            set this value with 0 or any guessed number if you didn't 
            get right value previously.
    */
    typedef structure {
        string ref;
        string query;
        list<column_sorting> sort_by;
        int start;
        int limit;
        int num_found;
    } SearchContigsOptions;

    /*
        global_location - this is location-related properties that
            are under sorting whereas items in "location" array are not
        feature_idx - legacy field keeping the position of feature in
            feature array in legacy Genome object.
    */
    typedef structure {
        string contig_id;
        int length;
        int feature_count;
    } ContigData;

    /*
        num_found - number of all items found in query search (with 
            only part of it returned in "features" list).
    */
    typedef structure {
        string query;
        int start;
        list<ContigData> contigs;
        int num_found;
    } SearchContigsResult;

    funcdef search_contigs(SearchContigsOptions params) 
        returns (SearchContigsResult result) authentication optional;

};
