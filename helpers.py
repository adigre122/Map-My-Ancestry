from datetime import datetime
import re
import time
import tkinter
import ttkbootstrap as tb
from tkinter import filedialog
from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser


def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("GEDCOM Files", "*.ged")]) # for GUI
    # file_path = 'SAMPLE.ged'
    
    # Initialize the parser
    gedcom_parser = Parser()
    gedcom_parser.parse_file(file_path, False) # Disable strict parsing

    # Process the selected file
    individuals = []

    for element in gedcom_parser.get_element_list():
        if isinstance(element, IndividualElement):
            individual_info = {
                'name': element.get_name(),
                'birth_date': "Date unknown",
                'birth_place': "Place unknown",
                'death_date': "Date unknown",
                'death_place': "Place unknown",
                'residences': []
            }

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

            individuals.append(individual_info)   

    return individuals

def get_year(date):

    # extract years
    date_formats = [
        r"\b\d{4}\b"  # Matches a 4-digit year
    ]

    # Remove common annotations from the date string
    date = re.sub(r"\b(?:abt|about|circa|around|est)\.?\b", "", date, flags=re.IGNORECASE)

    for date_format in date_formats:
        match = re.search(date_format, date)
        if match:
            year = int(match.group())
            if year <= datetime.now().year:  # Checking if the year is not in the future
                return year


    return None # Return 0 if the date format is not recognized - individual with year 0 will be filtered out as they will be considered deceased

def filter_individuals(slider_year, individuals):
    filtered_individuals = []
    unmapped_individuals = []
    threshold_age = 110  # Set a threshold age to consider someone deceased

    for person in individuals:
        birth_year = get_year(person['birth_date'])
        death_year = get_year(person['death_date']) if person['death_date'] != "Date unknown" else None
        residences = person['residences']
        
        # Remove residences that are None
        residences = [residence for residence in residences if residence[1] != "Place unknown"]

        most_recent_residence = max([res for res in residences if res[0] is not None and res[0] <= slider_year], key=lambda x: x[0], default=None)
        
        # Handle when there is no most recent residence
        if most_recent_residence is not None:
            year, location = most_recent_residence
            person['residences'] = [(year, location)]
        else:
            if birth_year is not None and person['birth_place']:
                person['residences'] = [(birth_year, person['birth_place'])]
            else:
                person['residences'] = [(None, 'No residence found')]

        # Filter out if all information is unknown or missing
        if birth_year is None and death_year is None and most_recent_residence is None:
            unmapped_individuals.append(person)
            continue

        # Filter out if deceased
        if death_year is not None and death_year <= slider_year:
            continue

        # Filter out individuals without birth information who couldn't be alive based on threshold age
        if birth_year is not None and death_year is None:
            if birth_year + threshold_age < slider_year:
                continue
        
        # Check the age threshold for individuals without birth information
        if birth_year is None and death_year is not None and death_year - threshold_age < slider_year:
            continue

        # Filter out individuals who has most recent residence after slider year
        if most_recent_residence is not None and most_recent_residence[0] > slider_year:
            continue

        # Filter out individuals who are likely deceased after living somewhere for threshold age
        if birth_year is None and death_year is None and most_recent_residence is not None:
            if most_recent_residence[0] + threshold_age < slider_year:
                continue

#       **** Handle Individuals to be Filtered ****
        if birth_year is not None and birth_year <= slider_year:
            filtered_individuals.append(person)
                
    return filtered_individuals, unmapped_individuals

def get_location(filtered_individuals):
    markers = []

    for person_data in filtered_individuals:
        if isinstance(person_data, dict):
            name = ' '.join(person_data.get('name', ('', '')))

            residences = person_data.get('residences', [])
            for residence in residences:
                year, location = residence
                if year and location != "Place unknown":
                    markers.append({'location': location, 'year': year, 'text': name})

    return markers
