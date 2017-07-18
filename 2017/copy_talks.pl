#!/usr/bin/env perl

use 5.016;
use strict;
use warnings;

use Text::CSV_XS;
use File::Copy;
use File::Spec;

#my $csv = Text::CSV_XS->new({sep_char => "\t"});

my $file = shift;

open(my $fh, '<', $file) or die "Couldn't open file: $!";

my $talkdir = 'Talks';

if (! -e $talkdir) {
    mkdir $talkdir;
}

while (my $line = <$fh>) {
    next if $line  =~ /^#/;
    chomp $line;
    #say $line;
    my ($abstract, $day, $talk, $poster, @rest) = split("\t", $line);

    next unless $talk;
    my $from = "BOSC_2017_paper_${abstract}.pdf";

    if (! -e $from) {
        die "Can't find PDF $from";
    }

    my $to = "$talk.pdf";

    my $daydir = "Day_$day";

    my $path = File::Spec->catdir($talkdir, $daydir);
    if ( ! -e $path ) {
        mkdir $path;
    }

    my $filepath = File::Spec->catfile($talkdir, $daydir, $to);
    say "Copying from $from to $filepath";
    File::Copy::cp($from, $filepath);
}
