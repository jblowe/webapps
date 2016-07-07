@x = <STDIN>;
chomp @x;
$pattern = join '|',@x;

#for $z (@x) {print $z};
#print $pattern . "\n";

open(FH, "<", "omcainternalparms.csv");

while (<FH>) {
  s/field/#/ unless /$pattern/;
  print;
}
