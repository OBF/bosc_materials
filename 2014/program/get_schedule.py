#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
try:
    from urllib.request import urlopen, urlretrieve
except ImportError:
    #Python 2
    from urllib2 import urlopen
    from urllib import urlretrieve

url = "http://www.open-bio.org/wiki/BOSC_2014_Schedule?action=raw"
txt_file = "schedule.txt"
tex_file = "schedule.tex"
tsv_file = "schedule.tsv"

if not os.path.isfile(txt_file):
    print("Downloading %s --> %s" % (url, txt_file))
    urlretrieve(url, txt_file)
else:
    print("Using %s cached as %s" % (url, txt_file))

def clean(text):
    text = text.strip().replace("_", r"\_").replace("&", r"\&")
    text = text.replace("é", r"{\'e}")
    if text.startswith("'''") and text.endswith("''':"):
        #Triple single-quotes for bold
        return r"\textbf{%s}:" % text[3:-4].strip()
    elif text.startswith("''") and text.endswith("'':"):
        #Double single-quotes for italics
        return r"\textit{%s}:" % text[2:-3].strip()
    elif text.startswith("'''''") and text.endswith("'''''"):
        #Five single-quotes for bold italics
        return r"\textbf{\textit{%s}}" % text[5:-5].strip()
    elif text.startswith("'''") and text.endswith("'''"):
        #Triple single-quotes for bold
        return r"\textbf{%s}" % text[3:-3].strip()
    elif text.startswith("''") and text.endswith("''"):
        #Double single-quotes for italics
        return r"\textit{%s}" % text[2:-2].strip()
    else:
        return text

def do_latex(handle, fields):
    handle.write(" & ".join(row) + "\\\\\n")


def clean_latex(text):
    text = text.replace(r"{\'e}", "é")
    #Crude - assumes } only used for Latex
    text = text.replace(r"\textit{", "").replace(r"\textbf{", "").replace("}", "")
    assert "{" not in text, text
    return text.strip()

def do_tabs(handle, fields, table):
    #TODO - Remove italics etc...
    if "..." in fields:
        return
    if len(fields) != 3:
        #e.g. coffee break
        return
    times, title, name = [clean_latex(t) for t in fields]
    if times.startswith("P"):
        poster = times
        day, start, end = "", "", ""
    else:
        poster = ""
        try:
            start, end = times.split("-")
        except (IndexError, ValueError) as e:
            sys.stderr.write("Ignoring row %r\n" % fields)
            return
        day = {1: "2014/07/11", 2: "2014/07/12"}[table]

    session = ""
    if title.startswith("["):
        i = title.index("]")
        session = title[1:i].strip()
        title = title[i+1:].strip()
    if title.endswith("]") and "[P" in title:
        assert not poster
        title, poster = title.rsplit(None, 1)

    handle.write("\t".join([day, start, end, poster, session, title, name]) + "\n")

print("Parsing %s --> %s" % (txt_file, tex_file))
with open(txt_file) as input:
    with open(tex_file, "w") as tex_output, open(tsv_file, "w") as tab_output:
        row = []
        table = 0
        for line in input:
            if line.startswith("{|"):
                #New table
                table += 1
                tex_output.write("\\begin{tabular}{lll}\n")
                assert not row
            elif line.startswith("|-"):
                #New row, output \\
                if row:
                    do_latex(tex_output, row)
                    do_tabs(tab_output, row, table)
                row = []
            elif line.startswith("| "):
                #Cell
                row.append(clean(line[2:]))
            elif line.startswith("|}"):
                #End of table
                if row:
                    do_latex(tex_output, row)
                    do_tabs(tab_output, row, table)
                row = []
                tex_output.write("\\end{tabular}\n\n")
print("Done")
