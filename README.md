# Media Tracker

Media Tracker is a full stack web application that allows users to keep track of movies and TV shows they have watched. Users can add media to their collection, give each item a rating from 1 to 10, assign genres, search their collection, sort their media, edit existing entries, and delete entries.

The project was built as a personal Computer Science project to practice web development, Python, Flask, SQLite, HTML, CSS, and JavaScript.

## Features

- Add movies and TV shows to the personal collection
- Give each media item a rating from 1 to 10
- Assign multiple genres to each media item
- View all saved media
- Sort media by:
  - Title A-Z
  - Title Z-A
  - Highest rating
  - Lowest rating
- Search media by:
  - Title
  - Genre
  - Type
- View detailed information about individual movies and TV shows
- Edit existing media
- Delete media with a confirmation message
- View the total number of media items in the collection
- View the average rating of the collection
- View the highest rated media on the home page
- Responsive design for smaller screens

## Technologies Used

- **Python** - Main programming language
- **Flask** - Web framework used to build the application
- **SQLite** - Database used to store media and genre information
- **HTML** - Used to structure the web pages
- **CSS** - Used to style and make the application responsive
- **JavaScript** - Used for the delete confirmation
- **Jinja** - Used to dynamically display database information in HTML
- **Git/GitHub** - Used for version control and storing the project

## Requirements

Before running the project make sure you have the following installed:
- Python 3
- Flask
- Git
- VScode or another code editor

SQLite is included with Python, so a separate SQLite installation is not required.

## Setting Up the Project

1. Get the Project

If you are downloading the project from GitHub, clone the repository using:
- git clone https://github.com/gshelagowski15/MediaTracker.git

After cloning the repository, move into the project folder:
- cd MediaTracker

2. Open the Project

Open the project folder in Visual Studio Code.
Make sure you can see the following files and folders:
- app.py
- init_db.py
- schema.sql
- static/
- templates/

3. Create a Virtual Environment

Open a terminal in the project folder and run:
- python -m venv .venv

This creates a virtual environment named .venv.

4. Activate the Virtual Environment

On Windows, run:
- .venv\Scripts\activate

On macOS or Linux, run:
- source .venv/bin/activate

After activation, the terminal should show that the virtual environment is active.

5. Install Flask

With the virtual environment activated, install Flask:
- pip install Flask

## Setting Up the Database

The project uses SQLite to store media and genre information.
Before running the application for the first time, create the database by running:
- python init_db.py

The init_db.py file reads the SQL commands from schema.sql and creates the database tables.

The database is stored at:
- instance/media.db

The database contains three tables:

- Media - Stores movie and TV show information
- Genres - Stores the available genres
- MediaGenres - Connects media items to their genres

You normally only need to run init_db.py when setting up the project for the first time or when the database schema needs to be recreated or updated.

## Running the Application

After installing Flask and setting up the database, run:
- python app.py

Flask will start the development server.

The terminal should display a local address similar to:
- http://127.0.0.1:5000

Open that address in a web browser to use Media Tracker.

## Using the Application

Home:
- The home page provides:
  - The total number of media items
  - The average rating
  - A list of the highest rated media
  - Buttons to add media or search the collection

My Media:
- The My Media page displays all media in the collection as cards.
- Media can be sorted by:
  - Title A-Z
  - Title Z-A
  - Highest rating
  - Lowest rating
- Clicking a media card opens its detailed information.

Add Media:
- The Add Media page allows you to enter:
  - Title
  - Type
  - Rating
  - Genres
- Multiple genres can be selected for a single media item.

Search:
- The Search page allows you to search the collection using:
  - Title
  - Genre
  - Type
- Search results are displayed as media cards.

Media Details:
- The media details page displays:
  - Title
  - Type
  - Rating
  - Genres
- From this page, you can edit or delete the media.
- Deleting media requires a confirmation message.

Edit Media:
- The Edit Media page allows you to update:
  - Title
  - Type
  - Rating
  - Genres
- The existing information is automatically filled into the form.

## Jinja Templates

The HTML files in the templates folder use Jinja, the template engine included with Flask.

Jinja allows Python data from app.py to be displayed dynamically inside HTML.
For example:
- <h1>{{ media["title"] }}</h1>

This displays the title of a media item.

Jinja is also used for conditional statements such as:
- {% if media %}

and loops such as:
- {% for item in media %}

The templates also use Jinja template inheritance.
For example:
- {% extends "base.html" %}

The above allows pages such as home.html, media_list.html, and search.html to reuse the common layout from base.html.

## Git and GitHub

Git is used to keep track of changes to the project, while GitHub can be used to store the project online.

After making changes to the project, the general Git workflow is:
- git add .
- git commit -m "Describe your changes"
- git push

If you have not connected the local project to a GitHub repository yet, create a repository on GitHub and connect the local project to it before using git push.

## Important Files

app.py:
- Contains the Flask application and the routes that control how the website works.

init_db.py:
- Creates the SQLite database using the SQL commands in schema.sql.

schema.sql:
- Contains the SQL commands used to create the database tables.

base.html:
- Contains the shared HTML structure used by the other pages, including the navigation bar and links to the CSS and JavaScript files.

style.css:
- Contains the styling for the entire website, including the layout, colors, media cards, forms, buttons, and responsive design.

script.js:
- Contains the JavaScript used for the delete confirmation.

templates/:
- Contains the HTML pages used by Flask and Jinja.

## Project Structure

```text
MediaTracker/
│
├── app.py
├── init_db.py
├── schema.sql
├── README.md
│
├── instance/
│   └── media.db
│
├── static/
│   ├── style.css
│   └── script.js
│
└── templates/
    ├── base.html
    ├── home.html
    ├── media_list.html
    ├── media_detail.html
    ├── add_media.html
    ├── edit_media.html
    ├── search.html
    └── search_results.html
```

## Author

Gavin Shelagowski

Computer Science Student

This project was created as a personal portfolio project to practice full stack web development and demonstrate skills with Python, Flask, SQLite, HTML, CSS, JavaScript, and Git.