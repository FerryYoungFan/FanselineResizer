#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
If you want to use pyinstaller for this project,
simply run:
"
    python3 _Installer.py
                            "
in terminal
"""

import os
"""
Python 3.7	    V 3.7.4
Pillow		    V 7.2.0
"""

def checkEnvironment(showInfo=True):
    if showInfo:
        print("Checking Python Environment...")
    try:
        import PIL
    except:
        if showInfo:
            print("Pillow not found, try to install:")
        os.system("pip3 install Pillow==7.2.0")

    not_install = None
    try:
        not_install = "Pillow"
        import PIL
        if showInfo:
            print("Check Environment - Done!")
    except:
        print("Error: Environment Error")
        print("{0} not installed.".format(not_install))

checkEnvironment(True)

try:
    import PyInstaller.__main__
except:
    print("check pyinstaller: not installed. Now install pyinstaller:")
    os.system('pip3 install pyinstaller')
    import PyInstaller.__main__

app_name = "FanselineResizer"
main_file = "FanResizer.py"
icon_path = "./logo_256x256.ico"
output_list = ["--noconfirm", "--name=%s" % app_name, "-F", "--windowed"]
if os.path.exists(icon_path):
    output_list.append("--icon=%s" % icon_path)
output_list.append(main_file)

PyInstaller.__main__.run(output_list)
