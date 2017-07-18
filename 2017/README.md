# Posters

`copy_posters.py` is a quickly hacked together script which reads the `Overview.txt` file (a simple tab-delim table of Easychair abstracts mapped to talk order or poster assignment), reads the appropriate original PDF from the Easychair PDF dump, then copies to a new folder modifying the filename to the poster ID and adding a simple text box to the PDF in the upper left corner.  Note there are two specific hacks to deal with the odd poster with non-standard margins or page size.  

The resulting individual PDFs were combined into one using Adobe Acrobat, though one could easily use PyPDF2 to do the same.

# Talks

Talk abstracts #'s were based on both day and order.  Abstracts were sorted and file names modified to talk order using a simple script `copy_talks.pl` (yes, Perl), and then combined as above using Adobe Acrobat.

# Compression

Acrobat was initially used for compression as well, but this method was not used in favor of [Nomi's method](http://smallpdf.com/) as it retained the embedded images at higher resolution with better compression.   
The final file is `BOSC2017-complete-program-compressed.pdf`.
