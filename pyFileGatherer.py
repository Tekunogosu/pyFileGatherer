#!/usr/bin/env python3

import io
import os
import re
import sys
import argparse
from glob import glob
from tarfile import TarFile, TarInfo, TarError
from datetime import datetime


# TODO: add ability to load config from ~/.config/pyfg
# TODO: Use argparse
# TODO: Add command line switches for
#       -h,
#       -c (config location)
#       -n (filename/location) Check permissions on filename/location
#       -f Files to add to archive. Throw error if no config files are specified in config or using -f
#       -t compression type, default: xz
#       -D enable debug output

DEBUG = False

args = sys.argv


FILE_NAME = f".config/sysConfs/configs-{datetime.now().strftime('%Y%m%d%H%M%S')}.xz"

# TODO: set output dir from config file

if DEBUG:
    COMPRESSED_OUTPUT_DIR = os.getcwd()
else:
    COMPRESSED_OUTPUT_DIR = os.path.expanduser("~")

files = {
    "grub": [os.path.abspath("/etc/default/grub"),
             os.path.abspath("/etc/grub.d/07_custom")],
    "portage": {
        "packages": glob(os.path.abspath("/etc/portage/package.*")),
        "make.conf": os.path.abspath("/etc/portage/make.conf"),
        "env": glob(os.path.abspath("/etc/portage/env/*"))
    },
    "fstab": os.path.abspath("/etc/fstab"),
    "genkernel_config": os.path.abspath("/etc/genkernel.conf"),
    "xorg.conf": os.path.abspath("/etc/X11/xorg.conf.d/xorg.conf"),
    "kernel_config": os.path.abspath("/usr/src/linux/.config")
}

files_to_compress = []


def glob_files(file_glob):

    if isinstance(file_glob, str):
        print("processing string") if DEBUG else None
        files_to_compress.extend(glob(file_glob))

    if isinstance(file_glob, list):
        print("processing list") if DEBUG else None
        for i in file_glob:
            glob_files(i)

    if isinstance(file_glob, dict):
        print("processing dict") if DEBUG else None
        for v in file_glob.values():
            glob_files(v)


glob_files(files)

the_file = COMPRESSED_OUTPUT_DIR + f"/{FILE_NAME}"

try:

    decision = None

    if os.path.exists(the_file):

        while not decision:
            decision = input(f"File {FILE_NAME} already exists, overwrite? [Y/n/[a|auto]]")[0].strip().lower()

            if "yes".startswith(decision):
                break

            elif "auto".startswith(decision):
                new_name = f"{FILE_NAME.split('.')[0]}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.xz"
                the_file = f"{COMPRESSED_OUTPUT_DIR}/{new_name}"

                if os.path.exists(the_file):
                    print(f"Sorry, {the_file} already exists somehow..")
                    decision = None
                else:
                    print(f"Auto-renaming file to {new_name}")

            elif "no".startswith(decision):
                new_name = input("Please enter new name: ")
                the_file = COMPRESSED_OUTPUT_DIR + f"/{new_name}"
                print(f"Writing to file {new_name}")

            else:
                print("Can't read? [Y/n/[a|auto]] are the only options...")
                decision = None

    with TarFile.open(the_file, 'w:xz') as lzf:
        for f in files_to_compress:
            lzf.add(name=f)

except TarError as e:
    print(f"Error occurred {e}")
    exit(1)


print(f"Files written to {the_file}")
