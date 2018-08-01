# -*- coding: utf-8 -*-

"""
file: wapiti.py

Description: a very simple wrapper for calling wapiti. Provides train
and test procedures.
TODO: add every option for train and test
TODO: add support for other modes, such as dump and update (1.5.0+)

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

import logging
import os.path
import subprocess
import time
import tarfile

from sem.logger import default_handler

from sem import SEM_HOME, SEM_EXT_DIR

from sem.misc import check_model_available

wapiti_logger = logging.getLogger("sem.wapiti")
wapiti_logger.addHandler(default_handler)
wapiti_logger.setLevel("INFO")

__command_name = os.path.join(SEM_EXT_DIR, "wapiti", "wapiti")

def command_name():
    """
    returns the executable name of Wapiti.
    
    This supposes that wapiti is installed on your computer.
    """
    
    return __command_name

def train(inputfile, pattern=None, output=None, algorithm=None, nthreads=1, maxiter=None, rho1=None, rho2=None, model=None, compact=False):
    """
    The train command of Wapiti.
    """
    
    cmd = [command_name(), "train"]
    if pattern is not None:   cmd.extend(["-p", pattern])
    if algorithm is not None: cmd.extend(["-a", str(algorithm)])
    if nthreads > 1:          cmd.extend(["-t", str(nthreads)])
    if maxiter is not None:   cmd.extend(["-i", str(maxiter)])
    if rho1 is not None:      cmd.extend(["-1", str(rho1)])
    if rho2 is not None:      cmd.extend(["-2", str(rho2)])
    if model is not None:     cmd.extend(["-m", str(model)])
    if compact:               cmd.append("-c")
    
    cmd.append(str(inputfile))
    if output is not None: cmd.append(str(output))
    
    exit_status = subprocess.call(cmd)
    
    if exit_status != 0:
        if output is None: output = "*stdout"
        raise RuntimeError("Wapiti exited with status {0}.\n{1:>6}: {2}\n{3:>6}: {4}\n{5:>6}: {6}".format(exit_status, "input", inputfile, "pattern", pattern, "output", output))

def label(input, model, output=None, only_labels=False, nbest=None):
    """
    The label command of Wapiti.
    """
    
    cmd = [command_name(), "label", "-m", str(model)]
    
    if only_labels:       cmd.extend(["-l"])
    if nbest is not None: cmd.extend(["-n", str(nbest)])
    
    cmd.append(input)
    if output is not None: cmd.append(str(output))
    
    exit_status = subprocess.call(cmd)
    
    if exit_status != 0:
        if output is None: output = "*stdout"
        raise RuntimeError("%s exited with status %i.\n\tmodel: %s\n\tinput: %s\n\toutput: %s" %(command_name(), exit_status, model, input, output))

def label_corpus(corpus, model, field, encoding):
    corpus_unicode = unicode(corpus).encode(encoding)
    
    cmd = [command_name(), "label", "-m", model, "--label"]
    
    wapiti_process     = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    w_stdout, w_stderr = wapiti_process.communicate(input=corpus_unicode)
    
    i = 0
    j = 0
    corpus.fields.append(field)
    for element in w_stdout.split("\n"):
        element = element.strip()
        if "" == element:
            i += 1
            j  = 0
        else:
            corpus.sentences[i][j][field] = element
            j += 1

def label_document(document, model, field, encoding, annotation_name=None, annotation_fields=None):
    if annotation_fields is None:
        fields = document.corpus.fields
    else:
        fields = annotation_fields
    
    if annotation_name is None:
        annotation_name = unicode(field)
    
    check_model_available(model, logger=wapiti_logger)
    
    corpus_unicode = document.corpus.unicode(fields).encode(encoding)
    
    cmd = [command_name(), "label", "-m", model, "--label"]
    
    wapiti_process     = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    w_stdout, w_stderr = wapiti_process.communicate(input=corpus_unicode)
    
    try:
        if wapiti_process.returncode != 0:
            raise RuntimeError("%s exited with status %i" %(command_name(), wapiti_process.returncode))
    except RuntimeError, re:
        for error_part in [line for line in w_stderr.split(u"\n") if line.strip() != ""]:
            wapiti_logger.error(error_part)
        wapiti_logger.exception(re)
        raise
    
    i    = 0
    j    = 0
    tags = [[]]
    document.corpus.fields.append(field)
    for element in w_stdout.split("\n"):
        element = element.strip()
        if "" == element:
            if len(tags[-1]) > 0:
                tags.append([])
                i += 1
                j  = 0
        else:
            tags[-1].append(element)
            j += 1
    
    tags = [t for t in tags if t]
    document.add_annotation_from_tags(tags, field, annotation_name)
