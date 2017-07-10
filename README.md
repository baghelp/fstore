# fstore
Simple script to upload files or directories to flickr, by appending them to a
photo or video file

This tool is very heavily based on alfem's https://github.com/alfem/synology-flickr-folder-uploader


---STILL UNDER CONSTRUCTION---

      ---DO NOT USE!!!---

# Installation 

* Create a folder for the flickr api

  mkdir api

* Set python to use that folder

  export PYTHONPATH=/var/services/homes/admin/api

* Install the flickr api

  easy_install  --install-dir=/var/services/homes/admin/api flickrapi

* Download the script (use your favourite browser, or wget command in your Synology)

  wget https://raw.githubusercontent.com/baghelp/fstore/master/fstore.py
 
* Give it execution permissions

  chmod u+x fstore.py

* Create a new app in your Flickr account: https://www.flickr.com/services/apps/create/apply and jot down api_key and api_secret
* Edit the script and adjust the api_key, api_secreet and paths at the begining
* Run it!

  ./fstor.py /volume1/alfem/Pics/Coches/ coches

  First parameter = Folder to upload
  
  Second parameter = Tag for the photos 

* On first run, the script will show an URL you need to visit in order to authorize it. Open the url in your brwoser, authorize the script and copy the code shown.   

You can install the api system wide and avoid setting the PYTHONPATH, but I prefer to keep my system clean.

