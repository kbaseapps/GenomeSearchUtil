
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
 * <p>Original spec-file type: Location</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "contig_id",
    "start",
    "strand",
    "length"
})
public class Location {

    @JsonProperty("contig_id")
    private String contigId;
    @JsonProperty("start")
    private Long start;
    @JsonProperty("strand")
    private String strand;
    @JsonProperty("length")
    private Long length;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("contig_id")
    public String getContigId() {
        return contigId;
    }

    @JsonProperty("contig_id")
    public void setContigId(String contigId) {
        this.contigId = contigId;
    }

    public Location withContigId(String contigId) {
        this.contigId = contigId;
        return this;
    }

    @JsonProperty("start")
    public Long getStart() {
        return start;
    }

    @JsonProperty("start")
    public void setStart(Long start) {
        this.start = start;
    }

    public Location withStart(Long start) {
        this.start = start;
        return this;
    }

    @JsonProperty("strand")
    public String getStrand() {
        return strand;
    }

    @JsonProperty("strand")
    public void setStrand(String strand) {
        this.strand = strand;
    }

    public Location withStrand(String strand) {
        this.strand = strand;
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

    public Location withLength(Long length) {
        this.length = length;
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
        return ((((((((((("Location"+" [contigId=")+ contigId)+", start=")+ start)+", strand=")+ strand)+", length=")+ length)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
