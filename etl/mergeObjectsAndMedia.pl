use strict;

my %count ;
my $delim = "\t";

open MEDIA,$ARGV[0] || die "couldn't open media file $ARGV[0]";
open METADATA,$ARGV[1] || die "couldn't open metadata file $ARGV[1]";
open HIRESURLS,$ARGV[2] || die "couldn't open hires media file $ARGV[2]";

warn join("\n",@ARGV);

my $CDN_PATH = $ARGV[3] ;
my %media ;
my %externalurls ;

while (<HIRESURLS>) {
  $count{'hires'}++;
  chomp;
  my ($filename) = split /$delim/;
  (my $objectnumber = $filename) =~ s/_.*//;
  # warn $filename,$objectnumber;
  $externalurls{$objectnumber} = "$CDN_PATH/$filename.jpg" ;
}

while (<MEDIA>) {
  $count{'media'}++;
  chomp;
  my ($objectcsid, $objectnumber, $mediacsid, $description, $filename, $creatorrefname, $creator, $blobcsid, $copyrightstatement, $identificationnumber, $rightsholderrefname, $rightsholder, $contributor, $approvedforweb, $imageType, $md5, $blob_length) = split /$delim/;
  #print "$blobcsid $objectcsid\n";
  $media{$objectcsid} .= $blobcsid . ',';
}

while (<METADATA>) {
  $count{'metadata'}++;
  chomp;
  my ($id, $objectid, @rest) = split /$delim/;
  my $objectnumber = $rest[1];
  my $ipstatus = $rest[19];
  # insert list of blobs as final column
  my $mediablobs = $media{$objectid};
  $count{'metadata matches'}++ if $externalurls{$objectnumber};
  my $externalurl = $externalurls{$objectnumber} ;
  my $has_images;
  my $public_domain;
  if ($mediablobs) {
    $count{'matched'}++;
    $has_images = 'Yes';
  }
  else {
    $count{'unmatched'}++;
    # insert csid of placeholder image
    $mediablobs = '196276ae-9619-4dc5-91b8';
    $has_images = 'No';
  }
  # print "$objectnumber: $ipstatus\n";
  if ($ipstatus =~ /(Public Domain|No Copyright)/i) {
    $count{'public domain: Yes'}++;
    $public_domain = 'Yes';
  }
  else {
    $count{'public domain: No'}++;
    $public_domain = 'No';
  }
  # insert column headers for the four fields being added
  if ($count{'metadata'} == 1) {
    $mediablobs = 'blob_ss';
    $externalurl = 'externalurl_s';
    $has_images = 'has_images_s';
    $public_domain = 'public_domain_s';
  }
  $mediablobs =~ s/,$//; # get rid of trailing comma
  print $_ . $delim . $public_domain . $delim . $has_images . $delim . $mediablobs . $delim . $externalurl . "\n";
}

foreach my $s (sort keys %count) {
 warn $s . ": " . $count{$s} . "\n";
}
