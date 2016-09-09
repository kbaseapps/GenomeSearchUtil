
package us.kbase.genomesearchutil;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: SearchRegionResult</p>
 * <pre>
 * num_found - number of all items found in query search (with 
 *     only part of it returned in "features" list).
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "query_contig_id",
    "query_region_start",
    "query_region_length",
    "page_start",
    "features",
    "num_found"
})
public class SearchRegionResult {

    @JsonProperty("query_contig_id")
    private String queryContigId;
    @JsonProperty("query_region_start")
    private Long queryRegionStart;
    @JsonProperty("query_region_length")
    private Long queryRegionLength;
    @JsonProperty("page_start")
    private Long pageStart;
    @JsonProperty("features")
    private List<FeatureData> features;
    @JsonProperty("num_found")
    private Long numFound;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("query_contig_id")
    public String getQueryContigId() {
        return queryContigId;
    }

    @JsonProperty("query_contig_id")
    public void setQueryContigId(String queryContigId) {
        this.queryContigId = queryContigId;
    }

    public SearchRegionResult withQueryContigId(String queryContigId) {
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

    public SearchRegionResult withQueryRegionStart(Long queryRegionStart) {
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

    public SearchRegionResult withQueryRegionLength(Long queryRegionLength) {
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

    public SearchRegionResult withPageStart(Long pageStart) {
        this.pageStart = pageStart;
        return this;
    }

    @JsonProperty("features")
    public List<FeatureData> getFeatures() {
        return features;
    }

    @JsonProperty("features")
    public void setFeatures(List<FeatureData> features) {
        this.features = features;
    }

    public SearchRegionResult withFeatures(List<FeatureData> features) {
        this.features = features;
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

    public SearchRegionResult withNumFound(Long numFound) {
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
        return ((((((((((((((("SearchRegionResult"+" [queryContigId=")+ queryContigId)+", queryRegionStart=")+ queryRegionStart)+", queryRegionLength=")+ queryRegionLength)+", pageStart=")+ pageStart)+", features=")+ features)+", numFound=")+ numFound)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
