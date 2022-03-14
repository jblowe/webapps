echo "Use of webapps (log analysis) `date`" > /var/www/html/webapps.txt
echo "" >> /var/www/html/webapps.txt
echo "`wc -l access.log` log records found" >> /var/www/html/webapps.txt
echo "" >> /var/www/html/webapps.txt
cut -f4 access.log -d" " | cut -c2-12 | sort -k3 -k2M -k1 -t '/' | head -1 >> /var/www/html/webapps.txt
cut -f4 access.log -d" " | cut -c2-12 | sort -k3 -k2M -k1 -t '/' | tail -1 >> /var/www/html/webapps.txt
echo "" >> /var/www/html/webapps.txt
cut -f6-8 -d " " access.log | perl -pe 's/"//g;s#(.*?/.*?/.*?)[/\?].*#\1#;s/ HTTP.*//' | sort | uniq -c | sort -rn >> /var/www/html/webapps.txt
