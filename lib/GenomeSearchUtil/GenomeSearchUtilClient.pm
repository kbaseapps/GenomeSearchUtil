package GenomeSearchUtil::GenomeSearchUtilClient;

use JSON::RPC::Client;
use POSIX;
use strict;
use Data::Dumper;
use URI;
use Bio::KBase::Exceptions;
my $get_time = sub { time, 0 };
eval {
    require Time::HiRes;
    $get_time = sub { Time::HiRes::gettimeofday() };
};

use Bio::KBase::AuthToken;

# Client version should match Impl version
# This is a Semantic Version number,
# http://semver.org
our $VERSION = "0.1.0";

=head1 NAME

GenomeSearchUtil::GenomeSearchUtilClient

=head1 DESCRIPTION


A KBase module: GenomeSearchUtil


=cut

sub new
{
    my($class, $url, @args) = @_;
    

    my $self = {
	client => GenomeSearchUtil::GenomeSearchUtilClient::RpcClient->new,
	url => $url,
	headers => [],
    };

    chomp($self->{hostname} = `hostname`);
    $self->{hostname} ||= 'unknown-host';

    #
    # Set up for propagating KBRPC_TAG and KBRPC_METADATA environment variables through
    # to invoked services. If these values are not set, we create a new tag
    # and a metadata field with basic information about the invoking script.
    #
    if ($ENV{KBRPC_TAG})
    {
	$self->{kbrpc_tag} = $ENV{KBRPC_TAG};
    }
    else
    {
	my ($t, $us) = &$get_time();
	$us = sprintf("%06d", $us);
	my $ts = strftime("%Y-%m-%dT%H:%M:%S.${us}Z", gmtime $t);
	$self->{kbrpc_tag} = "C:$0:$self->{hostname}:$$:$ts";
    }
    push(@{$self->{headers}}, 'Kbrpc-Tag', $self->{kbrpc_tag});

    if ($ENV{KBRPC_METADATA})
    {
	$self->{kbrpc_metadata} = $ENV{KBRPC_METADATA};
	push(@{$self->{headers}}, 'Kbrpc-Metadata', $self->{kbrpc_metadata});
    }

    if ($ENV{KBRPC_ERROR_DEST})
    {
	$self->{kbrpc_error_dest} = $ENV{KBRPC_ERROR_DEST};
	push(@{$self->{headers}}, 'Kbrpc-Errordest', $self->{kbrpc_error_dest});
    }

    #
    # This module requires authentication.
    #
    # We create an auth token, passing through the arguments that we were (hopefully) given.

    {
	my %arg_hash2 = @args;
	if (exists $arg_hash2{"token"}) {
	    $self->{token} = $arg_hash2{"token"};
	} elsif (exists $arg_hash2{"user_id"}) {
	    my $token = Bio::KBase::AuthToken->new(@args);
	    if (!$token->error_message) {
	        $self->{token} = $token->token;
	    }
	}
	
	if (exists $self->{token})
	{
	    $self->{client}->{token} = $self->{token};
	}
    }

    my $ua = $self->{client}->ua;	 
    my $timeout = $ENV{CDMI_TIMEOUT} || (30 * 60);	 
    $ua->timeout($timeout);
    bless $self, $class;
    #    $self->_validate_version();
    return $self;
}




=head2 search

  $result = $obj->search($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a GenomeSearchUtil.SearchOptions
$result is a GenomeSearchUtil.SearchResult
SearchOptions is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a GenomeSearchUtil.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a GenomeSearchUtil.boolean
boolean is an int
SearchResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	features has a value which is a reference to a list where each element is a GenomeSearchUtil.FeatureData
	num_found has a value which is an int
FeatureData is a reference to a hash where the following keys are defined:
	feature_id has a value which is a string
	aliases has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a string
	function has a value which is a string
	location has a value which is a reference to a list where each element is a GenomeSearchUtil.Location
	feature_type has a value which is a string
	global_location has a value which is a GenomeSearchUtil.Location
	feature_array has a value which is a string
	feature_idx has a value which is an int
	ontology_terms has a value which is a reference to a hash where the key is a string and the value is a string
Location is a reference to a hash where the following keys are defined:
	contig_id has a value which is a string
	start has a value which is an int
	strand has a value which is a string
	length has a value which is an int

</pre>

=end html

=begin text

$params is a GenomeSearchUtil.SearchOptions
$result is a GenomeSearchUtil.SearchResult
SearchOptions is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a GenomeSearchUtil.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a GenomeSearchUtil.boolean
boolean is an int
SearchResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	features has a value which is a reference to a list where each element is a GenomeSearchUtil.FeatureData
	num_found has a value which is an int
FeatureData is a reference to a hash where the following keys are defined:
	feature_id has a value which is a string
	aliases has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a string
	function has a value which is a string
	location has a value which is a reference to a list where each element is a GenomeSearchUtil.Location
	feature_type has a value which is a string
	global_location has a value which is a GenomeSearchUtil.Location
	feature_array has a value which is a string
	feature_idx has a value which is an int
	ontology_terms has a value which is a reference to a hash where the key is a string and the value is a string
Location is a reference to a hash where the following keys are defined:
	contig_id has a value which is a string
	start has a value which is an int
	strand has a value which is a string
	length has a value which is an int


=end text

=item Description



=back

=cut

 sub search
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function search (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to search:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'search');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "GenomeSearchUtil.search",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'search',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method search",
					    status_line => $self->{client}->status_line,
					    method_name => 'search',
				       );
    }
}
 


