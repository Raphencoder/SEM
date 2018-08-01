# -*- coding: utf-8 -*-

"""
file: setup.py

Description: setup file for SEM.

author: Yoann Dupont

MIT License

Copyright (c) 2018 Yoann Dupont

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# setuptools
from setuptools import setup, find_packages

import platform
SYSTEM = platform.system().lower()
ON_WINDOWS = (SYSTEM == "windows")

import subprocess
import tarfile
import os.path
import shutil
import sys
from filecmp import dircmp

def diff_files(dcmp):
    def diff_files_rec(dcmp, acc):
        right_only = dcmp.right_only
        if right_only:
            for ro in right_only:
                acc.append(os.path.join(dcmp.right, ro))
        for sub_dcmp in dcmp.subdirs.values():
            diff_files_rec(sub_dcmp, acc)
    acc = []
    diff_files_rec(dcmp, acc)
    return acc

try:
    prompt = raw_input
except NameError:
    prompt = input
validity = {"y":True, "ye":True, "yes":True, "n":False, "no":False}

import sem

#
# Removing GUI features, whan tkinter is not installed.
#

tkinter_available = True
try:
    import Tkinter
except ImportError:
    try:
        import tkinter
    except ImportError:
        tkinter_available = False

packages = find_packages()

if not tkinter_available:
    module_dir = os.path.join("sem", "modules")
    gui_files = [f for f in os.listdir(module_dir) if "gui" in f]
    for gui_file in gui_files:
        gui_path = os.path.join(module_dir, gui_file)
        shutil.move(gui_path, os.path.join(".", "."+gui_file))
    packages = [p for p in packages if "gui" not in p]

#
# compiling Wapiti
#

ext_dir = "./ext/"
wapiti_tar = os.path.join(ext_dir, [f for f in os.listdir("./ext") if f.startswith("wapiti") and f.endswith("tar.gz")][0])
cwd = os.path.abspath(".")
if not os.path.exists(os.path.join(ext_dir, "wapiti")):
    with tarfile.open(wapiti_tar, "r:gz") as tar:
        tar.extractall(os.path.dirname(ext_dir))
os.chdir(os.path.join(ext_dir, "wapiti"))
if ON_WINDOWS:
    cmd = [r".\make.bat", "wapiti"]
    wapiti_exec = os.path.join(ext_dir, "wapiti", "wapiti.exe")
else:
    cmd = ["make"]
    wapiti_exec = os.path.join(ext_dir, "wapiti", "wapiti")
if not os.path.exists(wapiti_exec):
    exit_status = subprocess.call(cmd, shell=True)
    os.chdir(cwd)
    if exit_status == 0:
        print
        print
        print "Wapiti compilation successful!"
    else:
        raise RuntimeError("Could not compile Wapiti: error code {}".format(exit_status))
else:
    print wapiti_exec, "already exists, not compiling."
    print

#
# preparing SEM data
#

# overriding SEM data, if the user is OK with it.
usr_sem_data = os.path.join(os.path.expanduser(u"~"), "sem_data")
already_exists = os.path.exists(usr_sem_data)
override = False
if already_exists:
    answer = prompt("\nsem_data already exists, override? [y/N] ").lower()
    override = validity.get(answer, False)

if override:
    try:
        shutil.rmtree(os.path.join(os.path.expanduser(u"~"), "sem_data"))
    except: # does not exist
        pass

try:
    os.makedirs(os.path.join(os.path.expanduser(u"~"), "sem_data"))
except: # already exists
    pass

if override or not already_exists:
    try:
        shutil.copytree("./resources", os.path.join(os.path.expanduser(u"~"), "sem_data", "resources"))
    except:
        pass
    try:
        shutil.copytree("./images", os.path.join(os.path.expanduser(u"~"), "sem_data", "resources", "images"))
    except:
        pass
    try:
        shutil.copytree("./ext", os.path.join(os.path.expanduser(u"~"), "sem_data", "ext"))
    except:
        pass
    try:
        shutil.copytree("./non-regression", os.path.join(os.path.expanduser(u"~"), "sem_data", "non-regression"))
    except:
        pass
else:
    # even if sem_data already exists, there may be some new files
    # the user would like to have.
    missing = diff_files(dircmp(os.path.join(usr_sem_data, "resources"), 'resources'))
    if missing:
        print "\nThe following files are missing:"
        print u"\t"+u" ".join(missing)
        answer = prompt("add missing files? [Y/n] ").lower()
        add_missing = validity.get(answer, True)
        if add_missing:
            for filename in missing:
                dest = os.path.join(usr_sem_data, filename)
                if os.path.isdir(filename):
                    shutil.copytree(filename, dest)
                else:
                    shutil.copy(filename, dest)

#
# launching setup
#

setup(
    name = "SEM",
    description = "SEM tool for text annotation",
    long_description = "SEM is a free NLP tool relying on Machine Learning technologies, especially CRFs. SEM provides powerful and configurable preprocessing and postprocessing.",
    license = "MIT",
    author = "Yoann Dupont",
    author_email = "yoa.dupont@gmail.com",
    maintainer = "Yoann Dupont",
    maintainer_email = "yoa.dupont@gmail.com",
    version = sem.version(),
    keywords = ['natural language processing', 'machine learning', 'tagging',
                'part-of-speech tagging', 'chunking', 'named entity recognition'],
    packages = find_packages(),
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'sem = sem.__main__:main'
        ]
    },
)

if not tkinter_available:
    for gui_file in gui_files:
        shutil.move(os.path.join(".", "."+gui_file), os.path.join(module_dir, gui_file))
