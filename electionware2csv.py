import sys

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import pdfminer

def y(obj):
    return (obj.bbox[1], -len(obj.get_text()))

with open(sys.argv[1], 'rb') as in_file:
    parser = PDFParser(in_file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    current_precinct = None
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
        layout = device.get_result()
        textboxes = []
        for obj in layout._objs:
            # if it's a textbox, print text and location
            if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                textboxes.append(obj)
        textboxes.sort(key=y, reverse=True)
        line_items = False
        last_value = None
        last_heading = None
        precinct = textboxes[4].get_text().strip()
        if current_precinct != precinct:
            print("precinct", precinct)
        current_precinct = precinct
        for textbox in textboxes:
            text = textbox.get_text().strip()
            if text == "TOTAL":
                print()
                print(last_heading.replace("\n", "-"))
                line_items = True
                line = 0
                last_value = None
            elif line_items:
                if last_value is None:
                    if textbox.bbox[0] == 20:
                        line_items = False
                        last_heading = text
                    else:
                        last_value = text
                elif textbox.bbox[0] != 20:
                    line_items = False
                    last_heading = text
                else:
                    print(text, last_value)
                    last_value = None
            else:
                last_heading = text

            # print(textbox.bbox, textbox.get_text().replace('\n', '_'))
        # break
