#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tkinter as tk
import base64
from io import BytesIO
from PIL import Image

def ensureDir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def convertFileFormat(path, new_format=None):
    if new_format is None:
        return path
    last_dot = 0
    for i in range(len(path)):
        if path[i] == ".":
            last_dot = i
    ftype = path[last_dot + 1:]
    if new_format[0] == ".":
        pass
    else:
        new_format = "." + new_format
    if "/" in ftype or "\\" in ftype:
        outpath = path + new_format
    else:
        outpath = path[:last_dot] + new_format
    return outpath


def getFileName(path="", suffix=True):
    if not path:
        return ""
    fname = path.replace("\\", "/").split("/")[-1]
    if not suffix:
        fname = ".".join(fname.split(".")[:-1])
    return fname


def getFileSuffix(fname=""):
    if not fname:
        return ""
    if not "." in fname:
        return ""
    return "." + fname.split(".")[-1]


def getFilePath(path=""):
    if not path:
        return ""
    fname = path.replace("\\", "/").split("/")[-1]
    if "." in fname:
        path = "/".join(path.replace("\\", "/").split("/")[:-1])
    else:
        path = "/".join(path.replace("\\", "/").split("/"))

    if path[-1] != "/":
        path = path + "/"
    return path


def legalFileName(fname=""):
    if not fname:
        return False
    illegal_dict = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
    for char in illegal_dict:
        if char in fname:
            return False
    return True


def makeLegalFileName(fname=""):
    if not fname:
        return "untitled"
    illegal_dict = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
    for char in illegal_dict:
        fname.replace(char, "_")
    return fname


def protectPath(path=""):
    if not os.path.exists(path):
        return path
    else:
        fpath = getFilePath(path)
        fname = getFileName(path, False)
        suffix = getFileSuffix(getFileName(path, True))
        name_counter = 1
        new_path = fpath + fname + "(" + str(name_counter) + ")" + suffix
        while os.path.exists(new_path):
            name_counter = name_counter + 1
            new_path = fpath + fname + "(" + str(name_counter) + ")" + suffix
        return new_path


def pil2tk(image):
    buffer = BytesIO()
    image.save(buffer, quality=100, format="PNG")
    base64_str = base64.b64encode(buffer.getvalue())
    return tk.PhotoImage(data=base64_str)


if __name__ == '__main__':
    pass
