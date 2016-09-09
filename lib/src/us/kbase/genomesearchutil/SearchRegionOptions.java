
package us.kbase.genomesearchutil;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: SearchRegionOptions</p>
 * <pre>
 * num_found - optional field which when set informs that there
 *     is no need to perform full scan in order to count this
 *     value because it was already done before; please don't
 *     set this value with 0 or any guessed number if you didn't 
 *     get right value previously.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "ref",
    "query_contig_id",
    "query_region_start",
    "query_region_length",
    "page_start",
    "page_limit",
    "num_found"
})
public class SearchRegionOptions {

    @JsonProperty("ref")
    private String ref;
    @JsonProperty("query_contig_id")
    private String queryContigId;
    @JsonProperty("query_region_start")
    private Long queryRegionStart;
    @JsonProperty("query_region_length")
    private Long queryRegionLength;
    @JsonProperty("page_start")
    private Long pageStart;
    @JsonProperty("page_limit")
    private Long pageLimit;
    @JsonProperty("num_found")
    private Long numFound;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("ref")
    public String getRef() {
        return ref;
    }

    @JsonProperty("ref")
    public void setRef(String ref) {
        this.ref = ref;
    }

    public SearchRegionOptions withRef(String ref) {
        this.ref = ref;
        return this;
    }

    @JsonProperty("query_contig_id")
    public String getQueryContigId() {
        return queryContigId;
    }

    @JsonProperty("query_contig_id")
    public void setQueryContigId(String queryContigId) {
        this.queryContigId = queryContigId;
    }

    public SearchRegionOptions withQueryContigId(String queryContigId) {
        this.queryContigId = queryContigId;
        return this;
    }

    @JsonProperty("query_region_start")
    public Long getQueryRegionStart() {
        return queryRegionStart;
    }

    @JsonProperty("query_region_start")
    public void setQueryRegionStart(Long queryRegionStart) {
        this.queryRegionStart = queryRegionStart;
    }

    public SearchRegionOptions withQueryRegionStart(Long queryRegionStart) {
        this.queryRegionStart = queryRegionStart;
        return this;
    }

    @JsonProperty("query_region_length")
    public Long getQueryRegionLength() {
        return queryRegionLength;
    }

    @JsonProperty("query_region_length")
    public void setQueryRegionLength(Long queryRegionLength) {
        this.queryRegionLength = queryRegionLength;
    }

    public SearchRegionOptions withQueryRegionLength(Long queryRegionLength) {
        this.queryRegionLength = queryRegionLength;
        return this;
    }

    @JsonProperty("page_start")
    public Long getPageStart() {
        return pageStart;
    }

    @JsonProperty("page_start")
    public void setPageStart(Long pageStart) {
        this.pageStart = pageStart;
    }

    public SearchRegionOptions withPageStart(Long pageStart) {
        this.pageStart = pageStart;
        return this;
    }

    @JsonProperty("page_limit")
    public Long getPageLimit() {
        return pageLimit;
    }

    @JsonProperty("page_limit")
    public void setPageLimit(Long pageLimit) {
        this.pageLimit = pageLimit;
    }

    public SearchRegionOptions withPageLimit(Long pageLimit) {
        this.pageLimit = pageLimit;
        return this;
    }

    @JsonProperty("num_found")
    public Long getNumFound() {
        return numFound;
    }

    @JsonProperty("num_found")
    public void setNumFound(Long numFound) {
        this.numFound = numFound;
    }

    public SearchRegionOptions withNumFound(Long numFound) {
        this.numFound = numFound;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((((((((((("SearchRegionOptions"+" [ref=")+ ref)+", queryContigId=")+ queryContigId)+", queryRegionStart=")+ queryRegionStart)+", queryRegionLength=")+ queryRegionLength)+", pageStart=")+ pageStart)+", pageLimit=")+ pageLimit)+", numFound=")+ numFound)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
