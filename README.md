# Map My Ancestry

#### Video Demo:  Check out a [demo](<URL HERE>) to see Map My Ancestry in action.

#### Map My Ancestry is a simple Python application that allows you to visualize the locations of your ancestors on a map based on the information provided by a GEDCOM file and an input year. This application utilizes the 'tkintermapview' library for the map view and 'ttkbootstrap' for styling.

## Installation

1. **Clone the repository:**
   
    ```
    git clone https://github.com/adigre122/Map-My-Ancestry.git
    cd Map-My-Ancestry
    ```
    
2. **Install Dependencies:**

    ```
    pip install -r requirements.txt
    ```

## Usage

**IMPORTANT:** Ensure you have downloaded a GEDCOM file from your ancestry program or website.

1. Run the application:

   ```
   python app.py
   ```

2. **Open GEDCOM File**: Use the "File" menu to open a GEDCOM file and load the family tree data. <br>
  ![open file](https://raw.githubusercontent.com/adigre122/Map-My-Ancestry/Version-1/tutorial.gif)

3. **Input Year**: Enter a specific year in the provided entry box and press Enter to see the locations of your ancestors living in that year. <br>
![input year](https://raw.githubusercontent.com/adigre122/Map-My-Ancestry/Version-1/Year%20Input.gif)

## Features
- **Interactive Map View**: The map view displays markers representing the locations of individuals based on their birthplaces or residences. Use the plus and minus buttons to zoom in or out. You can also use a scroll wheel or pinch/pull gestures on a trackpad to zoom in or out.

- **Location Considerations**: The application considers the years individuals lived to determine if they were living during the user's input year. If so, the Map My Ancestry will consider the ancestors' residential timeline information and birthplace.

- **Important Things to Consider**: This application will resort to plotting markers of the birthplace of the ancestors if no residential information can be found. 

## Future Versions

Potential enhancements in future releases:
- Preload map for faster processing
- Offline loading of the map tiles
- Buttons to change the map styling

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

This license allows others to remix, tweak, and build upon your work non-commercially, and although their new works must also acknowledge you and be non-commercial, they don’t have to license their derivative works on the same terms.

## Acknowledgments

- [Harvard's CS50](https://cs50.harvard.edu/x/2023/)
- [ttkbootstrap](https://github.com/TkinterTtk/ttkbootstrap)
- [tkintermapview](https://github.com/czq142857/tkintermapview)
