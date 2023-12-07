# Map My Ancestry

#### Video Demo:  Check out a [demo](https://www.youtube.com/watch?v=sEhbF_0cxUU) to see Map My Ancestry in action.

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

- **Important Things to Consider**: This application will resort to plotting markers of the birthplace of the ancestors if no residential information can be found. Make sure you have a stable internet connection in order to properly use Map My Ancestry.

## Future Versions

Potential enhancements in future releases:
- Preload map for faster processing
- Offline loading of the map tiles
- Buttons to change the map styling

## app.py

**app.py** is the main Python file that establishes the GUI for Map My Ancestry as well as the necessary functions for buttons and crucial features such as uploading a file and parsing it. I decided to keep this file clean and minimal to keep everything organized and easy to read.

## helpers.py

**helpers.py** is the meat and potatoes of this project. I wanted the main functionality to be in a separate file so that everything is organized and easier to debug and read. This was a crucial design choice that I knew would need to be necessary as the logic of parsing was more complicated than I expected it to be. This is because there were a lot of test cases I needed to consider to properly parse the data and only display the correct individuals on the map.

## requirements.txt

**requirements.txt** is a list of all dependencies needed for Map My Ancestry to run properly. Please look at step 2 in the installation process to see how to make sure you have all the dependencies for this project.

## SAMPLE.ged

**SAMPLE.ged** is a sample file I used in the demo to show how the filtering works live. You may look at this file and see how a simple GEDCOM file is structured. During the development stages, I also used my own personal GEDCOM file which is much larger with many different "tags" to ensure that the filtering logic still works and Map My Ancestry can process hundreds and thousands of individuals.

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

This license allows others to remix, tweak, and build upon your work non-commercially, and although their new works must also acknowledge you and be non-commercial, they don’t have to license their derivative works on the same terms.

## Acknowledgments

- [Harvard's CS50](https://cs50.harvard.edu/x/2023/)
- [GEDCOM Parser](https://gedcom.nickreynke.dev/gedcom/index.html)
- [ttkbootstrap](https://github.com/TkinterTtk/ttkbootstrap)
- [tkintermapview](https://github.com/czq142857/tkintermapview)
