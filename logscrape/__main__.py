#!/usr/bin/env python3
"""
Module for finding logging directories and searching them for matching patterns.
Can be run as a standalone program.
Author: Max Forsman
"""

import shlex
import os
from subprocess import Popen, PIPE
from log_parser import LogParser

ENCODING = 'utf-8'

def run_process(command):
    """Run command and output (stdout, error, exit_code)"""

    process = Popen(command, stdout=PIPE)
    (output, err) = process.communicate()
    exit_code = process.wait()
    return (output.decode(ENCODING), err, exit_code)

def find_log_directories(path):
    """Return any subdirectories from path with "log" in their name"""

    cmd = ["find", path, "-type", "d", "-name", "log*"]
    (output, error, code) = run_process(cmd)
    return output

def search_in_file(pattern, file_path):
    """Look for matching pattern in file_path"""
    prsr = LogParser(file_path)
    prsr.parse(pattern)

def build_find_params():
    """Return params for 'find' program"""

    find_params = ""
    if ARGS.max_age:
        find_params += "-mtime -"+ARGS.max_age + " "
    if ARGS.min_age:
        find_params += "-mtime +"+ARGS.min_age + " "
    return find_params

def find_matching_log_files(pattern, directories):
    """
    Find log files that contain pattern in list of directories.
    Note: directories should be a string and not a list (as they are output to stdout from unix find util)
    """

    find_params = build_find_params()
    cmd = "find " + directories + "\\( -name *.log -o -name *.log.gz -o \
        -name *.out -o -name *.out.gz -o -name *.txt \) " + find_params +" -exec zgrep -l "+pattern+" {} '\';"
    cmd = shlex.split(cmd)
    (output, error, code) = run_process(cmd)
    return output

def shutdown():
    """Exit the program"""
    raise SystemExit

def main():
    """Main program method"""

    import argparse
    #Add optional args
    parser = argparse.ArgumentParser(description='Search a directory for log files or search for a pattern in log files')
    parser.add_argument('--directory', '-d', action='store', dest='search_dir', default=os.getcwd(),
                        help='Set directory to be searched')
    parser.add_argument('--list-files', '-l', action='store_true', dest='list',
                        help='Only outputs the name of matching files')
    parser.add_argument('--newer-than', '-n', dest='max_age', help='Only show files newer than X days')
    parser.add_argument('--older-than', '-o', dest='min_age', help='Only show files older than X days')
    #Add positional args
    parser.add_argument('pattern', nargs=1)
    global ARGS
    ARGS = parser.parse_args()
    pattern = ARGS.pattern[0]
    dirs = find_log_directories(ARGS.search_dir)
    matching_files = find_matching_log_files(pattern, dirs)
    if ARGS.list:
        print(matching_files)
        shutdown()
    for file in matching_files.splitlines():
        search_in_file(pattern, file)


if __name__ == '__main__':
    main()
