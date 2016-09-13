
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
 * <p>Original spec-file type: ContigData</p>
 * <pre>
 * global_location - this is location-related properties that
 *     are under sorting whereas items in "location" array are not
 * feature_idx - legacy field keeping the position of feature in
 *     feature array in legacy Genome object.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "contig_id",
    "length",
    "feature_count"
})
public class ContigData {

    @JsonProperty("contig_id")
    private String contigId;
    @JsonProperty("length")
    private Long length;
    @JsonProperty("feature_count")
    private Long featureCount;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("contig_id")
    public String getContigId() {
        return contigId;
    }

    @JsonProperty("contig_id")
    public void setContigId(String contigId) {
        this.contigId = contigId;
    }

    public ContigData withContigId(String contigId) {
        this.contigId = contigId;
        return this;
    }

    @JsonProperty("length")
    public Long getLength() {
        return length;
    }

    @JsonProperty("length")
    public void setLength(Long length) {
        this.length = length;
    }

    public ContigData withLength(Long length) {
        this.length = length;
        return this;
    }

    @JsonProperty("feature_count")
    public Long getFeatureCount() {
        return featureCount;
    }

    @JsonProperty("feature_count")
    public void setFeatureCount(Long featureCount) {
        this.featureCount = featureCount;
    }

    public ContigData withFeatureCount(Long featureCount) {
        this.featureCount = featureCount;
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
        return ((((((((("ContigData"+" [contigId=")+ contigId)+", length=")+ length)+", featureCount=")+ featureCount)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
