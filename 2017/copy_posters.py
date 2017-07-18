import csv
import os
import io

from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

with open('Overview.txt') as csvfile:
    reader = csv.reader(csvfile, delimiter = "\t")
    next(reader, None)
    ct = 0
    for row in reader:
        if row[3] != '':
            # if ct == 10:
            #     break
            # ct += 1
            fromPDF = "BOSC_2017_paper_%s.pdf" % row[0]
            toPDF = "%s.pdf" % row[3]

            # open original PDF
            reader=PdfFileReader(open(fromPDF,'rb'), strict=False)
            page = reader.getPage(0)
            # page.scaleTo()

            # scale to letter?
            if page.mediaBox.getWidth() != 612 and page.mediaBox.getHeight() != 792:
                if row[3] == 'A-123':
                    print(" %d x %d " % (page.mediaBox.getWidth(), page.mediaBox.getHeight()))
                    page.scaleTo(580, 770)
                else:
                    page.scaleTo(612, 792)

            packet = io.BytesIO()

            # create a new PDF with Reportlab
            can = canvas.Canvas(packet, pagesize=letter)
            can.drawString(20, 750, row[3])
            can.save()

            #move to the beginning of the StringIO buffer
            packet.seek(0)
            new_pdf = PdfFileReader(packet)
            # read your existing PDF
            output = PdfFileWriter()

            # add the "watermark" (which is the new pdf) on the existing page
            page.mergePage(new_pdf.getPage(0))
            output.addPage(page)


            # # write new PDF
            writer=PdfFileWriter()
            writer.addPage(page)
            outfp = open(os.path.join('.', 'Posters', toPDF),'wb')
            writer.write(outfp)
