#!/bin/env python

import sys
import os
import re

EXAMPLE_DIR = "examples"
TAG_DIR = "tags"

FILE_PATH = os.path.dirname(os.path.realpath(__file__))

def clear_folder(folder):
    # Subroutine derived from http://stackoverflow.com/questions/185936/delete-folder-contents-in-python
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception:
            sys.stderr.write("Could not delete file %s.%s" % (file_path, os.linesep))

tag_pattern = re.compile(r"^\s*#+\s*<(/?)([^/>][^>]*)>\s*$")

class TagMatch:
    is_match = False
    is_start = False
    tag = None
    def __init__(self, line):
        match = tag_pattern.search(line)
        if not match:
            return
        self.is_match = True
        self.is_start = len(match.group(1)) == 0
        self.tag = match.group(2)

class Tag:
    def __init__(self, name, start):
        self.name = name
        self.start = start
        self.end = None
        self.line_gen = ()

    def ended(self, ended_at):
        if self.end is not None:
            raise ValueError("Tag ended for second time at %i" % ended_at)
        self.end = ended_at

def get_tags(read_file):
    f = open(read_file, 'r')
    non_tag_lines = []
    tags = {}
    for line in f:
        tag_match = TagMatch(line)
        if tag_match.is_match:
            # Process tag
            if tag_match.is_start:
                if tag_match.tag in tags:
                    raise ValueError("Duplicate tag %s" % tag_match.tag)
                tag = Tag(name=tag_match.tag, start=len(non_tag_lines))
                tags[tag.name] = tag
            else:
                if tag_match.tag not in tags:
                    raise ValueError("End tag before start tag for %s" % tag_match.tag)
                tag = tags[tag_match.tag]
                tag.ended(len(non_tag_lines))
                tag.line_gen = (non_tag_lines[x] for x in xrange(tag.start, tag.end))
        else:
            non_tag_lines.append(line)
    f.close()
    return (tags, non_tag_lines)

def process_tags(example_file_name):
    read_path = os.path.join(FILE_PATH, EXAMPLE_DIR, example_file_name)
    tags, non_tag_lines = get_tags(read_path)
    for tag_name in tags:
        tag = tags[tag_name]
        if not tag.end:
            raise ValueError("Tag started but not ended:  %s." % tag)
        filename = "%s.%s.py" % (example_file_name, tag_name)
        write_path = os.path.join(FILE_PATH, TAG_DIR, filename)
        f = open(write_path, 'w')
        for line in tag.line_gen:
            f.write(line)
        f.close()
    write_path = os.path.join(FILE_PATH, TAG_DIR, example_file_name)
    f = open(write_path, 'w')
    for line in non_tag_lines:
        f.write(line)
    f.close()

full_tags_dir = os.path.join(FILE_PATH, TAG_DIR)
if not os.path.exists(full_tags_dir):
    os.makedirs(full_tags_dir)
clear_folder(full_tags_dir)
example_files = os.listdir(os.path.join(FILE_PATH, EXAMPLE_DIR))
for example_file in example_files:
    process_tags(example_file)

