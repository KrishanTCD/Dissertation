import os
import gzip
import warnings
from datetime import datetime
from PIL import Image
import glob
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# Suppress warnings (optional)
warnings.filterwarnings('ignore', category=UserWarning, append=True)
class PDFContent:
    def __init__(self, header, content, image_path=None, is_model_summary=False):
        self.header = header
        self.content = content
        self.image_path = image_path
        self.is_model_summary = is_model_summary  # Flag to identify model summary

class PDFSection:
    def __init__(self, section_title):
        self.section_title = section_title
        self.content_objects = []

    def add_content(self, header, content, image_path=None, is_model_summary=False):
        self.content_objects.append(PDFContent(header, content, image_path, is_model_summary))

def dataframe_to_table(dataframe):
    data = [dataframe.columns.values.tolist()] + dataframe.values.tolist()
    return data

def render_dataframe(c, dataframe, x, y, max_width, max_height):
    data = dataframe_to_table(dataframe)
    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    table_width, table_height = table.wrap(0, 0)
    if y - table_height < 50:
        c.showPage()
        y = max_height - 40

    table.drawOn(c, x, y - table_height)

    y -= table_height + 20

    return y

def create_pdf(file_path1, title, banner_path, section_objects):
    # Creating a page
    c = canvas.Canvas(file_path1, pagesize=letter)

    page_width, page_height = letter

    # Setting the title of the PDF
    c.setTitle(title)

    # Drawing the banner on the first page
    if banner_path:
        banner = ImageReader(banner_path)
        # Getting the original dimensions of the banner image
        banner_width, banner_height = Image.open(banner_path).size
        # Calculating the aspect ratio of the banner
        aspect_ratio = banner_height / banner_width
        # Calculating the height based on the aspect ratio and the page width
        banner_height = page_width * aspect_ratio
        c.drawImage(banner, 0, page_height - banner_height, width=page_width, height=banner_height)

    # Moving cursor below the banner
    y = page_height - banner_height - 20

    # fix fonts
    header_font_size = 16
    content_font_size = 12
    c.setFont("Helvetica-Bold", header_font_size)

    for section_obj in section_objects:
        c.setFont("Helvetica-Bold", header_font_size)
        c.drawString(50, y, section_obj.section_title)
        y -= 20

        for content_obj in section_obj.content_objects:
            if y < 150:  # flag to shift stuff to next page
                c.showPage()
                if banner_path:
                    c.drawImage(banner, 0, page_height - banner_height, width=page_width, height=banner_height)
                y = page_height - banner_height - 20

            # header
            c.setFont("Helvetica-Bold", header_font_size - 2)
            c.drawString(50, y, content_obj.header)
            y -= 20

            # content
            if content_obj.is_model_summary:
                summary_text = content_obj.content.as_text()  # Convert the Summary object to text
                lines = summary_text.split('\n')
                for line in lines:
                    if y < 50:
                        c.showPage()
                        if banner_path:
                            c.drawImage(banner, 0, page_height - banner_height, width=page_width, height=banner_height)
                        y = page_height - banner_height - 40
                    c.drawString(50, y, line)
                    y -= 12
            elif isinstance(content_obj.content, pd.DataFrame):
                y = render_dataframe(c, content_obj.content, 50, y, page_width - 100, page_height - 150)
            elif isinstance(content_obj.content, pd.Series):
                lines = content_obj.content.to_string().split('\n')
                for line in lines:
                    if y < 50:
                        c.showPage()
                        if banner_path:
                            c.drawImage(banner, 0, page_height - banner_height, width=page_width, height=banner_height)
                        y = page_height - banner_height - 40
                    c.drawString(50, y, line)
                    y -= 12
            else:
                c.setFont("Helvetica", content_font_size)
                c.drawString(50, y, content_obj.content)
                y -= 20
            # image if it exists
            if content_obj.image_path:
                y -= 20
                img_path = content_obj.image_path
                img = Image.open(img_path)
                img_width, img_height = img.size
                aspect_ratio = img_height / img_width

                # Set the desired width of the image in the PDF
                pdf_img_width = page_width - 100
                pdf_img_height = pdf_img_width * aspect_ratio

                if y - pdf_img_height < 50:  # Flag if there's enough space on the page for the image
                    c.showPage()  # new page
                    if banner_path:
                        c.drawImage(banner, 0, page_height - banner_height, width=page_width, height=banner_height)
                    y = page_height - banner_height - 40  # leavin more space below banner

                img = ImageReader(img_path)
                c.drawImage(img, 50, y - pdf_img_height, width=pdf_img_width, height=pdf_img_height)
                y -= pdf_img_height + 20

        y -= 40  # Add some extra space between sections

    # Save the PDF
    c.save()