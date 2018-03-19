#! /usr/bin/python
import os
import dropbox
import time
from datetime import datetime

def file_size(file_path):
    """
    @summary: gets the size of the file
    @param file_path: the path to the file
    @return: Returns the size of the file
    """
    total_size = 0
    for currentfile in os.listdir(file_path):
        full_file_path = os.path.join(file_path, currentfile) #"%s/%s" %(file_path, currentfile)
        total_size += os.stat(full_file_path).st_size
    return total_size

def dropbox_upload(auth_token, file, name):
    """
    @summary: Uploads a file to a specified dropbox account
    @param auth_token: access token for the account to link
    @param file: the file to upload
    @param title: path and/or name for the file on Dropbox
    @return: Successful upload message or error message if upload could not be completed
    """
    dbx = dropbox.Dropbox(auth_token)
    if dbx.users_get_current_account():
        if dbx.files_upload(file, name):
            metadata = dbx.files_get_metadata(name).server_modified
            return "Successful upload: %s" %str(metadata)
    else:
        return "Authentication failed. The file was not able to be uploaded."

def delete_file(file_path):
    """
    @summary: Deletes a file on the harddrive
    @param file_path: path to the file
    @return: Successful deletion message or error message if file could not be deleted
    """
    try:
        os.remove(file_path)
        return "The file %s has been permanently removed." %file_path
    except OSError, e:
        return "The file %s is a directory. Deletion not successful." %file_path

def write_to(log_file_path, details):
    """
    @summary: writes the details of a successful upload and deletion to a log file;
    a new log file will be created if the given one does not already exist
    @param log_file_path: path to the log file
    @param details: date and time of successful upload and path of deleted filed
    """
    my_path = log_file_path
    try:
        f = open(my_path, "a")
        f.write(details + "\n")
        f.close()
    except Exception as e:
        

def monitor_file(dir_to_watch, log_file, dbx_auth_token, dbx_file_path):
    """
    @summary: watches a configurable directory, uploads the file to specified online account,
    and deletes the file on local hard disk upon successful upload
    @param dir_to_watch: path to directory
    @param log_file: log file to write timestamps and details to
    @param dbx_auth_token: account authorization token
    @param dbx_file_path: configurable path to file on Dropbox
    """
    direc = dir_to_watch
    log = log_file
    auth_token = dbx_auth_token
    file_path = dbx_file_path

    #size and time new modifications are checked against
    last_modified_file = file_size(direc)
    now_timestamp = time.asctime(time.localtime(time.time()))
    write_to(log, "Start: " + str(now_timestamp))
    now_timestamp_datetime = datetime.strptime(now_timestamp, "%a %b %d %H:%M:%S %Y")

    while True:
        new_modified_file = file_size(direc)
        if last_modified_file != new_modified_file:
            for f in os.listdir(direc):
                path = os.path.join(direc, f)
                f_timestamp = time.ctime(os.stat(path).st_ctime)  # time file was created
                f_timestamp_datetime = datetime.strptime(f_timestamp, "%a %b %d %H:%M:%S %Y")  # creates datetime object of time created
                if f_timestamp_datetime > now_timestamp_datetime:
                    write_to(log, f)
                    file_content = open(path)
                    file_content_tostring = str(file_content.read())
                    upload = dropbox_upload(auth_token, file_content_tostring, file_path + "-" + str(f))
                    write_to(log, upload)
                    if "Successful" in upload:
                        delete = delete_file(path)
                        write_to(log, delete)

print "Enter the directory path: "
directory = str(raw_input())
print "Enter the log file path: "
log = str(raw_input())
print "Enter token authentication key:"
dbx_auth_token = str(raw_input())
print "Enter the configurable path to the file on your Dropbox account:"
dbx_file_path = str(raw_input())
print "Now monitoring... \n"

monitor_file(directory, log, dbx_auth_token, dbx_file_path)




