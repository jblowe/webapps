use strict;
use Text::CSV;
use open ':std', ':encoding(UTF-8)';

my %count ;
my $delim = ",";

my $csv = Text::CSV->new({ binary => 1, sep_char => $delim, eol => "\n" })
  or die "cannot create Text::CSV object: " . Text::CSV->error_diag();

open MEDIA,'<:encoding(UTF-8)',$ARGV[0] || die "couldn't open media file $ARGV[0]";
open METADATA,'<:encoding(UTF-8)',$ARGV[1] || die "couldn't open metadata file $ARGV[1]";
open HIRESURLS,'<:encoding(UTF-8)',$ARGV[2] || die "couldn't open hires media file $ARGV[2]";

warn join("\n",@ARGV);

my $CDN_PATH = $ARGV[3] ;
my %media ;
my %externalurls ;

while (my $row = $csv->getline(\*HIRESURLS)) {
  $count{'hires'}++;
  my ($filename) = @$row;
  (my $objectnumber = $filename) =~ s/_.*//;
  # warn $filename,$objectnumber;
  $externalurls{$objectnumber} = "$CDN_PATH/$filename.jpg" ;
}

while (my $row = $csv->getline(\*MEDIA)) {
  $count{'media'}++;
  my ($objectcsid, $objectnumber, $mediacsid, $description, $filename, $creatorrefname, $creator, $blobcsid, $copyrightstatement, $identificationnumber, $rightsholderrefname, $rightsholder, $contributor, $approvedforweb, $imageType, $md5, $blob_length) = @$row;
  #print "$blobcsid $objectcsid\n";
  $media{$objectcsid} .= $blobcsid . ',';
}

while (my $row = $csv->getline(\*METADATA)) {
  $count{'metadata'}++;
  my ($id, $objectid, @rest) = @$row;
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
  $csv->say(\*STDOUT, [$id, $objectid, @rest, $public_domain, $has_images, $mediablobs, $externalurl]);
}

foreach my $s (sort keys %count) {
 warn $s . ": " . $count{$s} . "\n";
}