=head2 search_region

  $result = $obj->search_region($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a GenomeSearchUtil.SearchRegionOptions
$result is a GenomeSearchUtil.SearchRegionResult
SearchRegionOptions is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	query_contig_id has a value which is a string
	query_region_start has a value which is an int
	query_region_length has a value which is an int
	page_start has a value which is an int
	page_limit has a value which is an int
	num_found has a value which is an int
SearchRegionResult is a reference to a hash where the following keys are defined:
	query_contig_id has a value which is a string
	query_region_start has a value which is an int
	query_region_length has a value which is an int
	page_start has a value which is an int
	features has a value which is a reference to a list where each element is a GenomeSearchUtil.FeatureData
	num_found has a value which is an int
FeatureData is a reference to a hash where the following keys are defined:
	feature_id has a value which is a string
	aliases has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a string
	function has a value which is a string
	location has a value which is a reference to a list where each element is a GenomeSearchUtil.Location
	feature_type has a value which is a string
	global_location has a value which is a GenomeSearchUtil.Location
	feature_array has a value which is a string
	feature_idx has a value which is an int
	ontology_terms has a value which is a reference to a hash where the key is a string and the value is a string
Location is a reference to a hash where the following keys are defined:
	contig_id has a value which is a string
	start has a value which is an int
	strand has a value which is a string
	length has a value which is an int

</pre>

=end html

=begin text

$params is a GenomeSearchUtil.SearchRegionOptions
$result is a GenomeSearchUtil.SearchRegionResult
SearchRegionOptions is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	query_contig_id has a value which is a string
	query_region_start has a value which is an int
	query_region_length has a value which is an int
	page_start has a value which is an int
	page_limit has a value which is an int
	num_found has a value which is an int
SearchRegionResult is a reference to a hash where the following keys are defined:
	query_contig_id has a value which is a string
	query_region_start has a value which is an int
	query_region_length has a value which is an int
	page_start has a value which is an int
	features has a value which is a reference to a list where each element is a GenomeSearchUtil.FeatureData
	num_found has a value which is an int
FeatureData is a reference to a hash where the following keys are defined:
	feature_id has a value which is a string
	aliases has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a string
	function has a value which is a string
	location has a value which is a reference to a list where each element is a GenomeSearchUtil.Location
	feature_type has a value which is a string
	global_location has a value which is a GenomeSearchUtil.Location
	feature_array has a value which is a string
	feature_idx has a value which is an int
	ontology_terms has a value which is a reference to a hash where the key is a string and the value is a string
Location is a reference to a hash where the following keys are defined:
	contig_id has a value which is a string
	start has a value which is an int
	strand has a value which is a string
	length has a value which is an int


=end text

=item Description



=back

=cut

 sub search_region
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function search_region (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to search_region:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'search_region');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "GenomeSearchUtil.search_region",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'search_region',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method search_region",
					    status_line => $self->{client}->status_line,
					    method_name => 'search_region',
				       );
    }
}
 


