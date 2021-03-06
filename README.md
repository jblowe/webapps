## Webapps being used by omca

There are two flavors:

* "Legacy Webapps" which run as a single Python CGI script, the main module is `cswaMain.py`
* "Django Webapps" which run under Apache/WSGI; OMCA currently uses a very slightly modify version of
the "standard" CollectionSpace webapps,
so that code is not here -- only the two modules that have customizations.

The following directories are found in this repo:

* `bmu` the two Django webapp modules that had to be customized for OMCA. I put them here rather than make an OMCA branch in the 'standard' repo. If further customization is needed, it might be wise to consider making and maintaining such a branch.
* `cfgs` configuration files for the Legacy Webapps, customized for OMCA
* `config` configuration files for the Django Webapps, customized for OMCA
* `cswa` Legacy Webapps code, customized for OMCA
* `docs` documentation for Legacy webapps (Django webapp documentation is available through OMCA staff -- it is a PDF that is too big to keep here)
* `etl` ETL scripts ("extract-transform-load" for the OMCA Simple and Advanced Search Portals

#### Legacy Webapp Installation

* Follow the instructions at: http://

#### Legacy Webapp Maintenance

If these very poorly-written and heavily-modified webapps need to be modified (to fix bugs or and features)
one can try the following:

1. Fork this repo and clone onto your local dev system.
1. Make the code modifications needed in your local system.
1. Commit the revisions to your GitHub repo.
1. Signin to Dev, clone your repo for deployment purposes, or, if you have it cloned already, `git pull` to ensure it is up to date.
1. Update the module or modules that need to be updated, e.g. `sudo cp cswa/cswaConstants.py /usr/lib/cgi-bin` or even `sudo cp cswa/*.py /usr/lib/cgi-bin`.
1. Start the legacy webapps, e.g. http://10.99.1.11/cgi-bin/cswaMain.py.
1. Verify the fix or fixes work. You may need to look in the Apache error log if you see errors. You may
need to check updates to records using the regular UI to see that the correct values appear.
1. Rinse and repeat from step 4. to deploy on Prod.

A couple of observations about this procedure:

* There is alas no good way to test the webapps in advance of deployment on a Dev server. You could `scp` the files to the Dev server and test them before committing them to GitHub (a hassle); or you could get the legacy webapps working on your own development system (also a hassle). You can at least check to see that they compile before committing or uploading them by executing them via the command line. If you have resolved the few dependencies on your local machine, they will at least compile and give a runtime error.
* If there are errors when deployed on dev, you'll need to check the Apache logs (e.g. `/var/log/apache2/error.log`) to see if any useful info can be found.
* Yes, as described, you'll need root privileges to maintain these apps. It _is_ possible to do all this with lesser privileges, and that would probably be a good idea to figure out how to do.

#### Django Webapp Installation

* Follow the instructions at: http://

#### Django Webapp Maintenance

* Hopefully, you will not need to change the code much. At the moment, only the
two modules in the `bmu` directory of this repo have been modified for OMCA. If the bug you find or enhancement you
make is relevant to all users of these webapps, consider forking the `cspace-deployment` repo and issuing a pull
request to contribute your change.
* Otherwise, the update procedure is the same as for any GitHub-based Django project:

1. Fork-and-clone https://github.com/cspace-deployment/cspace_django_project
1. Get the webapps working on your local system (see the instructions in the repo)
1. Repair the code (on a branch), commit to your fork
1. For OMCA, the current deployment of the code is from `cspace-deployment` so once you have gotten
your commit merged into this upstream repo, you can:
1. Login to the server (Dev or Prod)
1. cd /usr/local/share/django/omca
1. sudo git pull -v
1. if you have changed any static files: .js, .css, .html, etc.
1. sudo python manange.py collectstatic
1. restart Apache
1. sudo apachectl graceful

Note that if you can't get your changes into the upstream repo, you'll have to add your fork as a remote and update the running code (in `/usr/local/share/django/omca`) on Dev from your fork.
