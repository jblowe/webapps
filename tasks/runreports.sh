#!/bin/bash
#
# ad hoc apparatus used to support 'booklets.task'
#
# this script must be in /home/webapps/RunJasperReports (along with all the other required stuff...)
# steps to set this 'standalone jaspersoft report hack':

# login to suitable account (e.g. ~webapps -- sql setup and java jdk)
# git clone https://github.com/okohll/RunJasperReports.git
# mkdir ~/jasperreports
# cp ~/webapps/tasks/runreports.sh ~/RunJasperReports/run.sh
#
# NB: password for dbuser 'reader_omca' needs to be in env. var DB_CSPACE_PASSWORD
#
# that should do it
#
source /home/webapps/.profile
set -x
time java -jar /home/webapps/RunJasperReports/RunJasperReports.jar \
-dbhost localhost -dbname omca_domain_omca -dbuser reader_omca -dbpass "${DB_CSPACE_PASSWORD}" -dbtype postgresql \
-folder /home/webapps/jasperreports -output pdf \
-reports "/home/webapps/webapps/reports/jrxml/$1" \
"$2"
