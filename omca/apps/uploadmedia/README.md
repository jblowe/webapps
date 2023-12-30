## Deploying and Configuring the Bulk Media Uploader (BMU)

This webapp and its associated "batch processes" provide a means to upload multiple media files
in one fell swoop and (optionally, provided the media files are appropriately names) relate the media
files to object records

The BMU uses the "standard" multi-file upload capability provided by most
HTTP client framework to allow users to upload batches of images and
provide associated metadata. 

BMU has two components, one online, one "offline":

* A django webapp that allows users to upload media (via the
  "standard" Django file upload components) and metadata (via a
  combination of form input and metadata in the EXIF data in the
  image.)

* A batch component consisting of shell and python scripts, which takes
  the uploaded images and metadata and "ingests" them into CSpace.

To deploy it on an IS&T Unix Team-managed server, (A RHEL6 VM, e.g. cspace-prod.cspace.berkeley.edu):

### WEBAPP COMPONENT:

* Clone this repo and install and configure the Django
  webapp(s), including this one, "as usual" (see the README.md for the Django project, one level up).

  In particular, edit ```uploadmedia.cfg``` to point to the temporary cache,
  which you will need to create and perhaps set permissions and SELinux tags for
  (this directory needs to be writable by the Apache server, and at UCB, the WSGI
  process which the webapps run under is owned by the application owner "app_webapps"). 
 
  `/tmp` is usually a good place to put this cache. At UCB, the caches are all
  of the form `/tmp/image_upload_cache_<name of tenant>`
 
  Record the full path in `[files]` section of `uploadmedia.cfg`

  e.g.
```
  [files]
  directory         = /tmp/image_upload_cache_pahma
```

   `uploadmedia.cfg` is also where you will configure tenant specific media handling
   options. These can get pretty complicated, so study the existing UCB
   configurations and associated JIRAs to understand how they work. 
   
   Alas, the ability to configure dropdowns with specific attributes and values 
   is limited, and the BMU code itself contains a number of tenant-specific
   code blocks that you may need to modify to get the effect you want.

### BATCH COMPONENT:

* Follow these steps to configure the batch component to run in
  the environment you are using: the batch component relies on cron or
  something similar to run, and has a number of expectations (dependencies)
  about where things are located and what they are named.
  Sorry it is so complicated, someday we'll make it more robust.

* The BMU batch job processes the files in the temporary cache (where the webapp put them). These
  files consist of jobs files (in .csv format) and the images themselves.

* This batch script does not require editing: all parameters are passed on the command line.

* Ensure that the temporary cache for images and intermediate files is
  present and properly configured with appropriate permissions. For the
  online portion, the current setting is `/home/webapps/bmu`.

```
(venv) webapps@cspace1804:~$ cat /var/www/omca/config/uploadmedia_batch.cfg 
# this is the config file for the batch component of the BMU
# the online portion (i.e. the webapp) is a Django webapp and is configured with
# those webapps
[info]

... snip

[files]
directory         = /home/webapps/bmu
```

* Alas, there is no way to test this webapp except to upload some
  media files and see what happens.

* There are some helper scripts: "runJob.sh" runs a single job from
  the command line. "runHelpers.sh" attempts to find problem media and
  create jobs to re-load/re-link them. Both of these would need to be
  tweaked to be used with OMCA media.

* The batch portion of the system is run via cron, and apache owns the
  uploaded files so it has to be run as use apache.  And there is a
  script that reports on the status of uploads that runs via cron as
  well.

  Here is the part of the current crontab for user webapps on the OMCA production server, where the batch process run nightly:

```
(venv) webapps@cspace1804:~$ crontab -l

[...]

###################################################################################
## BMU monitoring / report (i.e. send nightly emails) as 5:10 am
###################################################################################
10 05 * * * python3 /var/www/omca/uploadmedia/checkRuns.py /home/webapps/bmu jobs summary | expand -12 > /var/www/html/bmu.txt
##################################################################################
# clean up the BMU temp directories (erase images more than 48 hours old)
##################################################################################
01 04 * * * /home/webapps/webapps/etc/cleanBMUtempdir.sh /home/webapps/bmu >> /home/webapps/bmu_cleanup.log
```

A few more details on the batch process:

The "batch process", which runs nightly (or more frequently) as a cron job as shown above,
is really just a small bash script wrapper around a python script
(uploadMedia.py) that does the heavy lifting. The heavy lifting is as
follows:

* The webapp creates metadata files (*.step1.csv) in a temp directory.
  These point to the media files that were uploaded via the webapp to
  the same temp directory. (the directory is a config parameter to the
  webapps, see above.)

* Every night, cron globs all the *.step1.csv files together, passes
  the list of files to uploadMedia.py, which POSTs to the Blob, Media and
  Relations services to create Blobs and Media records and connect them to the
  corresponding Collectionobjects (if needed).

* In more detail:

- the shell script postblobs.sh processes a file (*.step1.csv) which is a
  list of image filenames and metadata. It calls the python script uploadMedia.py
  which POSTs to the Blob service to create blobs, then POSTs to the
  Media service, outputting a file *.step3.csv for every successful
  Media (and making bidirectional Relation if collectionobjects are involved.)

- Finally the bash script renames the *.step*.csv file to
  *.original.csv and *.processed.csv. This creates a trace for
  verification and prevents the images from being reprocessed the next
  time the cron job runs.

As an aside, note that this tmp/ directory is cleaned up by a script cleanBMUtempdir.sh,
which deletes files older than 48 hours -- i.e. there is a 2 day cache
of images load, in case something needs to be recovered or rerun. The various
"control files" (.csv and .log) are kept around forever.

Finally, there are a few other (very speculative!) scripts that are
used for reporting and maintenance:

* bulkmediaupload.sh - this runs a single *.step1.csv file; it can be used 
to run a specific upload "by hand" from the command line.

* checkObj.pl - this script checks Blobs uploaded vs. Media created; it
is used by the very rickety "runHelpers.sh" script below to report on
problem records.

* checkRuns.pl - this script creates some reports on BMU activity:
number of jobs and their status, lists of images and the CSIDs, finds
problem data (missing images, duplicates, etc.)

* runHelpers.sh - matches CSIDs loaded with log files, to find
discrepancies between what is in the database and what seems to have
been uploaded. No longer works due to schema changes in the Solr
datasource, which it uses to find Blob CSIDs.

* runJob.sh - like bulkmediaupload.sh, but does not cleanup/rename
intermediate files.

* verifyObjectsAndMedia.sh - somewhat scary script to make a list of
imagefile names and object numbers...

### RUNNING THE BMU FROM THE COMMAND LINE

Once it is installed, the BMU can be invoked on the command line on one of the manage servers as follows:

```
$ ssh 10.xx.xx.xx
$ sudo su - webapps
$ /var/www/omca/uploadmedia/postblob.sh /home/webapps/bmu/xxxxxx.step1.csv
```

Provide `xxxxxx.step1.csv` exists and correctly references images in the same diretory, you should get some output.
