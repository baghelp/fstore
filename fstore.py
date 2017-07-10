#!/usr/bin/python

# Simple Flickr folder uploader
# Author: baghelp <ankmike5@gmail.com>
# Heavily based on <https://github.com/alfem/synology-flickr-folder-uploader>

import flickrapi
import os
import sys
import argparse
import time
from shutil import copyfile

# Get an api key and secret: https://www.flickr.com/services/apps/create/apply
# Put those values in these variables
API_KEY = "b164a21528285942966a9d5779c5cfc9"
API_SECRET = "58ad8ff08f9b3cc7"

# Start this script. First time it shows an URL. Open it with your browser and
# authorize the script. Once authorized, script will store a token in user home
# directory. Change it if desired:
TOKEN_CACHE='./token'

global flickr
flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET, token_cache_location=TOKEN_CACHE)
global default_video
dirpath = os.path.dirname(os.path.realpath(__file__))
default_video = dirpath + "/" + "default.wmv"


def checkToken():
  global flickr
  if not flickr.token_valid(perms='write'):
      print "Authentication required"

      # Get request token
      flickr.get_request_token(oauth_callback='oob')

      # Show url. Copy and paste it in your browser
      authorize_url = flickr.auth_url(perms=u'write')
      print(authorize_url)

      # Prompt for verifier code from the user 
      verifier = unicode(raw_input('Verifier code: '))

      print "Verifier:", verifier

      # Trade the request token for an access token
      print(flickr.get_access_token(verifier))

#Driver script
#-------------
def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("path", help="path to download location of upload" +
                      " target")
  parser.add_argument("-t", "--tags",
                      help="One or more tags for all the files (use quotes if" +
                      " needed). Not used if downloading")
  parser.add_argument("-f", "--failed",
                      help="Only upload files if they previously failed to " +
                      "upload. Not used if downloading",
                      action="store_true")
  parser.add_argument("-i", "--ignore-failure",
                      help="delete files after upload is attempted, even if " +
                      "they are not uploaded successfully. Not used if "+
                      "downloading", action="store_true")
#parser.add_argument("-f", "--file", help="upload or download a file")
  parser.add_argument("-r", "--recursive",
                      help="upload or download a directory",
                      action="store_true")
#parser.add_argument("-u", "--upload", help="upload a file or directory",
#upload=True)
  parser.add_argument("-d", "--download",
                      help="download a file or directory")#, action="store_true")
  parser.add_argument("-v", "--verbose",
                      help="print filenames as they are uploaded",
                      action="store_true")
  parser.add_argument("-n", "--name",
                      help="Name of the set (use quotes if needed). Not used if"+
                      " downloading")
  params=parser.parse_args()

  checkToken()
  if params.download:
    print("downloading  something")
    if not params.recursive:
      x = 1
      #download a file
    else:
      x = 1
      #download a directory
    #TODO: write method for downloading
  else:
    #uploading something
    if params.name:
      TITLE=params.name
    else:
      TITLE=os.path.basename(os.path.normpath(params.path))
    if params.recursive:
      #upload a directory
      FOLDER=os.path.abspath(params.path)+"/"
      upload_dir(FOLDER, TITLE, params.tags, params.verbose)
    else:
      #upload a file
      FILE=os.path.abspath(params.path)
      upload_file(FILE, TITLE, params.tags, params.verbose)


def upload_dir(FOLDER, TITLE, tags, verbose):
  global default_video
  if tags:
    TAGS=tags
  else: 
    TAGS="uploaded on " + time.strftime("%d/%m/%Y")
  if verbose:
    print "Uploading", FOLDER, "to", TITLE, "with tags:", TAGS
  params = {}
  params['tags']=TAGS
  photo_ids=[]

  for filename in os.listdir(FOLDER):
      filename_split = filename.split('.')

      if len(filename_split) == 2:
          ext = filename_split[1].lower()
      else:
          ext = ''
      if ext not in ['png', 'jpeg', 'jpg', 'avi', 'mp4', 'gif', 'tiff', 'mov',
        'wmv', 'ogv', 'mpg', 'mp2', 'mpeg',
        'mpe', 'mpv']:
        #file needs to be padded and extension added
        copyfile(default_video, filename+'.wmv')
        f = open(filename + '.wmv', 'a')
        curr_file = open( FOLDER + filename, 'r')
        f.write(curr_file.read())
        f.close()
        curr_file.close()
        dirpath = os.path.dirname(os.path.realpath(__file__))
        full_filename = dirpath + '\\' + filename + '.wmv'
      else:
        #file is already a picture or a video
        full_filename = FOLDER + filename


      if verbose:
        print(filename),
        print(" -- uploading..."),

      print(full_filename)

      try:
          uploadResp = flickr.upload(filename=full_filename, is_public=0, is_friend=0, is_family=1, tags=TAGS)
          photo_id = uploadResp.findall('photoid')[0].text
          if verbose:
            print(' OK. Flickr id = ' + photo_id)
          photo_ids.append(photo_id)
      except:
          if verbose:
            print(" ERROR.")
          #TODO: log errors somewhere

  # Creating a set
  try:
      if verbose:
        print "Creating set",TITLE,
      resp = flickr.photosets.create(title=TITLE,primary_photo_id=photo_ids[0])
      photoset_id = photoset_id = resp.findall('photoset')[0].attrib['id']
      if verbose:
        print(' OK. Set id = ' + photoset_id)
      del photo_ids[0]
  except:
      if verbose:
        print "ERROR."
      sys.exit(4)

  for photo_id in photo_ids:
      try:
          resp = flickr.photosets.addPhoto(photoset_id=photoset_id,photo_id=photo_id)
      except:
          if verbose:
            print "ERROR adding file to set", photo_id

main()
