package Feed::Normalizer;
use strict;
use warnings;
use utf8;

use Feed::Util qw(null_or_trim);

sub normalize {
    my ($data) = @_;

    my $type = $data->{type};
    my $raw_feed = $data->{feed};
    my $raw_items = $data->{items} || [];

    my $normalized = {
        type  => $type,
        feed  => _normalize_feed($raw_feed),
        items => [ map { _normalize_item($_) } @$raw_items ],
    };

    return $normalized;
}

sub _normalize_feed {
    my ($raw) = @_;

    return {
        title       => null_or_trim($raw->{title}),
        link        => null_or_trim($raw->{link}),
        description => null_or_trim($raw->{description}),
    };
}

sub _normalize_item {
    my ($raw) = @_;

    return {
        id        => null_or_trim($raw->{id}),
        title     => null_or_trim($raw->{title}),
        link      => null_or_trim($raw->{link}),
        summary   => null_or_trim($raw->{summary}),
        content   => null_or_trim($raw->{content}),
        published => null_or_trim($raw->{published}),
    };
}

1;
