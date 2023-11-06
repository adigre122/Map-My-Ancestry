from datetime import datetime
import re
import time
import tkinter
import ttkbootstrap as tb
from tkinter import filedialog
from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser




def open_file():
    # file_path = filedialog.askopenfilename(filetypes=[("GEDCOM Files", "*.ged")]) # for GUI
    file_path = '.ged'
    
    # Initialize the parser
    gedcom_parser = Parser()
    gedcom_parser.parse_file(file_path, False) # Disable strict parsing

    # Process the selected file
    individuals = []
    locations_by_year = {} # Dictionary to store locations of individuals by year

    for element in gedcom_parser.get_element_list():
        if isinstance(element, IndividualElement):
            individual_info = {}
            individual_info['name'] = element.get_name()
            individual_info['birth_date'] = "Date unknown"
            individual_info['birth_place'] = "Place unknown"
            individual_info['death_date'] = "Date unknown"
            individual_info['death_place'] = "Place unknown"
            individual_info['residences'] = []

            for sub_element in element.get_child_elements():
                
                # Handle birth information
                if sub_element.get_tag() == 'BIRT':
                    for sub_sub_element in sub_element.get_child_elements():
                        if sub_sub_element.get_tag() == 'DATE':
                            individual_info['birth_date'] = sub_sub_element.get_value()
                        if sub_sub_element.get_tag() == 'PLAC':
                            individual_info['birth_place'] = sub_sub_element.get_value()
                            # print(f"Name: {individual_info['name']}, Birth Date: {individual_info['birth_date']}, Birth Place: {individual_info['birth_place']}")

                # Handle death information
                if sub_element.get_tag() == 'DEAT':
                    for sub_sub_element in sub_element.get_child_elements():
                        if sub_sub_element.get_tag() == 'DATE':
                            individual_info['death_date'] = sub_sub_element.get_value()
                        if sub_sub_element.get_tag() == 'PLAC':
                            individual_info['death_place'] = sub_sub_element.get_value()

                # Handle Residences and Years lived there
                if sub_element.get_tag() == 'RESI':
                    resi_date = None
                    resi_loc = None
                    for resi_sub_element in sub_element.get_child_elements():
                        if resi_sub_element.get_tag() == 'DATE':
                            resi_date = get_year(resi_sub_element.get_value())
                        if resi_sub_element.get_tag() == 'PLAC':
                            resi_loc = resi_sub_element.get_value()

                    if resi_date and resi_loc:
                        individual_info['residences'].append((resi_date, resi_loc))
                        locations_by_year.setdefault(individual_info['name'], []).append((resi_date, resi_loc))
            
            individuals.append(individual_info)

    return individuals, locations_by_year


# ***** TEST *****  Load individuals data from GEDCOM
# start_time = time.time()
# individuals, locations_by_year = open_file()

# for i in individuals:
#     print(i)

# for i, loc, in locations_by_year.items():
#     print(f"Individual: {i}, Locations: {loc}")
# end_time = time.time()
# execution_time = end_time - start_time
# print(f"Execution time: {execution_time} seconds")


def get_year(date):

    formats = ["%Y-%m-%d", "%Y-%m", "%d-%m-%Y", "%m-%Y", "%d %b %Y", "%b %d %Y", "%b %Y", "%Y"]

    for date_format in formats:
        try:
            date_object = datetime.strptime(date, date_format)
            return date_object.year
        except ValueError:
            pass

    if "about" in date or "around" in date or "abt" in date:
        match = re.search(r'\d{4}', date)
        if match:
            return int(match.group())

    return 0 # Return 0 if the date format is not recognized - individual with year 0 will be filtered out as they will be considered deceased

# ***** TEST *****  Year parsing
# print(get_year("31 Dec 2000"))  # Should print: 2000
# print(get_year("1 Apr 1935"))  # Should print: 1935
# print(get_year("Feb 1998"))   # Should print: 1998
# print(get_year("1945"))       # Should print: 1945
# print(get_year("Some Invalid Date"))  # Should print: 0


def filter_individuals(slider_year, individuals, locations_by_year):
    filtered_individuals = []
    current_year = datetime.now().year  # Get the current year
    threshold_age = 110  # Set a threshold age to consider someone deceased

    for person in individuals:
        birth_year = get_year(person['birth_date'])
        death_year = get_year(person['death_date']) if person['death_date'] != "Date unknown" else 9999999999
        residences = person['residences']

        # print(f"Birth Year: {birth_year}, Death Year: {death_year}, Slider Year: {slider_year}")  # Debug statement

        if death_year != 9999999999 and (birth_year is not None and (death_year is None or birth_year <= slider_year < death_year)):
            
            # Filter residences based on the slider year
            most_recent_residence = max([res for res in residences if res[0] <= slider_year], key=lambda x: x[0], default=None)
            
            if most_recent_residence:  # Add the most recent residence to the filtered list
                person['residences'] = [most_recent_residence]
                filtered_individuals.append(person)

    return filtered_individuals


# ***** TEST *****  Filter individuals data from GEDCOM based on slider year
# start_time = time.time()
# individuals, locations_by_year = open_file()

# # Replace value with desired slider year for testing
# slider_year = 2000

# filtered_data = filter_individuals(slider_year, individuals, locations_by_year)

# print(f"Filtered individuals for the year {slider_year}:")
# for person in filtered_data:
#     print("Name:", person['name'])
#     print("Birth Date:", person['birth_date'])
#     print("Death Date:", person['death_date'])
#     print("Residences:")
#     for residence in person['residences']:
#         print("   Year:", residence[0])
#         print("   Location:", residence[1])
#     print("-----------------------")

# end_time = time.time()
# execution_time = end_time - start_time
# print(f"Execution time: {execution_time} seconds")






