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

THREADS = 10


def main(args):
    """
    Creates pools for mapping to all the files the directory.
    """
    toUpload = []
    dirToID = {}
    pool = multiprocessing.Pool(args.num_connections)
    if args.folder[-1] == '/':
        args.folder = args.folder[0:-1]
    #Begin creating directories
    if args.create:
        print("****Creating directories****")
        dirToID = createDir((None, args.folder, dirToID))
    for root, dirs, files in os.walk(args.folder):
        if args.create:
            directoryTuples = [(root, dir, dirToID) for dir in dirs] #so inffecient...
            dirToIDArray = pool.map(createDir, directoryTuples)
            dirToID = {k : v for d in dirToIDArray for k, v in d.items()}
    if args.create:
        print("****Created directories****")
    numFiles = len(toUpload)
    print("****Uploading {0} files****".format(numFiles))
    pool.map(upload, toUpload)
    print("****Upload complete****")
    pool.close()
    pool.join()


def upload(fileNameParentTuple, count=0):
    """
    upload a file to the correct directory
    """
    f, name, parent = fileNameParentTuple
    try:
        output = subprocess.check_output(["/usr/local/bin/drive", "upload", "-t", name, "-p", parent, "-f", f])
        print("Uploaded: " + name)
    except subprocess.CalledProcessError:
        print("FAILED: " + name)
        if count < MAXCOUNT:
            upload(fileNameParentTuple, count + 1)


def createDir(parentFolderTuple):
    """
    Create the directory structure and save the ids
    tuple should be in the form parent, folder, dirToID
    """
    parent, folder, dirToID = parentFolderTuple
    fullPath = folder
    if parent is not None:
        fullPath = os.path.join(parent,folder)
    name = os.path.basename(fullPath)
    parentID = None
    try:
        parentID = dirToID[parent]
    except KeyError:
        pass
    #Create the command
    if parentID is None:
        cmd = ["/usr/local/bin/drive", "folder", "-t", name]
    else:
        cmd = ["/usr/local/bin/drive", "folder", "-t", name, "-p", parentID]
    try:
        #Run the command
        output = subprocess.check_output(cmd)
        dirToID[fullPath] = output.split()[1]
        print("Created {0}".format(name))
        return dirToID
    except subprocess.CalledProcessError:
        print ("FAILED: " + name)
        return createDir(parentFolderTuple) # naively try again

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Upload directory to gdrive")
    parser.add_argument('folder', type=str, help="Path to folder to open")
    parser.add_argument('-c', '--create', help="Disable creating directories in gdrive",
                        action='store_false', default=True)
    parser.add_argument('-n', '--num_connections', help="Number of connections to open to Google drive",
                        default=THREADS)
    args = parser.parse_args()
    main(args)
