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
    file_path = 'SAMPLE.ged'
    
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

# ***** TEST *****  Year parsing
# print(get_year("31 Dec 2000"))  # Should print: 2000
# print(get_year("1 Apr 1935"))  # Should print: 1935
# print(get_year("Feb 1998"))   # Should print: 1998
# print(get_year("1945"))       # Should print: 1945
# print(get_year("Some Invalid Date"))  # Should print: 0


def filter_individuals(slider_year, individuals):
    filtered_individuals = []
    unmapped_individuals = []
    threshold_age = 110  # Set a threshold age to consider someone deceased

    for person in individuals:
        birth_year = get_year(person['birth_date'])
        death_year = get_year(person['death_date']) if person['death_date'] != "Date unknown" else None
        residences = person['residences']
        most_recent_residence = max([res for res in residences if res[0] <= slider_year], key=lambda x: x[0], default=None)
        # print(f"Birth Year: {birth_year}, Death Year: {death_year}, Slider Year: {slider_year}")  # Debug statement
        
        # Filter out if all information is unknown or missing
        if birth_year is None and death_year is None and most_recent_residence is None:
            unmapped_individuals.append(person)
            continue

        # Filter out if deceased
        if death_year and death_year <= slider_year:
            continue

        # Filter out individuals without death information who couldn't be alive based on threshold age
        if birth_year and not death_year:
            if birth_year + threshold_age < slider_year:
                continue
        
        # Check the age threshold for individuals without birth information
        if not birth_year and death_year and death_year - threshold_age < slider_year:
            continue


#       **** Handle Cases for Individuals to be Filtered ****

        # Case 1: Lifespan is within the slider year (individual is alive or died after slider year)
        if birth_year is not None and death_year is not None and birth_year <= slider_year and death_year >= slider_year:
            
            # Check for most recent residential information
            if most_recent_residence is not None:
                person['residences'] = [most_recent_residence]
                
            # No residential info, use birth year and birth place instead
            elif most_recent_residence is None and birth_year is not None:
                person['residences'] = [(birth_year, person['birth_place'])] 
            
            filtered_individuals.append(person)


        # Case 2: Birth year is found but death year is not found
        elif birth_year is not None and death_year is None:

            # If the person could plausibly be alive at the slider year based on threshold age
            if birth_year + threshold_age >= slider_year:
                
                # Check for most recent residential information
                if most_recent_residence is not None:
                    person['residences'] = [most_recent_residence]
                
                # No residential info, use birth year and birth place instead
                else:
                    person['residences'] = [(birth_year, person['birth_place'])] 
                
            filtered_individuals.append(person)

        # Case 3: Birth year not found but death year is found
        elif birth_year is None and death_year is not None:

            # If the person could plausibly be alive at the slider year based on threshold age
            if death_year - threshold_age <= slider_year:
            
                # Check for most recent residential information
                if most_recent_residence is not None:
                    person['residences'] = [most_recent_residence]
                
                # No residential info, use birth year and birth place instead
                else:
                    person['residences'] = [(birth_year, person['birth_place'])] 
            
            filtered_individuals.append(person)
        
        # Case 4: No birth or death information found (option to show individuals in GUI later)
        else:
            if birth_year is None and death_year is None:
            
                # Check for most recent residential information
                if most_recent_residence is not None:
                    person['residences'] = [most_recent_residence]
                    filtered_individuals.append(person)
                
                else: # Nothing to go off of, unmap them
                    person['residences'] = [(None, 'No residence found')]
                    unmapped_individuals.append(person)
                
    return filtered_individuals, unmapped_individuals


# ***** TEST *****  Filter individuals data from GEDCOM based on entry year
# start_time = time.time()
# individuals = open_file()

# # Replace value with desired slider year for testing
# entry_year = 2015

# filtered_data, unmapped_data = filter_individuals(entry_year, individuals)

# print(filtered_data)

# # Write filtered data to a file
# with open('filtered_data.txt', 'w') as file:
#     file.write("### Filtered Individuals ###\n")
#     for person in filtered_data:
#         file.write(f"Name: {person['name']}\n")
#         file.write(f"Birth Date: {person['birth_date']}\n")
#         file.write(f"Death Date: {person['death_date']}\n")
#         file.write("Residences:\n")
#         for residence in person['residences']:
#             file.write(f"   Year: {residence[0]}\n")
#             file.write(f"   Location: {residence[1]}\n")
#         file.write("-----------------------\n")

#     file.write("### Unmapped Individuals ###\n")
#     for person in unmapped_data:
#         file.write(f"Name: {person['name']}\n")
#         file.write(f"Birth Date: {person['birth_date']}\n")
#         file.write(f"Death Date: {person['death_date']}\n")
#         file.write("Residences:\n")
#         for residence in person['residences']:
#             file.write(f"   Year: {residence[0]}\n")
#             file.write(f"   Location: {residence[1]}\n")
#         file.write("-----------------------\n")

# end_time = time.time()
# execution_time = end_time - start_time
# print(f"Execution time: {execution_time} seconds")



def get_location(filtered_individuals):
    markers = []
    for person in filtered_individuals:
        try:
            name = ' '.join(person.get('name', ('', '')))  # Combine first and last name into one string
        except Exception as e:
            print(f"Error getting name: {e}")
            print(f"Person data causing the issue: {person}")
            continue  # Skip the current person if an error occurs

        # individual's residence location - text should be name
        for residence in person.get('residences', []):
            year, location = residence  # Unpack the residence tuple
            if year and location != "Place unknown":
                markers.append({'location': location, 'text': name})

    return markers


# ***** TEST *****  get location data from GEDCOM based on entry year
# start_time = time.time()
# individuals_data = open_file()

# # Replace value with desired slider year for testing
# entry_year = 2023

# # Filter individuals based on the entry year
# filtered_data, unmapped_data = filter_individuals(entry_year, individuals_data)

# # Get location markers
# markers = get_location(filtered_data)
# count = 0
# # Print the result
# print("Markers:")
# for marker in markers:
#     print()
#     print(f"Location: {marker['location']}")
#     print(f"Text: {marker['text']}")
#     print()
#     print("-----------------------")
#     count += 1

# print(f"Filtered Count: {count} people")
# end_time = time.time()
# execution_time = end_time - start_time
# print(f"Execution time: {execution_time} seconds")
