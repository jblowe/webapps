set -x
time java -jar /home/webapps/RunJasperReports/RunJasperReports.jar \
-dbhost localhost -dbname omca_domain_omca -dbuser reader_omca -dbpass "${DB_CSPACE_PASSWORD}" -dbtype postgresql \
-folder /home/webapps/jasperreports -output pdf \
-reports "/home/webapps/webapps/reports/jrxml/$1" \
"$2"

# this script runs a jaspersoft report on the omca production server and puts the result pdf
# in the webapps users 'jasperreports' directory.
# it uses an open source repo to execute the jrxml file:
# https://github.com/okohll/RunJasperReports.git
# to deploy, clone the repo, follow the instructions and place this script in the directory
# the other bit of magic required is the taskrunner webapp task called 'booklets.task'
# which runs all the booklets reports and makes the result available via the web
# i.e. it places the pdfs in /var/www/html/reports where they can be retrived by
# anyone who can access that apache directory (i.e. who can log in via the vpn)
