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
TEMP_FOLDER = "/home/baghelp/fstoreTempFiles/"

# Start this script. First time it shows an URL. Open it with your browser and
# authorize the script. Once authorized, script will store a token in user home
# directory. Change it if desired:
TOKEN_CACHE='./token'

global flickr
flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET, token_cache_location=TOKEN_CACHE)
scriptdirpath = os.path.dirname(os.path.realpath(__file__))
global dummy_video
dummy_video = scriptdirpath + "/" + "default.mp4"


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
  parser.add_argument("path", help="path to files to be uploaded")
  parser.add_argument("-t", "--tags",
                      help="One or more tags for all the files (use quotes if" +
                      " needed). Not used if downloading")
  parser.add_argument("-s", "--set",
                      help="Name of the set (use quotes if needed). Not used if"+
                      " downloading")
  parser.add_argument("-x", "--delete-files",
                      help="delete files that are uploaded successfully", 
                      action="store_true")
  parser.add_argument("-i", "--ignore-failure",
                      help="delete files after upload is attempted, even if " +
                      "they are not uploaded successfully. Not used if "+
                      "downloading", action="store_true")
#parser.add_argument("-f", "--file", help="upload or download a file")
  parser.add_argument("-r", "--recursive",
                      help="upload or download a directory",
                      action="store_true")
  parser.add_argument("-f", "--failed",
                      help="Only upload files if they previously failed to " +
                      "upload. Not used if downloading",
                      action="store_true")
  parser.add_argument("-v", "--verbose",
                      help="print filenames as they are uploaded or downloaded",
                      action="store_true")
#parser.add_argument("-u", "--upload", help="upload a file or directory",
#upload=True)
  #parser.add_argument("-d", "--download",
                      #help="download a file or directory")#, action="store_true")
  params=parser.parse_args()
  global TARGET
  TARGET=os.path.abspath(params.path)

  checkToken()
  if False: #params.download:
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
    SET_NAME = ''
    if params.recursive:

      #upload target is a directory
      TARGET += "/"
      if params.set:
        # use the passed in name as the name of the set to upload
        SET_NAME=params.set
      print "uploading folder: ", TARGET
      upload_dir(TARGET, SET_NAME, params.tags, params.verbose)

    else:
      
      #upload target is a file
# debugging
      print "uploading single file: ", TARGET
      upload_file(TARGET, params.verbose, params.tags) #TODO: write
      #function


def upload_dir(TARGET, SET_NAME, tags, verbose):
  global dummy_video
  if tags:
    TAGS=tags
  else: 
    TAGS="uploaded on " + time.strftime("%d/%m/%Y")
  if verbose:
    print "Uploading", TARGET,
    if SET_NAME:
      print "to set", SET_NAME,
    print "with tags:", TAGS
  # Creating a set
  params = {}
  params['tags']=TAGS

# debugging
  #print "os.listdir(TARGET)[0]:",os.listdir(TARGET)[0]
  #print "os.listdir(TARGET)[:]:",os.listdir(TARGET)
  #print "os.listdir(TARGET)[0:]:",os.listdir(TARGET)[0:]
  #print "os.listdir(TARGET)[1:]:",os.listdir(TARGET)[1:]
  filename = os.listdir(TARGET)[0]
  photo_id = upload_file(filename, verbose, TAGS)
  remove_temp_file(filename)
  if SET_NAME:
    if photo_id != -1:
# make a set
      try:
        if verbose:
          print "Creating set",SET_NAME,
        resp = flickr.photosets.create(title=SET_NAME,primary_photo_id=photo_ids[0])
        photoset_id = photoset_id = resp.findall('photoset')[0].attrib['id']
        if verbose:
          print(' OK. Set id = ' + photoset_id)
      except:
        print "ERROR, set could not be created. One file uploaded (",filename,
        ") without deletion, and without being added to a set. If you get",
        " this same error often, maybe uploading with set isn't working."
        sys.exit(4)
    else:
        print "ERROR, set could not be created. One file uploaded (",filename,
        ") without deletion, and without being added to a set. If you get ",
        "this same error often, maybe uploading with set isn't working."
        sys.exit(4)

  for filename in os.listdir(TARGET)[1:]:
# upload all the files
    photo_id = upload_file(filename, verbose, TAGS)
    if SET_NAME:
# if set title was passed in, add file to set
      try:
        resp = flickr.photosets.addPhoto(photoset_id=photoset_id,photo_id=photo_id)
      except:
        print "ERROR adding file ", filename," to set "
  print "All files in dir", TARGET,"uploaded"



def remove_temp_file(filename):
  filename_split = filename.split('.')
  if len(filename_split) == 2:
    # file has extension
    ext = filename_split[1].lower()
  else:
    # no extension
    ext = ''
#      if ext not in ['png', 'jpeg', 'jpg', 'avi', 'mp4', 'gif', 'tiff', 'mov',
#       'wmv', 'ogv', 'mpg', 'mp2', 'mpeg',
#       'mpe', 'mpv']:
  #file needs to be padded and extension added
  # assume all files need to be padded for now, because it makes stuff easier
  if not os.path.exists(TEMP_FOLDER):
    # check if temp folder exists, print error if not
    print "ERROR. temporary file folder (",TEMP_FOLDER,") could not be ",
    "found. temp file could not be deleted. hopefully you deleted the temp",
    " folder?"
  os.remove(TEMP_FOLDER + filename+'.mp4')


def upload_file(filepath, verbose, TAGS):
  global TARGET
  filename = filepath.split('/')[-1]
  filename_split = filename.split('.')
  tempfileName = filename + '.mp4'
  print "uploading file: ", filename

  if len(filename_split) == 2:
    # file has extension
    ext = filename_split[1].lower()
  else:
    # no extension
    ext = ''
#      if ext not in ['png', 'jpeg', 'jpg', 'avi', 'mp4', 'gif', 'tiff', 'mov',
#       'wmv', 'ogv', 'mpg', 'mp2', 'mpeg',
#       'mpe', 'mpv']:
  #file needs to be padded and extension added
  # assume all files need to be padded for now, because it makes stuff easier
  if not os.path.exists(TEMP_FOLDER):
    # check if temp folder exists, make if not
    os.makedirs(TEMP_FOLDER)
  copyfile(dummy_video, TEMP_FOLDER + filename+'.mp4')
  f = open(TEMP_FOLDER + filename + '.mp4', 'a')
  curr_file = open( filepath, 'r')
  f.write(curr_file.read())
  f.close()
  curr_file.close()
  full_filename = TEMP_FOLDER + filename + '.mp4'
#     else:
    #file is already a picture or a video
#       full_filename = TARGET + filename


  if verbose:
    print(filename),
    print(" -- uploading..."),

  print(full_filename)

  photo_id = -1
  print "trying to upload file:",tempfileName, "with tags",TAGS
  try:
    uploadResp = flickr.upload(full_filename, is_public=0, is_friend=0, is_family=0)
    photo_id = uploadResp.findall('photoid')[0].text
    if verbose:
      print(' OK. Flickr id = ' + photo_id)
  except:
    if verbose:
      print(" ERROR. Could not upload file ", full_filename)
      #print "response:",uploadResp
    #TODO: log errors and progress somewhere
  return photo_id





main()
