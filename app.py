from datetime import datetime
import time
import tkinter
import ttkbootstrap as tb
import tkintermapview
from helpers import open_file, filter_individuals, get_location

# Global variable to store the existing markers
existing_markers = []

def open_selected_file():
    global individuals_data
    individuals_data = open_file()  # Load data from the selected file
    
    if individuals_data:
        # Clear existing markers before adding new ones
        clear_markers()

        # By default, show all ancesters living now (current year - 2023)
        marker_current_year = filter_individuals(datetime.now().year, individuals_data) 
        add_markers(map_widget, marker_current_year)  # Display markers

def add_markers(map_widget, individuals):
    global existing_markers
    markers = get_location(individuals)

    for marker in markers:
        location = tkintermapview.convert_address_to_coordinates(marker['location'])
        if location is not None:
            text = marker['text']
            lat, long = location  # Extract latitude and longitude from the tuple
            map_widget.set_marker(lat, long, text=text)
            existing_markers.append((lat, long, text))  # Save marker information
        else:
            print(f"Failed to get location for marker: {marker}")


def clear_markers():
    global existing_markers
    map_widget.delete_all_marker()
    existing_markers = []

# handles text box for year input
def on_year_entry_change(entry):
    try:
        year_value = int(year_entry.get())
        global individuals_data, map_widget
        if year_value > datetime.now().year:
            print("Invalid year. Please enter a valid year.")
        else:
            filtered_data, unmapped_data = filter_individuals(year_value, individuals_data)
            print("Filtered Data:", filtered_data)  # for debugging
            
            clear_markers() # clear existing markers before adding new ones
            add_markers(map_widget, filtered_data)
            print("Markers added successfully") # for debugging
    except Exception as e:
        print(f"An error occurred: {e}")

root = tb.Window(themename="superhero")
root.title("Map My Ancestry Visualizer")
root.geometry(f"{800}x{600}")

label = tb.Label(text="Map My Ancestry", font=("Helvetica", 28), bootstyle="default")
label.pack(pady=50)

# Create a menu bar
menu_bar = tb.Menu(root)
file_menu = tb.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=open_selected_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

# Create entry widget for year input
year_entry = tb.Entry(root)
year_entry.pack()

# Function to validate the input (allow only digits)
validate_cmd = root.register(lambda s: s.isdigit())
year_entry.config(validate="key", validatecommand=(validate_cmd, "%S"))
year_entry.bind("<Return>", on_year_entry_change)

# create map widget
map_widget = tkintermapview.TkinterMapView(root, width=400, height=400, corner_radius=0)
map_widget.pack(fill="both", expand=True)

# Set map to Google Satellite view
map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", max_zoom=22) 

# set current widget position and zoom
map_widget.set_address("Earth")
map_widget.set_zoom(1)

root.mainloop()
