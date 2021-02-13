#### How to setup and maintain OMCA Solr cores

This setup structure support multiple cores for the OMCA deployments.

The current scheme (February 2021) uses Solr8 and the 'managed-schema' approach.

The files in this directory are used to build the needed POSTs to the Solr schema API
to create the required fields.

Each *.fields.txt file contains the dynamic fields loaded into the Solr; from this list
a set of <copyField> statements is created to generate a corresponding keyword (*_txt) field.
(The _txt version is needed to support keyword searching in the Portals.)

2 cores are currently being maintained for the CSpace@OMCA deployment.

To create and maintain these cores, the following scripts are useful:

* *.fields.txt -- list of fields being extracted in the Solr pipelines.
* makecores.sh -- script to create and populate the cores based on *.fields.txt

Some examples of running the scripts, etc. to make this go (on RTL servers):

```
# starting and stopping the Solr server
user@blacklight-dev:~$ sudo /bin/systemctl start solr.service
user@blacklight-dev:~$ sudo /bin/systemctl stop solr.service

# delete a single core
/opt/solr/bin/solr delete -c omca-public

# delete and recreate both cores
cd ~/webapps/etl
nohup time ./makesolrcores.sh > cores.log 2> /dev/null &

# recreate a single core
cd ~/webapps/etl
./makesolrcores.sh omca-public
```

After this finishes, you'll need to reload all the cores with fresh data.
This is most easily accomplished by rerunning the "solr pipelines"

See the Solr pipeline documentation: [README.md](../README.md)
