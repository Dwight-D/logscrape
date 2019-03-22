"""Module for parsing a logfile and retrieving log entries containing a given pattern"""

import gzip
import re
import mmap
import collections
import regex_templates

NEWLINE = b'\n'



def check_if_entry_start(line):
    """
    Check if current line is the start of a log entry
    Override this implementation if you want to define a different way of detecting the start of a log entry
    """

    regex = regex_templates.LOGBACK_BASIC_START
    match = re.search(regex, line)
    return bool(match)

#TODO: Refactor, make configurable/templateable instead of using inheritance
class LogParser:
    """Contains basic text file parsing functionality.
    Ideally should be extended to support specific log formatting.
    """

    def __init__(self, file_path):
        self.path = file_path
        self.file_map = self.open_file_map(file_path)
        self.encoding = 'utf-8'
        self.cursor_index = 0
        self.match_index = 0
        self.matches = []
        self.entries = []

    def open_file_map(self, file_path):
        """
        Open a mmap and return it
            :param file_path: The file to open
        """
        if file_path.endswith(".gz"):
            f = gzip.open(file_path, mode='r+b')
        else:
            f = open(file_path, 'r+b')
        file_map = mmap.mmap(f.fileno(), 0)
        file_map.seek(0) # reset file cursor
        return file_map

    def find_matches(self, pattern):
        """Find any occurences of pattern and store in self.matches"""

        #Encode string to binary for compatiblity with binary memory map
        pattern = pattern.encode(self.encoding)
        #Convert iterator to tuple in order to get count
        matches = list(re.finditer(pattern, self.file_map))
        self.matches = matches

    def has_matches(self):
        """Checks if any matches were found"""
        return len(self.matches) != 0

    def process_matches(self):
        """Process all matches and output their corresponding log entries"""
        if not self.has_matches():
            return None
        self.remove_duplicate_matches()
        for match in self.matches:
            index = self.find_previous_newline(match.start()) + 1
            self.move(index)
            output = self.readline()
            while True:
                line = self.readline()
                if line == '':
                    self.entries.append(output)
                    break
                if not check_if_entry_start(line):
                    output += line
                else:
                    self.entries.append(output)
                    break
         
    def remove_duplicate_matches(self):
        first_index = self.find_previous_newline(self.matches[0].start())
        if first_index == -1:
            first_index = 0
        duplicates = set()
        for idx, first_match in enumerate(self.matches):
            #If no newline between current and next match, remove next match (duplicate of first)
            pos = self.find_previous_newline(first_match.start()) +1
            if pos > 0:
                self.move(pos)
                match_line = self.readline()
                if not check_if_entry_start(match_line):
                    duplicates.add(idx)
            try:
                next_match = self.matches[idx + 1]
                if self.check_if_matches_on_same_line(first_match, next_match):
                    duplicates.add(idx+1)
            #No more matches
            except IndexError:
                break
        duplicates = list(duplicates)
        duplicates.reverse()
        for idx in duplicates:
            self.matches.pop(idx)

    def find_previous_newline(self, index):
        """Find the closest newline before index"""
        index = self.file_map.rfind(NEWLINE, 0, index)
        return index

    def find_next_newline(self, index):
        """Find the closest newline after index"""
        return self.file_map.find(NEWLINE, index)

    def check_if_matches_on_same_line(self, first_match, second_match):
        """
        Checks if two matches are separated by a newline character or not
        """
        result = self.file_map.rfind(NEWLINE, first_match.start(), second_match.start())
        return result == -1

    def readline(self, index=None):
        if not index:
            index = self.file_map.tell()
        self.file_map.seek(index)
        try:
            output = self.file_map.readline().decode(self.encoding)
        except UnicodeDecodeError:
            print(self.path)
            compressed = self.file_map.readline()
            print(compressed)
            output = gzip.decompress(compressed)
            print(output)
        return output

    def move(self, index):
        self.file_map.seek(index)

    def get_match_string(self, match):
        self.file_map.seek(match.start())
        line = self.file_map.read(match.end() - match.start())
        return line.decode(self.encoding)

    def get_line(self, index):
        self.move(self.find_previous_newline(index) +1 )
        return self.readline()

    def print_entries(self):
        for entry in self.entries:
            print(self.path)
            print(entry)

    def parse(self, pattern):
        self.find_matches(pattern)
        self.process_matches()
        self.print_entries()
        
