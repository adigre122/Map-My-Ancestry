import tkinter
import ttkbootstrap as tb
from tkinter import filedialog




def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("GEDCOM Files", "*.ged")])
    # Process the selected file (parse GEDCOM data, etc.)
    # Your code to handle the uploaded file goes here


