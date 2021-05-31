@tags = split('\|','supportsDocList|supportsNoContext|outputMIME|name|filename|supportsGroup|supportsSingleDoc|forDocType|updatedAt|createdAt|uri');

while (<>) {
   chomp;
   $x = $_;
   for $t (@tags) {
      if (/<$t>/) {
        chomp;
        s/<.*?>//g;
        s/^\s+(.*?)/\1/;
        $vals{$t} = $_;
      }
   }
}
for $t (@tags) {
   print $vals{$t} . "\t";
}
print "\n";

