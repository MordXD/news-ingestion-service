#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use 5.010;

use FindBin;
use lib "$FindBin::Bin/lib";

use Feed::App;

binmode(STDOUT, ':utf8');
binmode(STDERR, ':utf8');

my $url = shift @ARGV;

if (!$url) {
    print STDERR "Usage: $0 <feed_url>\n";
    exit 2;
}

my $app = Feed::App->new();
my ($result, $error) = $app->run($url);

if ($error) {
    print STDERR "$error\n";
    exit 1;
}

print "$result\n";
exit 0;
