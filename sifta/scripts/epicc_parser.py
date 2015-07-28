#!/usr/bin/python2
###############################################################################
# Copyright (c) 2014 Carnegie Mellon University
# Distributed under the terms of the BSD-style license found in license.txt.
# 
# Contributors: Will Klieber
###############################################################################

import sys
import os 
#import xml.etree.ElementTree as ET
import subprocess
from collections import *
from pprint import pprint
from OrderedSet import OrderedSet
from collections import OrderedDict
import re
import pdb
stop = pdb.set_trace
sfilename=""

def die(text): 
    sys.stderr.write(text + "\n")
    sys.exit(1)

class LineReader:
    """Reads a file line-by-line."""
    def __init__(self, file):
        self.file = file
        sfilename = file
        self.cur = None
        self.line_num = 0
        self.advance()

    def advance(self):
        self.cur = self.file.readline()
        self.line_num += 1

    def consume_line(self):
        ret = self.cur
        self.advance()
        return ret

    def close(self):
        self.file.close()

    def is_eof(self):
        return len(self.cur) == 0

class EpiccException(Exception):
    pass

def process_intent(infile, strip_intent_id=False):
    src_func = infile.consume_line()[4:].strip()
    curline = infile.consume_line()
    if not re.match("Intent value: [0-9]* possible value\(s\):", curline):
        if curline.strip() == "No value found.":  # TODO: Find out what this means.
            return [src_func, [], []]
        elif curline.strip() == "Found top element":
            return [src_func, [], [{'Top':True}]]
        elif curline.startswith("Type: "):
            return "IntentFilter"
        else:
            raise EpiccException("Unrecognized line: '%s'" % (curline.strip(),))
    ret = []
    intent_id = set()
    while True:
        curline = infile.consume_line()
        if len(curline.strip()) == 0:
            break
        if curline.strip() == 'No field set':
            ret.append({})
            continue
        # Note: ord("[")==0x5b, ord("]")==0x5d
        #regex_one =  "([A-Za-z]+): (\\x5b[^\\x5d]*\\x5d|[^\\x5d\\x5b, ]*)[,\n] *"
        ## Alex: The additional blank prevented matching of lines like this (blank in Type entry): Package: com/gmail/albanywang2000/onewordnews, Class: com/gmail/albanywang2000/onewordnews/StockActivity, Type: Japan stocks, Extras: [newField_45], 
        regex_one =  "([A-Za-z]+): (\\x5b[^\\x5d]*\\x5d|[^\\x5d\\x5b,]*)[,\n] *" 
        m = re.match("^ *(" + regex_one + ")*[\n]?$", curline)
        if m == None:
            intent = "ERROR: Unrecognized line: " + curline.strip()
        else:
            m = re.findall(regex_one, curline)
            intent = {}
            for (key, val) in m:
                if val.startswith("["):
                    assert(val.endswith("]"))
                    val = val[1:-1].split(", ")
                    if key == "Extras":
                        new_val = []
                        for ex in val:
                            if ex.startswith("newField_"):
                                intent_id.add(ex)
                                if not strip_intent_id:
                                    new_val.append(ex)
                            else:
                                new_val.append(ex)
                        val = new_val
                intent[key] = val
        #ret.append(curline)
        ret.append(intent)
    return (src_func, sorted(intent_id), ret)

def parse_epicc(filename, as_dict=False):
    sfilename = filename
    try:
        if (filename == '-'):
            file_ptr = sys.stdin
        else:
            file_ptr = open(filename, 'r')
    except IOError, e:
        die(str(e))
    infile = LineReader(file_ptr)
    ret = []
    pkg_name = ""
    while not infile.is_eof():
        if infile.cur.startswith("  - "):
            try:
                intent = process_intent(infile, strip_intent_id=as_dict)
                if intent != "IntentFilter":
                    ret.append(intent)
            except EpiccException as e:
                #die("Error parsing %s:\n%s" % (filename, str(e)))
                continue
        else:
            if pkg_name == "":
                m = re.match("^Manifest file for ([A-Za-z0-9_.$]+) version .*", infile.cur)
                if m:
                    pkg_name = m.group(1)
            infile.consume_line()
    if as_dict:
        ret = epicc_to_dict(ret,filename)
    #filename.close()
    return (pkg_name, ret)

def epicc_to_dict(epicc, filename):
    d = {}
    for (func_loc, intent_ids, intent_info) in epicc:
        if len(intent_ids) == 0:
            intent_ids = ["*"]
        if len(intent_ids) > 1:
            #die("Error: Intent does not have exactly one ID!\n")
            intent_ids = intent_ids[len(intent_ids)-1] #Intent has multiple ID's. Using the last one.
        d.setdefault(intent_ids[0], [])
        d[intent_ids[0]].extend(intent_info)
    return d

if __name__ == "__main__":
    import json
    def main():
        filename = sys.argv[1]
        ret = parse_epicc(filename)
        ret_json = json.dumps(ret, sort_keys=True, indent=4, separators=(',', ': '))
        #pprint(ret)
        print(ret_json)
    main()
