package Feed::Util;
use strict;
use warnings;
use utf8;

use base 'Exporter';

our @EXPORT_OK = qw(get_text extract_text first_non_empty trim null_or_trim parse_xml_tree find_in_tree);

sub trim {
    my ($str) = @_;
    return undef unless defined $str;
    $str =~ s/^\s+//;
    $str =~ s/\s+$//;
    return $str;
}

sub null_or_trim {
    my ($str) = @_;
    my $trimmed = trim($str);
    return undef if !defined $trimmed || $trimmed eq '';
    return $trimmed;
}

sub first_non_empty {
    my (@values) = @_;
    for my $v (@values) {
        my $trimmed = trim($v);
        return $trimmed if defined $trimmed && $trimmed ne '';
    }
    return undef;
}

# Parse XML into tree structure using XML::Parser
sub parse_xml_tree {
    my ($xml) = @_;

    require XML::Parser;
    my $parser = XML::Parser->new(Style => 'Tree');
    my $tree = eval { $parser->parse($xml) };
    if ($@) {
        return (undef, $@);
    }
    return ($tree, undef);
}

# Find elements in tree by tag name
sub find_in_tree {
    my ($tree, $tag_name) = @_;

    my @results;
    my @stack = ($tree);

    while (@stack) {
        my $node = pop @stack;
        next unless ref $node eq 'ARRAY';

        # Skip first element if it's a hash (attributes)
        my $start_idx = 0;
        if (@$node && ref $node->[0] eq 'HASH') {
            $start_idx = 1;
        }

        # Structure: [attrs?, tag, content, tag, content, ...]
        # Where content can be text (scalar) or nested element (array)
        for (my $i = $start_idx; $i < $#$node; $i += 2) {
            my $tag = $node->[$i];
            my $content = $node->[$i + 1];

            next unless defined $tag && !ref $tag && $tag ne '0';

            if (lc($tag) eq lc($tag_name)) {
                push @results, $content;
            }

            # If content is an array, it might be a nested element (has attrs at [0])
            # or text content (has "0" at [1])
            if (ref $content eq 'ARRAY' && @$content >= 2) {
                # Check if it's a nested element (first elem is hash or string tag)
                my $first_elem = $content->[0];
                if (ref $first_elem eq 'HASH' || (defined $first_elem && !ref $first_elem && $first_elem ne '0')) {
                    push @stack, $content;
                }
            }
        }
    }

    return @results;
}

# Get text content from first matching element
sub get_text {
    my ($tree, $tag_name) = @_;

    my @matches = find_in_tree($tree, $tag_name);
    return undef unless @matches;

    # Content array: [attrs?, "0", text_value] OR [attrs?, tag, child_content, ...]
    my $content = $matches[0];
    return undef unless ref $content eq 'ARRAY';

    # Find text content marked with key '0'
    # Structure: [attrs_or_tag, value, ...] - need to check all consecutive pairs
    for (my $i = 0; $i < $#$content; $i++) {
        my $key = $content->[$i];
        my $value = $content->[$i + 1];

        # Text content has key '0'
        if (defined $key && $key eq '0' && defined $value && !ref $value) {
            return $value;
        }
    }

    return undef;
}

1;
