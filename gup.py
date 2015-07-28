#!/usr/local/bin/python3
"""
Upload everything in a subdirectory to google drive. This program depends on the google drive
program located at https://github.com/prasmussen/gdrive.

The number of parallel connections is configured by the threads parameter, or by the -n flag.

This program should be able to achieve almost 90 MB/s of throughput to google drive when uploading photos and -n = 10
"""
import multiprocessing
import argparse
import os
import subprocess
import time
import random

THREADS = 10 #Number of threads.
MAXCOUNT = 1000 # Max number of retries.


class File(object):
    """
    Class to represent a file (or folder!) to be uploaded to google drive
    """
    def __init__(self, name, path, parent_ID=None):
        self.name = name
        self.path = path
        self.parent_ID = parent_ID

def main(args):
    """
    Creates pools for mapping to all the files the directory.
    """
    to_upload = []
    pool = multiprocessing.Pool(args.num_connections)
    if args.folder[-1] == '/':
        args.folder = args.folder[0:-1]
    #Begin creating directories
    print("****Creating directories****")
    #Create the initial directory.
    tuple_root_id = create_dir(File(args.folder, os.path.abspath(args.folder), None)) #Create the root directory.
    dict_dir_to_id = {tuple_root_id[0]: tuple_root_id[1]}
    for root, dirs, files in os.walk(args.folder):
        #Get the true path of the root.
        root = os.path.abspath(root)
        #Create file objects from the current dirs.
        file_dirs = [File(DIR, os.path.join(root, DIR), dict_dir_to_id[root]) for DIR in dirs]
        #Create the dirs in parallel, Get a tuple of (directory, id)
        tuple_directories_ids = pool.map(create_dir, file_dirs)
        #Add the ids from the previous map call to the directory -> id mapping
        for directory, id, in tuple_directories_ids:
            dict_dir_to_id[directory] = id
        #Append file objects to an array for future uploading
        to_upload += [File(file, os.path.join(root,file), dict_dir_to_id[root]) for file in files] #
    print("****Created directories****")
    numFiles = len(to_upload)
    print("****Uploading {0} files****".format(numFiles))
    pool.map(upload, to_upload)
    print("****Upload complete****")
    pool.close()
    pool.join()


def upload(f, count=0):
    """
    upload a file to the correct directory
    """
    try:
        output = subprocess.check_output(["/usr/local/bin/drive", "upload", "-t", f.name, "-p", f.parentID, "-f", f.path])
        print("Uploaded: " + f.name)
    except subprocess.CalledProcessError:
        print("FAILED: " + f.name)
        if count < MAXCOUNT:
            time.sleep(1+random.Random())
            upload(f, count + 1)


def create_dir(folder, count=0):
    """
    Create the directory structure and save the ids
    tuple should be in the form parent, folder, dirToID
    """

    if folder.parent_ID is None:
        cmd = ["/usr/local/bin/drive", "folder", "-t", folder.name]
    else:
        cmd = ["/usr/local/bin/drive", "folder", "-t", folder.name, "-p", folder.parent_ID]
    try:
        #Run the command
        output = subprocess.check_output(cmd)
        print("Created {0}".format(folder.name))
        return (folder.path, output.split()[1]) #Id of this folder
    except subprocess.CalledProcessError:
        print ("FAILED: " + folder.name)
        if count < MAXCOUNT:
            time.sleep(1+random.Random())
            return create_dir(folder, count+ 1) # Try again

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Upload directory to gdrive")
    parser.add_argument('folder', type=str, help="Path to folder to open")
    parser.add_argument('-n', '--num_connections', help="Number of connections to open to Google drive",
                        default=THREADS)
    args = parser.parse_args()
    main(args)
