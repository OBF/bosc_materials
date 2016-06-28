#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import csv
try:
    from urllib.request import urlopen, urlretrieve
except ImportError:
    #Python 2
    from urllib2 import urlopen
    from urllib import urlretrieve

url = "http://www.open-bio.org/wiki/BOSC_2016_Schedule?action=raw"
txt_file = "schedule.txt"  # temp file from BOSC wiki download
tex_file = "schedule.tex"  # currently unused
abs_file = "abstracts.tex"  # used to add to BOSC2016_abstracts.txt manually
tsv_file = "schedule.tsv"  # currently unused
easychair = "submission.csv"  # input file

if not os.path.isfile(easychair):
    print("Using EasyChair.org, go to Administration, Conference Data Download, ")
    print("View Tables or Download a Subset of Them, CSV Data, tick submission.csv")
    print("Save this file locally as submission.csv")
    easychair = os.devnull

if not os.path.isfile(txt_file):
    print("Downloading %s --> %s" % (url, txt_file))
    urlretrieve(url, txt_file)
else:
    print("Using %s cached as %s" % (url, txt_file))


abstract_pdfs = dict()
for f in os.listdir("."):
    if f.startswith("BOSC2016_a") and f.endswith(".pdf"):
        rest = f[10:]
        if "_" in rest:
            number, rest = rest.split("_", 1)
            try:
                abstract_pdfs[int(number)] = f
            except ValueError:
                pass

def clean_title(title):
    title = title.strip()
    map = {"Reproducibility in computationally intensive workflows with continuous analysis":
           "Reproducible Computational Workflows with Continuous Analysis"}
    if title in map:
        return map[title]
    title = title.replace("-\xc2\xad", "-").replace("\xe2\x80\x93", "-").replace("\\&", "&")
    title = title.replace("<br>", " ").replace("  ", " ")
    return map.get(title, title)

def load_easychair(filename):
    data = {}
    with open(filename, "rb") as handle:
        reader = csv.DictReader(handle, delimiter=',', quotechar='"')
        for row in reader:
            data[clean_title(row["title"]).lower()] = row
    return data
meta = load_easychair(easychair)

def clean(text):
    text = text.replace("\xe2\x80\x93", "-")
    text = text.strip().replace("_", r"\_").replace("&", r"\&")
    text = text.replace("é", r"{\'e}")
    text = text.replace("''' '''", " ")
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

def do_abs(handle, submission_id, title):
    handle.write("%% Abstract %s - %s\n" % (submission_id, title))
    try:
        i = int(submission_id)
        filename = abstract_pdfs.get(i, "MISSING.pdf")
    except ValueError:
        filename = "ERROR.pdf"
    handle.write("\\embed{2.5cm}{2.5cm}{2.5cm}{2.5cm}{%s}\n" % filename)

def do_tabs(handle, abs_handle, fields, table):
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
    if "Pay-your-own-way dinner" in title:
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
        day = {1: "2015/07/10", 2: "2015/07/11"}.get(table, "XXX")

    hacks = {
'[[BOSC\\_2016\\_Panel|Panel: Growing and sustaining open source communities]]':
"Panel: Growing and sustaining open source communities",
"'Keynote''': ''Open source, open access, and open data: why science moves faster in an open world":
"Keynote: Open source, open access, and open data: why science moves faster in an open world",
"'Keynote''': ''The open-source outbreak: can data prevent the next pandemic?":
"Keynote: The open-source outbreak: can data prevent the next pandemic?",
"[[Codefest\_2016|Codefest 2016]] Report":
"Codefest 2016 Report",
}
    if title in hacks:
        title = hacks[title]

    session = ""
    if title in ["Introduction and Welcome", "Lunch", "Announcements", "Registration", "Withdrawn", "Coffee Break", "Codefest 2016 Report", "Concluding Remarks"]:
        return
    if title.startswith("Session: ") or \
       title.startswith("Keynote: ") or \
       title.startswith("Panel: ") or \
       title.startswith("Suggest a BOF") or \
       title.startswith("BOF") or \
       title.startswith("Birds of a Feather") or \
       title.startswith("Concluding remarks") or \
       title.startswith("Poster Session ") or \
       title.startswith("Questions for lightning talk") or \
       title.startswith("Open Bioinformatics Foundation (OBF) Update") or \
       title.startswith("Presentation of Student Travel Awards") or \
       title.startswith("Pay-your-own-way dinner"):
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
        meta_data = meta[clean_title(title).lower()]
    except KeyError:
        sys.stderr.write("Update clean_title? No EasyChair data for: %r\n" % title)
        sys.stderr.write("%r\n" % list(meta.keys()))
        meta_data = dict()

    submission_id = int(meta_data.get("#", 0))
    assert submission_id, title

    handle.write("\t".join([str(submission_id), title, name, day, start, end, session, poster]) + "\n")
    do_abs(abs_handle, submission_id, title)

print("Parsing %s --> %s and %s" % (txt_file, tsv_file, tex_file))
with open(txt_file) as input:
    with open(tex_file, "w") as tex_output, open(tsv_file, "w") as tab_output, open(abs_file, "w") as abs_output:
        row = []
        table = -1
        for line in input:
            if line.startswith("{|"):
                #New table
                table += 1
                tex_output.write("\\begin{tabular}{lll}\n")
                assert not row
            elif line.startswith("|-"):
                #New row, output \\
                if row:
                    #print("Processing row from wiki: %r" % row)
                    do_latex(tex_output, row)
                    do_tabs(tab_output, abs_output, row, table)
                row = []
            elif line.startswith("|}"):
                #End of table
                if row:
                    do_latex(tex_output, row)
                    do_tabs(tab_output, abs_output, row, table)
                row = []
                tex_output.write("\\end{tabular}\n\n")
            elif line.startswith("|"):
                # Cell
                row.append(clean(line[1:]))
print("Done")
