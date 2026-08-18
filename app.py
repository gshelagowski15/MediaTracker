from flask import Flask, render_template, request, redirect, url_for
import sqlite3

# Creates the Flask application
app = Flask(__name__)

# Creates a connection to the sqlite database
def get_db_connection():

    # Opens the media.db database file inside the instance folder
    conn = sqlite3.connect("instance/media.db")

    # Allows database rows to be accessed using column names
    conn.row_factory = sqlite3.Row

    # Turn on foreign keys for this database connection
    conn.execute("PRAGMA foreign_keys = ON;")

    # Returns the database connection so the route can use it
    return conn

# Creates the home page route
@app.route("/")
def home():

    # Connects to the database and creates a cursor to run SQL queries
    conn = get_db_connection()
    cursor = conn.cursor()

    # Counts the total number of movies and TV shows in the database
    total_media = cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM Media;
        """
    ).fetchone()["count"]

    # Calculates the average rating of all media in the database
    average_rating = cursor.execute(
        """
        SELECT AVG(rating) AS average
        FROM Media;
        """
    ).fetchone()["average"]

    # Gets the five highest rated media to display on the home page
    # Media.title is also used to sort alphabetically when ratings are tied
    highest_rated = cursor.execute(
        """
        SELECT
            Media.id,
            Media.title,
            Media.type,
            Media.rating,
            GROUP_CONCAT(Genres.name, ', ') AS genres
        FROM Media
        LEFT JOIN MediaGenres
            ON Media.id = MediaGenres.media_id
        LEFT JOIN Genres
            ON MediaGenres.genre_id = Genres.id
        GROUP BY Media.id
        ORDER BY Media.rating DESC, Media.title
        LIMIT 5;
        """
    ).fetchall()

    # Closes the connection to the database
    conn.close()

    # Sends the information from the database to the home.html template
    return render_template("home.html", total_media=total_media, average_rating=average_rating, highest_rated=highest_rated)

# Creates the route used to add a new movie or TV show
@app.route("/add", methods=["GET", "POST"])
def add_media():

    # Check if the user submitted the Add Media form
    if request.method == "POST":

        # Gets the title entered into the form
        title = request.form["title"]

        # Gets the type of media selected in the form
        media_type = request.form["type"]

        # Convert the rating from the form into a decimal number
        rating = float(request.form["rating"])

        # Gets all the genres selected by the user
        genres = request.form.getlist("genres")

        # Connects to the database and creates a cursor to run SQL queries
        conn = get_db_connection()
        cursor = conn.cursor()

        # Adds the new media into the Media table
        cursor.execute(
            """
            INSERT INTO Media (title, type, rating)
            VALUES (?, ?, ?);
            """,
            (title, media_type, rating)
        )

        # Gets the id that SQLite created for the new media
        media_id = cursor.lastrowid

        # Adds each selected genre to the database
        for genre in genres:

            # Adds the genre to the Genres table if it does not already exist
            cursor.execute(
                """
                INSERT OR IGNORE INTO Genres (name)
                VALUES (?);
                """,
                (genre,)
            )

            # Finds the id of the genre that was just added or already existed
            cursor.execute(
                """
                SELECT id
                FROM Genres
                WHERE name = ?;
                """,
                (genre,)
            )

            # Stores the genre's id so it can be connected to the media
            genre_id = cursor.fetchone()["id"]

            # Connects the media and genre through the MediaGenres table
            cursor.execute(
                """
                INSERT INTO MediaGenres (media_id, genre_id)
                VALUES (?, ?);
                """,
                (media_id, genre_id)
            )

        # Saves all of the changes made to the database and then closes the connection
        conn.commit()
        conn.close()

        # Sends the user back to the home page after adding the media
        return redirect("/")

    # If the user has not submitted the form yet then display the Add Media page
    return render_template("add_media.html")

# Creates the route used to display all of the user's media
@app.route("/media")
def media_list():

    # Gets the sorting option from the URL
    # If no sorting option was provided then sort titles from A to Z
    sort = request.args.get("sort", "title_asc")

    # Connects to the database and creates a cursor to run SQL queries
    conn = get_db_connection()
    cursor = conn.cursor()

    # This variable will contain the SQL used to sort the results
    order_by = ""

    # Sort titles from Z to A
    if sort == "title_desc":
        order_by = "Media.title DESC"

    # Sort media from highest rating to lowest rating
    elif sort == "rating_desc":
        order_by = "Media.rating DESC, Media.title"

    # Sort media from lowest rating to highest rating
    elif sort == "rating_asc":
        order_by = "Media.rating ASC, Media.title"

    # If none of the above then sort titles from A to Z
    else:
        order_by = "Media.title ASC"

    # Gets all media and their associated genres from the database
    media = cursor.execute(
        f"""
        SELECT
            Media.id,
            Media.title,
            Media.type,
            Media.rating,
            GROUP_CONCAT(Genres.name, ', ') AS genres
        FROM Media
        LEFT JOIN MediaGenres
            ON Media.id = MediaGenres.media_id
        LEFT JOIN Genres
            ON MediaGenres.genre_id = Genres.id
        GROUP BY Media.id
        ORDER BY {order_by};
        """
    ).fetchall()

    # Closes the connection to the database
    conn.close()

    # Sends the media and current sorting option to the media list template
    return render_template("media_list.html", media=media, sort=sort)

# Creates the route used to display the details of a selected media
@app.route("/media/<int:media_id>")
def media_detail(media_id):

    # Connects to the database and creates a cursor to run SQL queries
    conn = get_db_connection()
    cursor = conn.cursor()

    # Finds the selected media with the id from the URL
    # GROUP_CONCAT combines all of its genres into one string
    media = cursor.execute(
        """
        SELECT
            Media.id,
            Media.title,
            Media.type,
            Media.rating,
            GROUP_CONCAT(Genres.name, ', ') AS genres
        FROM Media
        LEFT JOIN MediaGenres
            ON Media.id = MediaGenres.media_id
        LEFT JOIN Genres
            ON MediaGenres.genre_id = Genres.id
        WHERE Media.id = ?
        GROUP BY Media.id;
        """,
        (media_id,)
    ).fetchone()

    # Closes the connection to the database
    conn.close()

    # If no media was found with that id then return a 404 error
    if media is None:
        return "Media not found", 404

    # Displays the media details using the media_detail.html template
    return render_template("media_detail.html", media=media)

# Creates the route used to edit an existing media item
@app.route("/media/<int:media_id>/edit", methods=["GET", "POST"])
def edit_media(media_id):

    # Connects to the database and creates a cursor to run SQL queries
    conn = get_db_connection()
    cursor = conn.cursor()

    # Checks if the user submitted the edit form
    if request.method == "POST":

        # Gets the updated information from the form
        title = request.form["title"]
        media_type = request.form["type"]
        rating = float(request.form["rating"])
        genres = request.form.getlist("genres")

        # Updates the media information in the Media table
        cursor.execute(
            """
            UPDATE Media
            SET title = ?, type = ?, rating = ?
            WHERE id = ?;
            """,
            (title, media_type, rating, media_id)
        )

        # Removes the old genre relationships for this media item
        # They will be replaced with the genres selected in the edit form
        cursor.execute(
            """
            DELETE FROM MediaGenres
            WHERE media_id = ?;
            """,
            (media_id,)
        )

        # Adds each newly selected genre
        for genre in genres:

            # Adds the genre if it does not already exist
            cursor.execute(
                """
                INSERT OR IGNORE INTO Genres (name)
                VALUES (?);""",
                (genre,)
            )

            # Finds the id of the genre
            genre_id = cursor.execute(
                """
                SELECT id
                FROM Genres
                WHERE name = ?;
                """,
                (genre,)
            ).fetchone()["id"]

            # Connects the genre to the media item
            cursor.execute(
                """
                INSERT INTO MediaGenres (media_id, genre_id)
                VALUES (?, ?);
                """,
                (media_id, genre_id)
            )

        # Saves all of the changes made to the database and then closes the connection
        conn.commit()
        conn.close()

        # Returns to the detail page for the media item that was edited
        return redirect(url_for("media_detail", media_id=media_id))

    # Gets the basic information for the media item being edited
    media = cursor.execute(
        """
        SELECT
            Media.id,
            Media.title,
            Media.type,
            Media.rating
        FROM Media
        WHERE Media.id = ?;
        """,
        (media_id,)
    ).fetchone()

    # Get all of the genres currently connected to the media item
    genres = cursor.execute(
        """
        SELECT Genres.name
        FROM Genres
        JOIN MediaGenres
            ON Genres.id = MediaGenres.genre_id
        WHERE MediaGenres.media_id = ?;
        """,
        (media_id,)
    ).fetchall()

    # Creates a list of the names of the selected genres
    selected_genres = [genre["name"] for genre in genres]

    # Closes the connection to the database
    conn.close()

    # If no media was found with that id then return a 404 error
    if media is None:
        return "Media not found", 404

    # Displays the edit form with the current media information
    return render_template("edit_media.html", media=media, selected_genres=selected_genres)

# Creates the route used to delete a media item
@app.route("/media/<int:media_id>/delete", methods=["POST"])
def delete_media(media_id):

    # Connects to the database and creates a cursor to run SQL queries
    conn = get_db_connection()
    cursor = conn.cursor()

    # Deletes the relationships between the media item and its genres
    cursor.execute(
        """
        DELETE FROM MediaGenres
        WHERE media_id = ?;
        """,
        (media_id,)
    )

    # Deletes the media item from the Media table
    cursor.execute(
        """
        DELETE FROM Media
        WHERE id = ?;
        """,
        (media_id,)
    )

    # Saves all of the changes made to the database and then closes the connection
    conn.commit()
    conn.close()

    # Returns the user to the My Media page
    return redirect(url_for("media_list"))

# Creates the search route
# This route accepts GET requests to display the search form
# and POST requests to process a search
@app.route("/search", methods=["GET", "POST"])
def search():

    # Starts with empty search values and an empty list of results
    title = ""
    genre = ""
    media_type = ""
    media = []

    # Checks if the user submitted the search form
    if request.method == "POST":

        # Gets the search values entered or selected by the user
        title = request.form["title"].strip()
        genre = request.form["genre"]
        media_type = request.form["type"]

        # Connects to the database and creates a cursor to run SQL queries
        conn = get_db_connection()
        cursor = conn.cursor()

        # Search using title + genre + type filters
        if title and genre and media_type:
            media = cursor.execute(
                """
                SELECT
                    Media.id,
                    Media.title,
                    Media.type,
                    Media.rating,
                    GROUP_CONCAT(Genres.name, ', ') AS genres
                FROM Media
                JOIN MediaGenres
                    ON Media.id = MediaGenres.media_id
                JOIN Genres
                    ON MediaGenres.genre_id = Genres.id
                WHERE Media.title LIKE ?
                    AND Genres.name = ?
                    AND Media.type = ?
                GROUP BY Media.id
                ORDER BY Media.title;
                """,
                (f"%{title}%", genre, media_type)
            ).fetchall()

        # Search using title + genre filters
        elif title and genre:
            media = cursor.execute(
                """
                SELECT
                    Media.id,
                    Media.title,
                    Media.type,
                    Media.rating,
                    GROUP_CONCAT(Genres.name, ', ') AS genres
                FROM Media
                JOIN MediaGenres
                    ON Media.id = MediaGenres.media_id
                JOIN Genres
                    ON MediaGenres.genre_id = Genres.id
                WHERE Media.title LIKE ?
                    AND Genres.name = ?
                GROUP BY Media.id
                ORDER BY Media.title;
                """,
                (f"%{title}%", genre)
            ).fetchall()

        # Search using title + type filters
        elif title and media_type:
            media = cursor.execute(
                """
                SELECT
                    Media.id,
                    Media.title,
                    Media.type,
                    Media.rating,
                    GROUP_CONCAT(Genres.name, ', ') AS genres
                FROM Media
                LEFT JOIN MediaGenres
                    ON Media.id = MediaGenres.media_id
                LEFT JOIN Genres
                    ON MediaGenres.genre_id = Genres.id
                WHERE Media.title LIKE ?
                    AND Media.type = ?
                GROUP BY Media.id
                ORDER BY Media.title;
                """,
                (f"%{title}%", media_type)
            ).fetchall()

        # Search using genre + type filters
        elif genre and media_type:
            media = cursor.execute(
                """
                SELECT
                    Media.id,
                    Media.title,
                    Media.type,
                    Media.rating,
                    GROUP_CONCAT(Genres.name, ', ') AS genres
                FROM Media
                JOIN MediaGenres
                    ON Media.id = MediaGenres.media_id
                JOIN Genres
                    ON MediaGenres.genre_id = Genres.id
                WHERE Genres.name = ?
                    AND Media.type = ?
                GROUP BY Media.id
                ORDER BY Media.title;
                """,
                (genre, media_type)
            ).fetchall()

        # Search using title only
        elif title:
            media = cursor.execute(
                """
                SELECT
                    Media.id,
                    Media.title,
                    Media.type,
                    Media.rating,
                    GROUP_CONCAT(Genres.name, ', ') AS genres
                FROM Media
                LEFT JOIN MediaGenres
                    ON Media.id = MediaGenres.media_id
                LEFT JOIN Genres
                    ON MediaGenres.genre_id = Genres.id
                WHERE Media.title LIKE ?
                GROUP BY Media.id
                ORDER BY Media.title;
                """,
                (f"%{title}%",)
            ).fetchall()

        # Search using genre filter only
        elif genre:
            media = cursor.execute(
                """
                SELECT
                    Media.id,
                    Media.title,
                    Media.type,
                    Media.rating,
                    GROUP_CONCAT(Genres.name, ', ') AS genres
                FROM Media
                JOIN MediaGenres
                    ON Media.id = MediaGenres.media_id
                JOIN Genres
                    ON MediaGenres.genre_id = Genres.id
                WHERE Genres.name = ?
                GROUP BY Media.id
                ORDER BY Media.title;
                """,
                (genre,)
            ).fetchall()

        # Search using type filter only
        elif media_type:
            media = cursor.execute(
                """
                SELECT
                    Media.id,
                    Media.title,
                    Media.type,
                    Media.rating,
                    GROUP_CONCAT(Genres.name, ', ') AS genres
                FROM Media
                LEFT JOIN MediaGenres
                    ON Media.id = MediaGenres.media_id
                LEFT JOIN Genres
                    ON MediaGenres.genre_id = Genres.id
                WHERE Media.type = ?
                GROUP BY Media.id
                ORDER BY Media.title;
                """,
                (media_type,)
            ).fetchall()

        # If the user submits the form without selecting any filters then display every media item
        else:
            media = cursor.execute(
                """
                SELECT
                    Media.id,
                    Media.title,
                    Media.type,
                    Media.rating,
                    GROUP_CONCAT(Genres.name, ', ') AS genres
                FROM Media
                LEFT JOIN MediaGenres
                    ON Media.id = MediaGenres.media_id
                LEFT JOIN Genres
                    ON MediaGenres.genre_id = Genres.id
                GROUP BY Media.id
                ORDER BY Media.title;
                """
            ).fetchall()

        # Closes the connection to the database
        conn.close()

        # Displays the search results and the filters used for the search
        return render_template("search_results.html", media=media, title=title, genre=genre, media_type=media_type)

    # If the user has not submitted a search yet then display the search form
    return render_template("search.html")

# Starts the Flask development server when this file is run directly
if __name__ == "__main__":

    # Runs the application in debug mode so errors and code changes
    # are easier to see while developing the project
    app.run(debug=True)