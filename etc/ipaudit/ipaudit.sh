
time psql -F $'\t' -A -U reader_omca -d omca_domain_omca -f ipaudit.sql > ipaudit.csv
cut -f4 ipaudit.csv | sort | uniq -c > ipaudit.values.txt

perl -ne '@x=split /\t/;print if $x[3] eq ""' ipaudit.csv > ipaudit.blank.csv
perl -ne '@x=split /\t/;print if $x[3] eq "Assumed Protected by Copyright"' ipaudit.csv > ipaudit.Assumed_Protected_by_Copyright.csv
perl -ne '@x=split /\t/;print if $x[3] eq "Copyright OMCA"' ipaudit.csv > ipaudit.Copyright_OMCA.csv
perl -ne '@x=split /\t/;print if $x[3] eq "In Copyright"' ipaudit.csv > ipaudit.In_Copyright.csv
perl -ne '@x=split /\t/;print if $x[3] eq "No Known Restrictions"' ipaudit.csv > ipaudit.No_Known_Restrictions.csv
perl -ne '@x=split /\t/;print if $x[3] eq "OMCA Licensed"' ipaudit.csv > ipaudit.OMCA_Licensed.csv
perl -ne '@x=split /\t/;print if $x[3] eq "Protected by Copyright"' ipaudit.csv > ipaudit.Protected_by_Copyright.csv
perl -ne '@x=split /\t/;print if $x[3] eq "Public Domain"' ipaudit.csv > ipaudit.Public_Domain.csv

tar czvf ipa.tgz ipaudit.*
mv ipa.tgz ipaudit.tgz
cp ipaudit.tgz /var/www/html/
tar --list -f ipaudit.tgz

