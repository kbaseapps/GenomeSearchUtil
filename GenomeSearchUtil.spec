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

    typedef structure {
        string ref;
        string query;
        list<column_sorting> sort_by;
        int start;
        int limit;
    } SearchOptions;

    typedef structure {
        string contig_id;
        int start;
        string strand;
        int length;
    } Location;

    typedef structure {
        string feature_id;
        mapping <string, list<string>> aliases;
        string function;
        list<Location> location;
        string feature_type;
        Location global_location;
    } FeatureData;

    /*
        num_found - number of all items found in query search (with 
            only part of it returned in "features" list).
    */
    typedef structure {
        int start;
        list <FeatureData> features;
        int num_found;
    } SearchResult;

    funcdef search(SearchOptions params) returns (SearchResult result) authentication optional;
};
