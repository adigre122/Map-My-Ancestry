import time
import tkinter
import ttkbootstrap as tb
from tkinter import filedialog
from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser

# Initialize the parser
gedcom_parser = Parser()


def open_file():
    # file_path = filedialog.askopenfilename(filetypes=[("GEDCOM Files", "*.ged")]) # for GUI
    file_path = '.ged'
    
    # Use gedcom parser
    gedcom_parser.parse_file(file_path, False) # Disable strict parsing

    # Process the selected file
    individuals = []

    for element in gedcom_parser.get_element_list():
        if isinstance(element, IndividualElement):
            individuals.append(element)

    
    locations_by_year = {} # Dictionary to store locations of individuals by year

    

    for i in individuals:
        # Access and print individual's information (adjust based on the attributes you need)
        indi_id = i.get_pointer()
        name = i.get_name()
        
        # Access birth date and place
        birth_date = "Date unknown"
        birth_place = "Place unknown"
        death_date = "Date unknown"
        death_place = "Place unknown"
        
        # Loop through sub-elements to find birth date and place
        for sub_element in i.get_child_elements():

            # Handle birth information
            if sub_element.get_tag() == 'BIRT':
                for sub_sub_element in sub_element.get_child_elements():
                    if sub_sub_element.get_tag() == 'DATE':
                        birth_date = sub_sub_element.get_value()
                    if sub_sub_element.get_tag() == 'PLAC':
                        birth_place = sub_sub_element.get_value()

            # Handle death information
            if sub_element.get_tag() == 'DEAT':
                for sub_sub_element in sub_element.get_child_elements():
                    if sub_sub_element.get_tag() == 'DATE':
                        death_date = sub_sub_element.get_value()
                    if sub_sub_element.get_tag() == 'PLAC':
                        death_place = sub_sub_element.get_value()

            # Handle residences throughout lifetime
            if sub_element.get_tag() == 'RESI':
                print("Processing RESI for", name)  # Debug print
                resi_date = None
                resi_loc = None
                for resi_sub_element in sub_element.get_child_elements():
                    if resi_sub_element.get_tag() == 'DATE':
                        resi_date = resi_sub_element.get_value()
                        # print("Residence Date:", resi_date)  # Debug print
                    if resi_sub_element.get_tag() == 'PLAC':
                        resi_loc = resi_sub_element.get_value()
                        # print("Residence Place:", resi_loc)  # Debug print

                # Populate locations_by_year
                if resi_date and resi_loc:
                    # print("Year:", resi_date, "Location:", resi_loc)  # Debug print
                    locations_by_year.setdefault(name, []).append((resi_date, resi_loc))


        # print("Individual ID:", indi_id)
        # print("Name:", name)
        # print("Birth Date:", birth_date)
        # print("Birth Place:", birth_place)
        # print("Death Date:", death_date)
        # print("Death Place:", death_place)
        # print("Locations by year:", locations_by_year)  # Debug print
        # print("\n")

start_time = time.time()
open_file()
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")


