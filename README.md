## Webapps being used by omca

The "Django Webapps" run under Apache/WSGI; OMCA currently uses a slightly customized version of
the "standard" CollectionSpace webapps, this repo only contains those customizations, which are applied
"on top of" the standard codebase.

The following directories are found in this repo:
* `docs` documentation for Legacy webapps (Django webapp documentation is available through OMCA staff -- it is a PDF that is too big to keep here)
* `etc` various ad hoc and helper code: fix dups, merge authority terms, etc.
* `etl` Solr ETL scripts ("extract-transform-load") for the OMCA Simple and Advanced Search Portals
* `omca` the customized code and config files for the Django webapps. This directory contains:
  * `apps` customized applications
  * `config` configuration files for the Django Webapps, customized for OMCA
  * `fixtures` text content of various helpers
* `legacy` Legacy Webapps code, customized for OMCA, pre-ubuntu 18 version. For reference only!
  * `bmu` the two Django webapp modules that had to be customized for OMCA. I put them here rather than make an OMCA branch in the 'standard' repo. If further customization is needed, it might be wise to consider making and maintaining such a branch.
  * `cfgs` configuration files for the Legacy Webapps, customized for OMCA
  * `cswa` original CGI webapp code

#### Webapp Installation

* Documented in Google Docs. Consult OMCA staff for access

#### Webapp Maintenance

* Hopefully, you will not need to change the code much. 
If the bug you find or enhancement you
make is relevant to all users of these webapps, consider forking the `cspace-deployment` repo and issuing a pull
request to contribute your change.
* Otherwise, the update procedure is the same as for any GitHub-based Django project:

1. Fork-and-clone https://github.com/OaklandMuseum/webapps
2. Get the webapps working on your local system (see the instructions in the repo)
3. Repair the code (on a branch), commit to your fork
4. For OMCA, the current deployment of the code is from `jblowe` so once you have gotten
your commit merged into this upstream repo, you can:
5. Login to the server (Dev or Prod)
6. `cd ~webapps/webapps`
7. `sudo git pull -v`
8. ... follow instructions in Google Docs
9. `exit`
10. restart Apache as your own (super)user:
`sudo apachectl graceful`

Note that if you can't get your changes into the upstream repo, you'll have to add your fork as a remote and update the running code (in `/usr/local/share/django/omca`) on Dev from your fork.
