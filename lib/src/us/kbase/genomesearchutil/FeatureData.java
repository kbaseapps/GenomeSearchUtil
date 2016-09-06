
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
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "feature_id",
    "aliases",
    "function",
    "location",
    "feature_type"
})
public class FeatureData {

    @JsonProperty("feature_id")
    private java.lang.String featureId;
    @JsonProperty("aliases")
    private Map<String, List<String>> aliases;
    @JsonProperty("function")
    private java.lang.String function;
    @JsonProperty("location")
    private List<Location> location;
    @JsonProperty("feature_type")
    private java.lang.String featureType;
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
    public List<Location> getLocation() {
        return location;
    }

    @JsonProperty("location")
    public void setLocation(List<Location> location) {
        this.location = location;
    }

    public FeatureData withLocation(List<Location> location) {
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
        return ((((((((((((("FeatureData"+" [featureId=")+ featureId)+", aliases=")+ aliases)+", function=")+ function)+", location=")+ location)+", featureType=")+ featureType)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
