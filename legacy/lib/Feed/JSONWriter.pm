package Feed::JSONWriter;
use strict;
use warnings;
use utf8;

use JSON::PP ();

sub encode {
    my ($data) = @_;

    my $json = JSON::PP->new->utf8->canonical;

    # Pretty print for readability
    $json = $json->pretty(1);

    return $json->encode($data);
}

1;
