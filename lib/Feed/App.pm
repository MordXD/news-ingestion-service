package Feed::App;
use strict;
use warnings;
use utf8;

use Feed::Fetcher;
use Feed::Parser;
use Feed::Normalizer;
use Feed::JSONWriter;

sub new {
    my ($class) = @_;
    return bless {}, $class;
}

sub run {
    my ($self, $url) = @_;

    # Fetch
    my ($xml, $final_url, $fetch_error) = Feed::Fetcher::fetch($url);
    if ($fetch_error) {
        return (undef, $fetch_error);
    }

    # Parse
    my ($raw_data, $parse_error) = Feed::Parser::parse($xml);
    if ($parse_error) {
        return (undef, $parse_error);
    }

    # Normalize
    my $normalized = Feed::Normalizer::normalize($raw_data);

    # Add meta
    $normalized->{meta} = {
        source_url => $url,
        final_url  => $final_url,
    };

    # JSON
    my $json = Feed::JSONWriter::encode($normalized);

    return ($json, undef);
}

1;
