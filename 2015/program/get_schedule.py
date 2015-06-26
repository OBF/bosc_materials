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

url = "http://www.open-bio.org/wiki/BOSC_2015_Schedule?action=raw"
txt_file = "schedule.txt"
tex_file = "schedule.tex"
abs_file = "abstracts.tex"
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


abstract_pdfs = dict()
for f in os.listdir("."):
    if f.endswith(".pdf") and "-" in f:
        number, rest = f.split("-", 1)
        try:
            int(number)
            abstract_pdfs[number] = f
        except ValueError:
            pass
print("Identified %i abstract PDF files" % len(abstract_pdfs))

def load_open_conf(filename):
    data = {}
    with open(filename, "rb") as handle:
        raw = handle.read()
        lines = [line.strip() for line in raw.split("\r\n")]
        header = [t.strip('"').strip() for t in lines.pop(0).split("\t")]
        #header = [t.strip('"').strip() for t in handle.readline().rstrip("\n").split("\t")]
        #print header
        title = header.index("TITLE")
        print("Found title as column %i" % (title+1))
        #for line in handle:
        for line in lines:
            if not line.strip():
                continue
            values = [t.strip('"').strip() for t in line.rstrip("\n").split("\t")]
            if len(values) < title:
                print("Bad line: %r" % line)
                sys.exit(1)
            data[values[title].lower()] = dict(zip(header, values))
    return data
meta = load_open_conf(open_conf)

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
    filename = abstract_pdfs.get(submission_id, "MISSING.pdf")
    handle.write("\\embed{2.5cm}{4cm}{2cm}{2.5cm}{%s}\n" % filename)

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
"[[BOSC\\_2015\\_Panel|Panel: Open Source, Open Door: increasing diversity in the bioinformatics open source community]]":
"Panel: Open Source, Open Door: increasing diversity in the bioinformatics open source community"
}
    if title in hacks:
        title = hacks[title]

    session = ""
    if title in ["Lunch", "Announcements", "Registration", "Withdrawn", "Coffee Break", "Codefest 2015 Report", "Concluding Remarks"]:
        return
    if title.startswith("Session: ") or \
       title.startswith("Keynote: ") or \
       title.startswith("Suggest a BOF") or \
       title.startswith("BOF") or \
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
    #Manual cross-reference hacks
    hacks2 = {
"GOexpress: A R/Bioconductor package for the identification and visualisation of robust gene ontology signatures through supervised learning of gene expression data":
"GOexpress: A R/Bioconductor package for the identification and visualisation of robust gene ontology signatures through supervised clustering of gene expression data",
"COPO: Bridging the Gap from Data to Publication in Plant Science":
"COPO - Bridging the Gap from Data to Publication in Plant Science",
"From Fastq To Drug Recommendation - Automated Cancer Report Generation using OncoRep \\&amp; Omics Pipe":
"From Fastq To Drug Recommendation - Automated Cancer Report Generation using OncoRep & Omics Pipe",
"Research shared: www.researchobject.org":
"Research shared:  www.researchobject.org",
"Portable workflow and tool descriptions with the CWL":
"Portable worflow and tool descriptions with the CWL",
"Apollo: Scalable \\&amp; collaborative curation for improved comparative genomics":
"Apollo: Scalable & collaborative curation for improved comparative genomics",
}
    try:
        if title in hacks2:
            meta_data = meta[hacks2[title].lower()]
        else:
            meta_data = meta[title.lower()]
    except KeyError:
        sys.stderr.write("No OpenConf data for: %r\n" % title)
        meta_data = dict()

    submission_id = meta_data.get("SUBMISSION ID", "?")

    handle.write("\t".join([submission_id, title, name, day, start, end, session, poster]) + "\n")
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
