from datetime import datetime
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
    file_path = 'SAMPLE.ged'
    
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
                # print("Processing RESI for", name)  # Debug print
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

            # print(f"Name: {name}, Birth Date: {birth_date}, Death Date: {death_date}")

    return individuals, locations_by_year

        # print("Individual ID:", indi_id)
        # print("Name:", name)
        # print("Birth Date:", birth_date)
        # print("Birth Place:", birth_place)
        # print("Death Date:", death_date)
        # print("Death Place:", death_place)
        # print("Locations by year:", locations_by_year)  # Debug print
        # print("\n")

# start_time = time.time()
# open_file()
# end_time = time.time()
# execution_time = end_time - start_time
# print(f"Execution time: {execution_time} seconds")

def get_year(date):
    try:
        # Try to parse the date and extract the year
        date_object = datetime.strptime(date, "%d %b %Y")
        return date_object.year
    except ValueError:
        pass

    try:
        # Try to parse the date and extract the year in another format
        date_object = datetime.strptime(date, "%b %d %Y")
        return date_object.year
    except ValueError:
        pass

    try:
        # Try to parse the date and extract the year in another format
        date_object = datetime.strptime(date, "%b %Y")
        return date_object.year
    except ValueError:
        pass

    try:
        # Try to parse the date and extract the year in another format
        date_object = datetime.strptime(date, "%Y")
        return date_object.year
    except ValueError:
        pass

    # Return 0 if the date format is not recognized - individual with year 0 will be filtered out as they will be considered deceased
    return 0

# Testing the get_year function
# print(get_year("31 Dec 2000"))  # Should print: 2000
# print(get_year("1 Apr 1935"))  # Should print: 1935
# print(get_year("Feb 1998"))   # Should print: 1998
# print(get_year("1945"))       # Should print: 1945
# print(get_year("Some Invalid Date"))  # Should print: None


def filter_individuals(slider_year, individuals, locations_by_year):
    filtered_individuals = []
    current_year = datetime.now().year  # Get the current year
    threshold_age = 110  # Set a threshold age to consider someone deceased

    for i in individuals:
        birth_year = None
        death_year = None
        residences = []

        # Handle birth and death information
        for sub in i.get_child_elements():
            if sub.get_tag() == 'BIRT':
                for sub_sub in sub.get_child_elements():
                    if sub_sub.get_tag() == 'DATE':
                        birth_year = get_year(sub_sub.get_value())
            if sub.get_tag() == 'DEAT':
                for sub_sub in sub.get_child_elements():
                    if sub_sub.get_tag() == 'DATE':
                        death_year = get_year(sub_sub.get_value())

        # Handle residences
        residence_years = [get_year(res[0]) for res in locations_by_year.get(i, []) if get_year(res[0]) is not None]
        if any(res_year <= slider_year for res_year in residence_years):
            latest_residence = max([res[0] for res in locations_by_year.get(i, []) if get_year(res[0]) <= slider_year])
            latest_residence_location = [res[1] for res in locations_by_year.get(i, []) if res[0] == latest_residence][0]
            residences.append((latest_residence, latest_residence_location))

        # Handle missing residence information
        if not residences:
            birth_date = get_year(f"{birth_year}")
            death_date = get_year(f"{death_year}") if death_year != 9999999999 else "Present"

            for sub_element in i.get_child_elements():
                if sub_element.get_tag() == 'BIRT':
                    for sub_sub_element in sub_element.get_child_elements():
                        if sub_sub_element.get_tag() == 'PLAC':
                            birth_place = sub_sub_element.get_value()

            if birth_date and death_date:
                placeholder_residence = f"From {birth_date} to {death_date} - {birth_place}"
                residences.append((placeholder_residence, "Residence Location Not Found. Using Place of Birth"))

        if death_year != 9999999999 and (birth_year is not None and (death_year is None or birth_year <= slider_year < death_year)):
            filtered_individuals.append((i, birth_year, death_year, residences))

    return filtered_individuals


# start_time = time.time()
# individuals, locations_by_year = open_file()

# filtered_data = filter_individuals(2000, individuals, locations_by_year)
# end_time = time.time()

# execution_time = end_time - start_time
# print(f"Execution time: {execution_time} seconds")

# for person in filtered_data:
#     name = person[0].get_name()
#     birth_year = person[1]
#     death_year = person[2]
#     residence_info = person[3]
#     print(f"Name: {name}, Birth Year: {birth_year}, Death Year: {death_year}, Residence Info: {residence_info}")