=head2 search_contigs

  $result = $obj->search_contigs($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a GenomeSearchUtil.SearchContigsOptions
$result is a GenomeSearchUtil.SearchContigsResult
SearchContigsOptions is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a GenomeSearchUtil.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a GenomeSearchUtil.boolean
boolean is an int
SearchContigsResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	contigs has a value which is a reference to a list where each element is a GenomeSearchUtil.ContigData
	num_found has a value which is an int
ContigData is a reference to a hash where the following keys are defined:
	contig_id has a value which is a string
	length has a value which is an int
	feature_count has a value which is an int

</pre>

=end html

=begin text

$params is a GenomeSearchUtil.SearchContigsOptions
$result is a GenomeSearchUtil.SearchContigsResult
SearchContigsOptions is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	query has a value which is a string
	sort_by has a value which is a reference to a list where each element is a GenomeSearchUtil.column_sorting
	start has a value which is an int
	limit has a value which is an int
	num_found has a value which is an int
column_sorting is a reference to a list containing 2 items:
	0: (column) a string
	1: (ascending) a GenomeSearchUtil.boolean
boolean is an int
SearchContigsResult is a reference to a hash where the following keys are defined:
	query has a value which is a string
	start has a value which is an int
	contigs has a value which is a reference to a list where each element is a GenomeSearchUtil.ContigData
	num_found has a value which is an int
ContigData is a reference to a hash where the following keys are defined:
	contig_id has a value which is a string
	length has a value which is an int
	feature_count has a value which is an int


=end text

=item Description



=back

=cut

 sub search_contigs
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function search_contigs (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to search_contigs:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'search_contigs');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "GenomeSearchUtil.search_contigs",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'search_contigs',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method search_contigs",
					    status_line => $self->{client}->status_line,
					    method_name => 'search_contigs',
				       );
    }
}
 
  
sub status
{
    my($self, @args) = @_;
    if ((my $n = @args) != 0) {
        Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
                                   "Invalid argument count for function status (received $n, expecting 0)");
    }
    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
        method => "GenomeSearchUtil.status",
        params => \@args,
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
                           code => $result->content->{error}->{code},
                           method_name => 'status',
                           data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
                          );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method status",
                        status_line => $self->{client}->status_line,
                        method_name => 'status',
                       );
    }
}
   

sub version {
    my ($self) = @_;
    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
        method => "GenomeSearchUtil.version",
        params => [],
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(
                error => $result->error_message,
                code => $result->content->{code},
                method_name => 'search_contigs',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method search_contigs",
            status_line => $self->{client}->status_line,
            method_name => 'search_contigs',
        );
    }
}

sub _validate_version {
    my ($self) = @_;
    my $svr_version = $self->version();
    my $client_version = $VERSION;
    my ($cMajor, $cMinor) = split(/\./, $client_version);
    my ($sMajor, $sMinor) = split(/\./, $svr_version);
    if ($sMajor != $cMajor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Major version numbers differ.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor < $cMinor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Client minor version greater than Server minor version.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor > $cMinor) {
        warn "New client version available for GenomeSearchUtil::GenomeSearchUtilClient\n";
    }
    if ($sMajor == 0) {
        warn "GenomeSearchUtil::GenomeSearchUtilClient version is $svr_version. API subject to change.\n";
    }
}

=head1 TYPES



=head2 boolean

=over 4



=item Description

Indicates true or false values, false = 0, true = 1
@range [0,1]


=item Definition

=begin html

<pre>
an int
</pre>

=end html

=begin text

an int

=end text

=back



=head2 column_sorting

=over 4



=item Definition

=begin html

<pre>
a reference to a list containing 2 items:
0: (column) a string
1: (ascending) a GenomeSearchUtil.boolean

</pre>

=end html

=begin text

a reference to a list containing 2 items:
0: (column) a string
1: (ascending) a GenomeSearchUtil.boolean


=end text

=back



=head2 SearchOptions

=over 4



=item Description

num_found - optional field which when set informs that there
    is no need to perform full scan in order to count this
    value because it was already done before; please don't
    set this value with 0 or any guessed number if you didn't 
    get right value previously.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a GenomeSearchUtil.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a GenomeSearchUtil.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int


=end text

=back



=head2 Location

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
contig_id has a value which is a string
start has a value which is an int
strand has a value which is a string
length has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
contig_id has a value which is a string
start has a value which is an int
strand has a value which is a string
length has a value which is an int


=end text

=back



=head2 FeatureData

=over 4



=item Description

aliases - mapping from alias name (key) to set of alias sources 
    (value),
global_location - this is location-related properties that are
    under sorting whereas items in "location" array are not,
feature_array - field recording which array a feature is located in
    (features, mrnas, cdss, ect.)
feature_idx - field keeping the position of feature in
    it's array in a Genome object,
ontology_terms - mapping from term ID (key) to term name (value).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
feature_id has a value which is a string
aliases has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a string
function has a value which is a string
location has a value which is a reference to a list where each element is a GenomeSearchUtil.Location
feature_type has a value which is a string
global_location has a value which is a GenomeSearchUtil.Location
feature_array has a value which is a string
feature_idx has a value which is an int
ontology_terms has a value which is a reference to a hash where the key is a string and the value is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
feature_id has a value which is a string
aliases has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a string
function has a value which is a string
location has a value which is a reference to a list where each element is a GenomeSearchUtil.Location
feature_type has a value which is a string
global_location has a value which is a GenomeSearchUtil.Location
feature_array has a value which is a string
feature_idx has a value which is an int
ontology_terms has a value which is a reference to a hash where the key is a string and the value is a string


=end text

=back



=head2 SearchResult

=over 4



=item Description

