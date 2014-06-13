#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
try:
    from urllib.request import urlopen, urlretrieve
except ImportError:
    #Python 2
    from urllib2 import urlopen
    from urllib import urlretrieve

url = "http://www.open-bio.org/wiki/BOSC_2014_Schedule?action=raw"
txt_file = "schedule.txt"
tex_file = "schedule.tex"

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
        return r"\textbf{\\textit{%s}}" % text[5:-5].strip()
    elif text.startswith("'''") and text.endswith("'''"):
        #Triple single-quotes for bold
        return r"\textbf{%s}" % text[3:-3].strip()
    elif text.startswith("''") and text.endswith("''"):
        #Double single-quotes for italics
        return r"\textit{%s}" % text[2:-2].strip()
    else:
        return text

print("Parsing %s --> %s" % (txt_file, tex_file))
with open(txt_file) as input:
    with open(tex_file, "w") as output:
        row = []
        for line in input:
            if line.startswith("{|"):
                #New table
                output.write("\\begin{tabular}{lll}\n")
                assert not row
            elif line.startswith("|-"):
                #New row, output \\
                if row:
                    output.write(" & ".join(row) + "\\\\\n")
                row = []
            elif line.startswith("| "):
                #Cell
                row.append(clean(line[2:]))
            elif line.startswith("|}"):
                #End of table
                if row:
                    output.write(" & ".join(row) + "\\\\\n")
                row = []
                output.write("\\end{tabular}\n\n")
print("Done")
