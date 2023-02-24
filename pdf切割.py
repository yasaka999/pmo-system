from PyPDF2 import PdfReader, PdfWriter

infile = '../files/2021学年第一学期九年级英语西湖区期末检测(1).pdf'
outfile = '../files/2021学年第一学期九年级英语西湖区期末检测(1)split.pdf'

pdf_input_left = PdfReader(open(infile, 'rb'))
pdf_input_right = PdfReader(open(infile, 'rb'))
pdf_output = PdfWriter()

page = pdf_input_left.pages[0]
width = float(page.mediabox.width)
height = float(page.mediabox.height)
page_count = pdf_input_left.pages

for i in range(len(page_count)):
    # left page
    page_left = pdf_input_left.pages[i]
    page_left.mediabox.lower_left = (0, 0)
    page_left.mediabox.lower_right = (width/2,0)
    page_left.mediabox.upper_left = (0, height)
    page_left.mediabox.upper_right = (width/2, height)
    pdf_output.add_page(page_left)
    
    # right page
    page_right = pdf_input_right.pages[i]
    page_right.mediabox.lower_left = (width/2, 0)
    page_right.mediabox.lower_right = (width, 0)
    page_right.mediabox.upper_left = (width/2, height)
    page_right.mediabox.upper_right = (width, height)
    pdf_output.add_page(page_right)

pdf_output.write(open(outfile, 'wb'))