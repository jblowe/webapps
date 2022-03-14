sort -u /tmp/access.log | grep -v "Auvik HTTP Monitor" > tmp1.log
sort -m -u tmp1.log access.log > tmp2.log
mv tmp2.log access.log
rm tmp1.log

