set -x
time java -jar /home/webapps/RunJasperReports/RunJasperReports.jar \
-dbhost localhost -dbname omca_domain_omca -dbuser reader_omca -dbpass "${DB_CSPACE_PASSWORD}" -dbtype postgresql \
-folder /home/webapps/jasperreports -output pdf \
-reports "/home/webapps/webapps/reports/jrxml/$1" \
"$2"
