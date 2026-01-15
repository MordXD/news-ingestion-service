package Feed::Parser;
use strict;
use warnings;
use utf8;

use Feed::Util qw(parse_xml_tree get_text);
use Feed::Parser::RSS;
use Feed::Parser::Atom;

sub parse {
    my ($xml) = @_;

    my ($tree, $error) = parse_xml_tree($xml);
    if ($error) {
        return (undef, "XML parse error: $error");
    }

    # Tree structure: [root_tag, [attrs, content...]]
    my $root_tag = $tree->[0];

    if (lc($root_tag) eq 'rss') {
        my $data = Feed::Parser::RSS::parse($tree);
        return ({ type => 'rss', %$data }, undef);
    }
    elsif (lc($root_tag) eq 'feed') {
        my $data = Feed::Parser::Atom::parse($tree);
        return ({ type => 'atom', %$data }, undef);
    }
    else {
        return (undef, "Unsupported feed format: $root_tag");
    }
}

1;
