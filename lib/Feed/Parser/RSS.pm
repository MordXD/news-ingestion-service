package Feed::Parser::RSS;
use strict;
use warnings;
use utf8;

use Feed::Util qw(get_text find_in_tree first_non_empty);

sub parse {
    my ($tree) = @_;

    # Find channel element
    my @channels = find_in_tree($tree, 'channel');
    return { feed => {}, items => [] } unless @channels;

    my $channel = $channels[0];

    my $feed = {
        title       => get_text($channel, 'title'),
        link        => get_text($channel, 'link'),
        description => get_text($channel, 'description'),
    };

    # Find all items - can be directly in rss or in channel
    my @items;
    my @item_trees = find_in_tree($channel, 'item');

    for my $item_tree (@item_trees) {
        my $item = {
            id        => first_non_empty(get_text($item_tree, 'guid'), get_text($item_tree, 'link')),
            title     => get_text($item_tree, 'title'),
            link      => get_text($item_tree, 'link'),
            summary   => get_text($item_tree, 'description'),
            content   => get_text($item_tree, 'content:encoded'),
            published => get_text($item_tree, 'pubDate'),
        };
        push @items, $item;
    }

    return {
        feed  => $feed,
        items => \@items,
    };
}

1;
