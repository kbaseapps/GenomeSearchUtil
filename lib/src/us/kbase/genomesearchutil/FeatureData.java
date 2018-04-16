
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
 * <p>Original spec-file type: FeatureData</p>
 * <pre>
 * aliases - mapping from alias name (key) to set of alias sources 
 *     (value),
 * global_location - this is location-related properties that are
 *     under sorting whereas items in "location" array are not,
 * feature_array - field recording which array a feature is located in
 *     (features, mrnas, cdss, non_coding_features)
 * feature_idx - field keeping the position of feature in its array in a
 *     Genome object,
 * ontology_terms - mapping from term ID (key) to term name (value).
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "feature_id",
    "aliases",
    "function",
    "location",
    "feature_type",
    "global_location",
    "feature_array",
    "feature_idx",
    "ontology_terms"
})
public class FeatureData {

    @JsonProperty("feature_id")
    private java.lang.String featureId;
    @JsonProperty("aliases")
    private Map<String, List<String>> aliases;
    @JsonProperty("function")
    private java.lang.String function;
    @JsonProperty("location")
    private List<us.kbase.genomesearchutil.Location> location;
    @JsonProperty("feature_type")
    private java.lang.String featureType;
    /**
     * <p>Original spec-file type: Location</p>
     * 
     * 
     */
    @JsonProperty("global_location")
    private us.kbase.genomesearchutil.Location globalLocation;
    @JsonProperty("feature_array")
    private java.lang.String featureArray;
    @JsonProperty("feature_idx")
    private Long featureIdx;
    @JsonProperty("ontology_terms")
    private Map<String, String> ontologyTerms;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("feature_id")
    public java.lang.String getFeatureId() {
        return featureId;
    }

    @JsonProperty("feature_id")
    public void setFeatureId(java.lang.String featureId) {
        this.featureId = featureId;
    }

    public FeatureData withFeatureId(java.lang.String featureId) {
        this.featureId = featureId;
        return this;
    }

    @JsonProperty("aliases")
    public Map<String, List<String>> getAliases() {
        return aliases;
    }

    @JsonProperty("aliases")
    public void setAliases(Map<String, List<String>> aliases) {
        this.aliases = aliases;
    }

    public FeatureData withAliases(Map<String, List<String>> aliases) {
        this.aliases = aliases;
        return this;
    }

    @JsonProperty("function")
    public java.lang.String getFunction() {
        return function;
    }

    @JsonProperty("function")
    public void setFunction(java.lang.String function) {
        this.function = function;
    }

    public FeatureData withFunction(java.lang.String function) {
        this.function = function;
        return this;
    }

    @JsonProperty("location")
    public List<us.kbase.genomesearchutil.Location> getLocation() {
        return location;
    }

    @JsonProperty("location")
    public void setLocation(List<us.kbase.genomesearchutil.Location> location) {
        this.location = location;
    }

    public FeatureData withLocation(List<us.kbase.genomesearchutil.Location> location) {
        this.location = location;
        return this;
    }

    @JsonProperty("feature_type")
    public java.lang.String getFeatureType() {
        return featureType;
    }

    @JsonProperty("feature_type")
    public void setFeatureType(java.lang.String featureType) {
        this.featureType = featureType;
    }

    public FeatureData withFeatureType(java.lang.String featureType) {
        this.featureType = featureType;
        return this;
    }

    /**
     * <p>Original spec-file type: Location</p>
     * 
     * 
     */
    @JsonProperty("global_location")
    public us.kbase.genomesearchutil.Location getGlobalLocation() {
        return globalLocation;
    }

    /**
     * <p>Original spec-file type: Location</p>
     * 
     * 
     */
    @JsonProperty("global_location")
    public void setGlobalLocation(us.kbase.genomesearchutil.Location globalLocation) {
        this.globalLocation = globalLocation;
    }

    public FeatureData withGlobalLocation(us.kbase.genomesearchutil.Location globalLocation) {
        this.globalLocation = globalLocation;
        return this;
    }

    @JsonProperty("feature_array")
    public java.lang.String getFeatureArray() {
        return featureArray;
    }

    @JsonProperty("feature_array")
    public void setFeatureArray(java.lang.String featureArray) {
        this.featureArray = featureArray;
    }

    public FeatureData withFeatureArray(java.lang.String featureArray) {
        this.featureArray = featureArray;
        return this;
    }

    @JsonProperty("feature_idx")
    public Long getFeatureIdx() {
        return featureIdx;
    }

    @JsonProperty("feature_idx")
    public void setFeatureIdx(Long featureIdx) {
        this.featureIdx = featureIdx;
    }

    public FeatureData withFeatureIdx(Long featureIdx) {
        this.featureIdx = featureIdx;
        return this;
    }

    @JsonProperty("ontology_terms")
    public Map<String, String> getOntologyTerms() {
        return ontologyTerms;
    }

    @JsonProperty("ontology_terms")
    public void setOntologyTerms(Map<String, String> ontologyTerms) {
        this.ontologyTerms = ontologyTerms;
    }

    public FeatureData withOntologyTerms(Map<String, String> ontologyTerms) {
        this.ontologyTerms = ontologyTerms;
        return this;
    }

    @JsonAnyGetter
    public Map<java.lang.String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(java.lang.String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public java.lang.String toString() {
        return ((((((((((((((((((((("FeatureData"+" [featureId=")+ featureId)+", aliases=")+ aliases)+", function=")+ function)+", location=")+ location)+", featureType=")+ featureType)+", globalLocation=")+ globalLocation)+", featureArray=")+ featureArray)+", featureIdx=")+ featureIdx)+", ontologyTerms=")+ ontologyTerms)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
