import tkinter
from tkinter import *
import tkinter as tk
import tkinter.messagebox as mbox
from PIL import Image, ImageTk
from fpdf import FPDF
import webbrowser
from transformers import pipeline
import spacy
import json
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import textwrap

selected_option = None
# main window created
window = Tk()
window.geometry("1000x700")
window.title("Resume Generator")

def def_start():
    nlp_ner = spacy.load("model-best\content\model-last")

    def create_resume_image(headings, contents, image_path='Untitled_Artwork 3.jpg'):
        name_content = ""
        name_key = ""
        for key, value in contents.items():
            if key.lower() == 'name':
                name_content = value
                name_key = key
                break  # Exit loop once 'Name' content is found

        # Remove 'Name' content from the dictionary
        if name_key:
            contents.pop(name_key)
         # Extract 'Name' content
        name_coordinates = (800, 368)  # Coordinates for 'Name' content

        # Remove 'Name' from the list of headings
        for heading in list(headings):
            if heading.lower() == 'name':
                headings.remove(heading)
        print(headings)
        # Load the image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)

        # Set up drawing context
        draw = ImageDraw.Draw(pil_image)
        font_size = 100
        font = ImageFont.truetype("times.ttf", font_size-30)
        smallfont = ImageFont.truetype("times.ttf", font_size-50)
        namefont= ImageFont.truetype("times.ttf", font_size+100)
        # Set the line height for the content
        line_height = 30

        # Define initial coordinates for headings and contents
        x, y = 868, 1064
        
        draw.text(name_coordinates, name_content, fill=(255, 255, 255), font=namefont)
        headings = list(headings)
        # Write headings and contents on the image
        if len(headings)==4:
            for heading in headings:
                # Write heading
                # Add spacing between headings
                heading_text_width, heading_text_height = draw.textsize(heading, font=font)
                content = contents.get(heading,"")
                wrapped_content = textwrap.fill(content, width=60) 
                content_text_width, content_text_height = draw.textsize(wrapped_content, font=smallfont)
                # Write content if available for the heading
                heading_x = (pil_image.width - heading_text_width) // 2
                content_x = (pil_image.width - content_text_width) // 2
                
                draw.text((heading_x, y), heading, fill=(0,0,128), font=font)
                y += line_height + 200
                draw.text((content_x, y), wrapped_content, fill=(0,0,0), font=smallfont)
                wrapped_content_lines = wrapped_content.split('\n')
                wrapped_content_height = len(wrapped_content_lines) * line_height
                y += wrapped_content_height + 60  # Adjust for multi-line content

                y += line_height * 2 
        elif len(headings)>=5:
            start_x, start_y = 198, 1064
            start_line = (1203,941)
            end_line = (1203,3169)
            draw.line([start_line, end_line], fill=(0, 0, 128), width=5)
            for index, heading in enumerate(headings[:3]):
                # Write heading
                draw.text((start_x, start_y), heading, fill=(0,0,128), font=font)
                content_y = start_y + line_height + 200   # Add spacing between headings

                # Write content if available for the heading
                content = contents.get(heading,"")
                wrapped_content = textwrap.fill(content, width=40)
                draw.text((start_x, content_y), wrapped_content, fill=(0,0,0), font=smallfont)

                content_height = draw.textsize(wrapped_content, font=smallfont)[1]
                #start_y += line_height * (content.count('\n') + 2) + 20 + content_height # Adjust for multi-line content
                start_y = content_y + content_height + 20

                # Add extra space between sections if applicable
                if index == 2:
                    start_y += line_height * 2  # Extra space between sections

            # Write next two headings and contents
            start_x, start_y = 1429, 1064
            for index, heading in enumerate(headings[3:]):
                # Write heading
                draw.text((start_x, start_y), heading, fill=(0,0,128), font=font)
                content_y = start_y + line_height + 200  # Add spacing between headings

                # Write content if available for the heading
                content = contents.get(heading, "")
                wrapped_content = textwrap.fill(content, width=40)
                draw.text((start_x, content_y), wrapped_content, fill=(0,0,0), font=smallfont)

                content_height = draw.textsize(wrapped_content, font=smallfont)[1]

                start_y = content_y + content_height + 20  
                #start_y += line_height * (content.count('\n') + 2) + content_height+20



        # Save the new image
        output_path = 'output_resume.jpg'
        pil_image.save(output_path)

        return output_path

    def def_PDF():
        global basic
        basic = text_enter.get("1.0", END)
        text_generator = pipeline("text-generation", model="gpt2")

        mbox.showinfo("Generating Resume", "Resume generation in progress...")

        generated_text = text_generator(basic, max_length=100, num_return_sequences=1)

        doc = nlp_ner(generated_text[0]['generated_text'])
        recognized_entities = [(ent.text, ent.label_) for ent in doc.ents]

        # Create a new Word document

        headings = set(label for text, label in recognized_entities)

        contents = {}
        for entity, label in recognized_entities:
            if label == 'NAME':
                contents['NAME'] = entity
            elif label == 'DESIGNATION/ABOUT':
                contents['DESIGNATION/ABOUT'] = entity
            elif label == 'SKILLS':
                contents['SKILLS'] = entity
            elif label == 'EXPERIENCE':
                contents['EXPERIENCE'] = entity
            elif label == 'EDUCATION':
                contents['EDUCATION'] = entity
            elif label == 'ACHIEVEMENTS':
                contents['ACHIEVEMENTS'] = entity
            elif label == 'ADDITIONAL INFO':
                contents['ADDITIONAL INFO'] = entity

        for key, value in contents.items():
            contents[key] = value.replace('\n', '')

        print(contents)
        #print(recognized_entities)

        output_image_path = create_resume_image(headings, contents)
        print(f"Resume image saved at: {output_image_path}")


        # Select a template based on the number of labels identified
        """if num_labels >= 3:
            selected_template = "template_2.docx"  # Replace with your template file name or path
        elif num_labels == 3:
            selected_template = "Template_1.docx"  # Replace with your template file name or path
        else:
            selected_template = "Template_2.docx"  # Replace with your template file name or path

        # Load the selected template
        resume_doc = Document(selected_template)
        resume_doc.save("selected_resume.docx")"""

        mbox.showinfo("Resume Generated", "Resume has been generated successfully!")


    f1 = Frame(window, width=1000, height=700)
    f1.propagate(0)
    f1.pack(side='top')

    start1 = tk.Label(f1,text="RESUME GENERATOR", font=("Arial", 50), fg="magenta")  # same way bg
    start1.place(x=120, y=10)

    text_enter = tk.Text(window, height=13, width=48, font=("Arial", 20), bg="light blue", fg="blue", borderwidth=3,relief="solid")
    text_enter.place(x=120, y=110)

    def clear_text():
        text_enter.delete("1.0", END)

        # created button for clear
    clearb = Button(window, text="CLEAR", command=clear_text, font=("Arial", 25), bg="light green", fg="blue",borderwidth=3, relief="raised")
    clearb.place(x=100, y=580)

    pdfb = Button(window, text="GENERATE RESUME", command=def_PDF, font=("Arial", 25), bg="orange", fg="blue",borderwidth=3, relief="raised")
    pdfb.place(x=300, y=590)

start1 = tk.Label(text = "RESUME GENERATOR", font=("Arial", 55), fg="magenta") # same way bg
start1.place(x = 90, y = 10)

# image on the main window
path = "Images/resume_front.png"
# Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
img = ImageTk.PhotoImage(Image.open(path))
# The Label widget is a standard Tkinter widget used to display a text or image on the screen.
panel = tk.Label(window, image = img)
panel.place(x = 340, y = 150)

# created start button
startb = Button(window, text="START",command=def_start,font=("Arial", 30), bg = "light green", fg = "blue", borderwidth=3, relief="raised")
startb.place(x =100 , y =570 )


# function for exiting
def exit_win():
    if mbox.askokcancel("Exit", "Do you want to exit?"):
        window.destroy()

# created exit button
exitb = Button(window, text="EXIT",command=exit_win,font=("Arial", 30), bg = "red", fg = "blue", borderwidth=3, relief="raised")
exitb.place(x =730 , y =570 )


window.protocol("WM_DELETE_WINDOW", exit_win)
window.mainloop()