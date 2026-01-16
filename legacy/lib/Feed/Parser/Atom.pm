package Feed::Parser::Atom;
use strict;
use warnings;
use utf8;

use Feed::Util qw(get_text find_in_tree first_non_empty);

sub parse {
    my ($tree) = @_;

    # The feed is the root element's content
    my $feed_tree = $tree->[1];

    my $feed = {
        title       => get_text($feed_tree, 'title'),
        link        => _get_main_link($feed_tree),
        description => get_text($feed_tree, 'subtitle'),
    };

    my @items;
    my @entries = find_in_tree($feed_tree, 'entry');

    for my $entry (@entries) {
        my $item = {
            id        => get_text($entry, 'id'),
            title     => get_text($entry, 'title'),
            link      => _get_entry_link($entry),
            summary   => get_text($entry, 'summary'),
            content   => get_text($entry, 'content'),
            published => first_non_empty(
                get_text($entry, 'published'),
                get_text($entry, 'updated')
            ),
        };
        push @items, $item;
    }

    return {
        feed  => $feed,
        items => \@items,
    };
}

sub _get_main_link {
    my ($tree) = @_;
    return _find_link($tree);
}

sub _get_entry_link {
    my ($tree) = @_;
    return _find_link($tree);
}

sub _find_link {
    my ($tree) = @_;

    my @links = find_in_tree($tree, 'link');

    # First try alternate
    for my $link (@links) {
        next unless ref $link eq 'ARRAY';
        my $attrs = $link->[0];
        next unless ref $attrs eq 'HASH';

        my $rel = $attrs->{rel} || '';
        my $href = $attrs->{href};
        if ($rel eq 'alternate' && $href) {
            return $href;
        }
    }

    # Then no rel
    for my $link (@links) {
        next unless ref $link eq 'ARRAY';
        my $attrs = $link->[0];
        next unless ref $attrs eq 'HASH';

        my $rel = $attrs->{rel} || '';
        my $href = $attrs->{href};
        if (!$rel && $href) {
            return $href;
        }
    }

    # Fallback to first available
    for my $link (@links) {
        next unless ref $link eq 'ARRAY';
        my $attrs = $link->[0];
        next unless ref $attrs eq 'HASH';

        my $href = $attrs->{href};
        return $href if $href;
    }

    return undef;
}

1;
