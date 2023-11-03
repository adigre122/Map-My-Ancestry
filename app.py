import tkinter
import ttkbootstrap as tb
import tkintermapview
from helpers import open_file


root = tb.Window(themename="superhero")
root.title("Map My Ancestry Visualizer")
root.geometry(f"{800}x{600}")

label = tb.Label(text="Map My Ancestry", font=("Helvetica", 28), bootstyle="default")
label.pack(pady=50)

# Create a menu bar
menu_bar = tb.Menu(root)
file_menu = tb.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

# create map widget
map_widget = tkintermapview.TkinterMapView(root, width=400, height=400, corner_radius=0)
map_widget.pack(fill="both", expand=True)

# Set map to Google Satellite view
map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22) 

# set current widget position and zoom
map_widget.set_address("Libya")
map_widget.set_zoom(1)

root.mainloop()
