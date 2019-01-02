#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
# pychecker: disable=line-too-long
"""Tool for setting up synchronized videos to be used with info-beamer
Developed by Joseph T. Foley <foley at RU dot IS>
Started 2019-01-02

Package dependencies
  ubuntu: python-requests ffmpeg
  pip: timecode
"""

import os
import os.path
import sys
import subprocess
import re
import itertools

import logging
import argparse

import timecode ## Have to get from pip

if __name__ == '__main__':
    # http://stackoverflow.com/questions/8299270/ultimate-answer-to-relative-python-imports
    # relative imports do not work when we run this module directly
    PACK_DIR = os.path.dirname(os.path.join(os.getcwd(), __file__))
    ADDTOPATH = os.path.normpath(os.path.join(PACK_DIR, '..'))
    # add more .. depending upon levels deep
    sys.path.append(ADDTOPATH)

    SCRIPTPATH = os.path.dirname(os.path.realpath(__file__))
    DEVNULL = open(os.devnull, 'wb')


class PrepVideoTool(object):
    """Abstraction for interacting with info-beamer REST api"""
    logfd = None
    log = logging.getLogger("prepvideos")

    def __init__(self, args):
        """Prepare logger and other setup
        """
        # setup logger
        logpath = 'info_beamer.log'
        floglevel = logging.DEBUG
        cloglevel = logging.INFO
        self.log.setLevel(floglevel)
        self.log.addHandler(logging.FileHandler(logpath))
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(cloglevel)
        self.log.addHandler(console_handler)
        self.log.info("Logging to %s", logpath)
        self.log.debug("File logging set at %s", floglevel)
        self.log.debug("Console logging level at %s", cloglevel)

        # Examine the arguments
        # create a data structure for the relevant video files
        self.fileinfo = {}
        for file_path in args.infile:
            self.fileinfo[file_path] = {'file_path': file_path}

    def getvideoinfo(self):
        """Examine some videos and get useful informatin into the self.fileinfo dictionary.
        We assume there is only one video stream per file"""
        #https://stackoverflow.com/questions/3844430/how-to-get-the-duration-of-a-video-in-python
        duration_re = re.compile(r'Duration: ([\d\:\.]+),')
        fps_re = re.compile(r'([\d]+) fps')
        
        for filename in self.fileinfo.keys():
            result = subprocess.Popen(
                ["ffprobe", filename],
                stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            result_lines = result.stdout.readlines()
            duration_lines = [x for x in result_lines if "Duration" in x]
            match_obj = duration_re.search(duration_lines[0])
            vlen = match_obj.group(1)
            fps_lines = [x for x in result_lines if "fps" in x]
            match_obj = fps_re.search(fps_lines[0])
            fps = match_obj.group(1)
            self.fileinfo[filename] = {'timecode': timecode.Timecode(fps, vlen)}
        
            
    def calcvideomin(self):
        """Figure out which video is shortest"""
        self.getvideoinfo()
        minfilename = None
        mintimecode = timecode.Timecode("30", "23:59:59:59")
        for filename in self.fileinfo.keys():
            mytimecode = self.fileinfo[filename]['timecode']
            self.log.info("file: %s, timecode: %s", filename, mytimecode)
            if mytimecode < mintimecode:
                self.log.info('smaller than %s')
                minfilename = filename
                mintimecode = mytimecode

        self.log.info("Minimum file: %s, timecode: %s", minfilename, mintimecode)

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='Tool for preparing synchronized videos for use in info-beamer')
    PARSER.add_argument('--version', action="version", version="%(prog)s 0.1")  #version init was depricated
    PARSER.add_argument('action',#required!
                        choices=['checklength'],
                        help='what should the tool do')
    PARSER.add_argument('infile', nargs="+",
                        help='files to be processed')
    ARGS = PARSER.parse_args()
    TOOL = PrepVideoTool(ARGS)
    if ARGS.action == "checklength":
        TOOL.calcvideomin()
