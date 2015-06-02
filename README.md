#Google Upload Python (GUP)

A simple way to upload a directory with sub directories to Google Drive in parallel. With largish files and 10
connections, speeds of over 90MB/s have been seen.

##Installation
First, setup the drive cli client located here: https://github.com/prasmussen/gdrive
Then either copy gup.py to somewhere on your path, or simply run it from the directory.

There are no other requirments other than a standard Python 2.7/3.4 install.

##Usage

gup.py [-h] [-c] [-n NUM_CONNECTIONS] folder

Upload directory to gdrive

positional arguments:
  folder                Path to folder to open

optional arguments:
  -h, --help            show this help message and exit
  -c, --no-create          Disable creating directories in gdrive
  -n NUM_CONNECTIONS, --num_connections NUM_CONNECTIONS
                        Number of connections to open to Google drive

