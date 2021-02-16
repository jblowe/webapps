The fixtures used for this project contain the content shown in the various "nav bar" items of the various apps.

Each app has 0 or more items; these can be managed (edited and organized) using the Django admin interface, available if
you are logged in.
  
Note that if changes are made online to the content of an item, steps may need to be taken to preserve those changes
when the project is updated: normally, the project update scripts (i.e. "deployment scripts") reload the fixture from
whatever is checked in to GitHub.

Below is a conversation that shows how to preserve changes to the nav items:

"""
# login to target server
$ ssh ...

# become webapp user
$ sudo su - ...
(venv)$ cd /var/www/omca
# dump the database table corresponding to the app of interest to the appropriate json file
(venv) $ python manage.py dumpdata --format=json search | python -mjson.tool > fixtures/search.json
# since we don't check in changes from deployed code, we need to move the file(s) to our local machine to
# check it into github. We do this by copying the file(s) first to /tmp so we can get to them from our developer account
(venv) $ cp fixtures/*.json /tmp

# Now, on our local machine:
$ cd ..../<project>/fixtures
fixtures $ scp [server]:/tmp/*.json .
internal.json                                                                  100%  472     0.5KB/s   00:00    
search.json                                                                    100%   10KB  10.1KB/s   00:01    
toolbox.json                                                                   100% 7590     7.4KB/s   00:00    
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

	modified:   search.json

# commit and push the changes
fixtures $ git commit -a -m "omca-1337: capture updates to Help tab for search webapp"
fixtures $ git push -v
"""
