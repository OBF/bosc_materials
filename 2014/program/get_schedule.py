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
open_conf = "openconf.tsv"

if not os.path.isfile(open_conf):
    print("Using OpenConf, Export All Submissions, tick all fields, tab separated")
    print("Save this file locally as openconf.tsv")
    open_conf = os.devnull

if not os.path.isfile(txt_file):
    print("Downloading %s --> %s" % (url, txt_file))
    urlretrieve(url, txt_file)
else:
    print("Using %s cached as %s" % (url, txt_file))

def load_open_conf(filename):
    data = {}
    with open(filename) as handle:
        header = [t.strip('"').strip() for t in handle.readline().rstrip("\n").split("\t")]
        #print header
        title = header.index("TITLE")
        for line in handle:
            values = [t.strip('"').strip() for t in line.rstrip("\n").split("\t")]
            data[values[title].lower()] = dict(zip(header, values))
    return data
meta = load_open_conf(open_conf)

def clean(text):
    text = text.replace("\xe2\x80\x93", "-")
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
    elif text.startswith("'''"):
        #Partial bold
        bold = text[3:]
        i = bold.index("'''")
        bold, rest = bold[:i], bold[i+3:]
        return r"\textbf{%s} %s" % (bold.strip(), rest.strip())
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

    if name.startswith("Suggest a BOF topic"):
        return
    if "Pay-your-own-way BOSC dinner" in title:
        return

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

    hacks = {"[[BOSC\\_2014\\_Keynote\\_Speakers|Keynote: A History of Bioinformatics (in the Year 2039)]]" : "A History of Bioinformatics (in the Year 20\
39)",
"[http://www.open-bio.org/wiki/Main\\_Page Open Bioinformatics Foundation (OBF) update]" : "Open Bioinformatics Foundation (OBF) update",
"[[Codefest\\_2014 | Codefest 2014 Report]]": "Codefest 2014 Report",
"| [[BOSC\\_2014\\_Keynote\\_Speakers|Keynote: Biomedical Research as an Open Digital Enterprise]]" : "Biomedical Research as an Open Digital Enterprise",
}
    if title in hacks:
        title = hacks[title]

    session = ""
    if title in ["Lunch", "Announcements", "Registration", "Withdrawn"]:
        return
    if title.startswith("Session: ") or \
       title.startswith("Suggest a BOF") or \
       title.startswith("Poster Session ") or \
       title.startswith("Presentation of Student Travel Awards"):
        return
    if title.startswith("["):
        i = title.index("]")
        session = title[1:i].strip()
        title = title[i+1:].strip()
    if name.endswith("]") and " [P" in name:
        assert not poster
        name, poster = name.strip().rsplit(None, 1)
        assert poster.startswith("[P") and poster.endswith("]")
        poster = poster[1:-1]

    assert title not in ["", "]"], fields
    try:
        meta_data = meta[title.lower()]
    except KeyError:
        sys.stderr.write("No OpenConf data for: %r\n" % title)
        meta_data = dict()

    submission_id = meta_data.get("SUBMISSION ID", "?")

    handle.write("\t".join([submission_id, title, name, day, start, end, session, poster]) + "\n")

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
