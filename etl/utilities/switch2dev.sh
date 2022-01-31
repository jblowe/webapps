#!/usr/bin/env bash
#
# a lil helper script to change the solr pipeline config to point to dev instead of prod and to
# send email notifications to Dev jblowe and not the various "real" addresses.
export DEVCONTACT="johnblowe@gmail.com"
cd
perl -i -pe 's/10.99.1.13/10.99.1.11/' solrdatasources/*/*.sh
perl -i -pe 's/CONTACT=.*/CONTACT="$ENV{"DEVCONTACT"}"/' solrdatasources/*/*.sh
