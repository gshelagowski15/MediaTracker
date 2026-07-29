from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("instance/media.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/add", methods=["GET", "POST"])
def add_media():
    if request.method == "POST":

        title = request.form["title"]
        media_type = request.form["type"]
        rating = float(request.form["rating"])
        genres = request.form.getlist("genres")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO Media (title, type, rating) VALUES (?, ?, ?);", (title, media_type, rating))

        media_id = cursor.lastrowid

        for genre in genres:

            cursor.execute("INSERT OR IGNORE INTO Genres (name) VALUES (?);", (genre,))

            cursor.execute("SELECT id FROM Genres WHERE name = ?;", (genre,))

            genre_id = cursor.fetchone()["id"]

            cursor.execute("INSERT INTO MediaGenres (media_id, genre_id) VALUES (?, ?);", (media_id, genre_id))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_media.html")

@app.route("/media")
def media_list():
    conn = get_db_connection()

    media = conn.execute(
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

    conn.close()

    return render_template("media_list.html", media=media)

if __name__ == "__main__":
    app.run(debug=True)