num_found - number of all items found in query search (with 
    only part of it returned in "features" list).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
features has a value which is a reference to a list where each element is a GenomeSearchUtil.FeatureData
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
features has a value which is a reference to a list where each element is a GenomeSearchUtil.FeatureData
num_found has a value which is an int


=end text

=back



=head2 SearchRegionOptions

=over 4



=item Description

num_found - optional field which when set informs that there
    is no need to perform full scan in order to count this
    value because it was already done before; please don't
    set this value with 0 or any guessed number if you didn't 
    get right value previously.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a string
query_contig_id has a value which is a string
query_region_start has a value which is an int
query_region_length has a value which is an int
page_start has a value which is an int
page_limit has a value which is an int
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a string
query_contig_id has a value which is a string
query_region_start has a value which is an int
query_region_length has a value which is an int
page_start has a value which is an int
page_limit has a value which is an int
num_found has a value which is an int


=end text

=back



=head2 SearchRegionResult

=over 4



=item Description

num_found - number of all items found in query search (with 
    only part of it returned in "features" list).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
query_contig_id has a value which is a string
query_region_start has a value which is an int
query_region_length has a value which is an int
page_start has a value which is an int
features has a value which is a reference to a list where each element is a GenomeSearchUtil.FeatureData
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
query_contig_id has a value which is a string
query_region_start has a value which is an int
query_region_length has a value which is an int
page_start has a value which is an int
features has a value which is a reference to a list where each element is a GenomeSearchUtil.FeatureData
num_found has a value which is an int


=end text

=back



=head2 SearchContigsOptions

=over 4



=item Description

num_found - optional field which when set informs that there
    is no need to perform full scan in order to count this
    value because it was already done before; please don't
    set this value with 0 or any guessed number if you didn't 
    get right value previously.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a GenomeSearchUtil.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a string
query has a value which is a string
sort_by has a value which is a reference to a list where each element is a GenomeSearchUtil.column_sorting
start has a value which is an int
limit has a value which is an int
num_found has a value which is an int


=end text

=back



=head2 ContigData

=over 4



=item Description

global_location - this is location-related properties that
    are under sorting whereas items in "location" array are not
feature_idx - legacy field keeping the position of feature in
    feature array in legacy Genome object.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
contig_id has a value which is a string
length has a value which is an int
feature_count has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
contig_id has a value which is a string
length has a value which is an int
feature_count has a value which is an int


=end text

=back



=head2 SearchContigsResult

=over 4



=item Description

num_found - number of all items found in query search (with 
    only part of it returned in "features" list).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
contigs has a value which is a reference to a list where each element is a GenomeSearchUtil.ContigData
num_found has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
query has a value which is a string
start has a value which is an int
contigs has a value which is a reference to a list where each element is a GenomeSearchUtil.ContigData
num_found has a value which is an int


=end text

=back



=cut

package GenomeSearchUtil::GenomeSearchUtilClient::RpcClient;
use base 'JSON::RPC::Client';
use POSIX;
use strict;

#
# Override JSON::RPC::Client::call because it doesn't handle error returns properly.
#

sub call {
    my ($self, $uri, $headers, $obj) = @_;
    my $result;


    {
	if ($uri =~ /\?/) {
	    $result = $self->_get($uri);
	}
	else {
	    Carp::croak "not hashref." unless (ref $obj eq 'HASH');
	    $result = $self->_post($uri, $headers, $obj);
	}

    }

    my $service = $obj->{method} =~ /^system\./ if ( $obj );

    $self->status_line($result->status_line);

    if ($result->is_success) {

        return unless($result->content); # notification?

        if ($service) {
            return JSON::RPC::ServiceObject->new($result, $self->json);
        }

        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    elsif ($result->content_type eq 'application/json')
    {
        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    else {
        return;
    }
}


sub _post {
    my ($self, $uri, $headers, $obj) = @_;
    my $json = $self->json;

    $obj->{version} ||= $self->{version} || '1.1';

    if ($obj->{version} eq '1.0') {
        delete $obj->{version};
        if (exists $obj->{id}) {
            $self->id($obj->{id}) if ($obj->{id}); # if undef, it is notification.
        }
        else {
            $obj->{id} = $self->id || ($self->id('JSON::RPC::Client'));
        }
    }
    else {
        # $obj->{id} = $self->id if (defined $self->id);
	# Assign a random number to the id if one hasn't been set
	$obj->{id} = (defined $self->id) ? $self->id : substr(rand(),2);
    }

    my $content = $json->encode($obj);

    $self->ua->post(
        $uri,
        Content_Type   => $self->{content_type},
        Content        => $content,
        Accept         => 'application/json',
	@$headers,
	($self->{token} ? (Authorization => $self->{token}) : ()),
    );
}



1;
