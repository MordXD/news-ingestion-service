package Feed::Fetcher;
use strict;
use warnings;
use utf8;

use LWP::UserAgent;

sub fetch {
    my ($url) = @_;

    my $ua = LWP::UserAgent->new(
        timeout  => 30,
        agent    => 'FeedParser/1.0',
        ssl_opts => { verify_hostname => 1 },
    );

    my $response = $ua->get($url);

    if (!$response->is_success) {
        return (undef, undef, "HTTP error: " . $response->status_line);
    }

    my $xml        = $response->decoded_content;
    my $final_url  = $response->request->uri->as_string;

    return ($xml, $final_url, undef);
}

1;
