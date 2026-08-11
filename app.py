from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("instance/media.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
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

        cursor.execute(
            """
            INSERT INTO Media (title, type, rating)
            VALUES (?, ?, ?);
            """,
            (title, media_type, rating)
        )

        media_id = cursor.lastrowid

        for genre in genres:

            cursor.execute(
                """
                INSERT OR IGNORE INTO Genres (name)
                VALUES (?);
                """,
                (genre,)
            )

            cursor.execute(
                """
                SELECT id
                FROM Genres
                WHERE name = ?;
                """,
                (genre,)
            )

            genre_id = cursor.fetchone()["id"]

            cursor.execute(
                """
                INSERT INTO MediaGenres (media_id, genre_id)
                VALUES (?, ?);
                """,
                (media_id, genre_id)
            )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_media.html")

@app.route("/media")
def media_list():
    conn = get_db_connection()
    cursor = conn.cursor()

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

    conn.close()

    return render_template("media_list.html", media=media)

@app.route("/media/<int:media_id>")
def media_detail(media_id):
    conn = get_db_connection()
    cursor = conn.cursor()

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

    conn.close()

    if media is None:
        return "Media not found", 404

    return render_template("media_detail.html", media=media)

@app.route("/media/<int:media_id>/edit", methods=["GET", "POST"])
def edit_media(media_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        media_type = request.form["type"]
        rating = float(request.form["rating"])
        genres = request.form.getlist("genres")

        cursor.execute(
            """
            UPDATE Media
            SET title = ?, type = ?, rating = ?
            WHERE id = ?;
            """,
            (title, media_type, rating, media_id)
        )

        cursor.execute(
            """
            DELETE FROM MediaGenres
            WHERE media_id = ?;
            """,
            (media_id,)
        )

        for genre in genres:
            cursor.execute(
                """
                INSERT OR IGNORE INTO Genres (name)
                VALUES (?);""",
                (genre,)
            )

            genre_id = cursor.execute(
                """
                SELECT id
                FROM Genres
                WHERE name = ?;
                """,
                (genre,)
            ).fetchone()["id"]

            cursor.execute(
                """
                INSERT INTO MediaGenres (media_id, genre_id)
                VALUES (?, ?);
                """,
                (media_id, genre_id)
            )

        conn.commit()
        conn.close()

        return redirect(url_for("media_detail", media_id=media_id))

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

    selected_genres = [genre["name"] for genre in genres]

    conn.close()

    if media is None:
        return "Media not found", 404

    return render_template("edit_media.html", media=media, selected_genres=selected_genres)

@app.route("/media/<int:media_id>/delete", methods=["POST"])
def delete_media(media_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM MediaGenres
        WHERE media_id = ?;
        """,
        (media_id,)
    )

    cursor.execute(
        """
        DELETE FROM Media
        WHERE id = ?;
        """,
        (media_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("media_list"))

@app.route("/search", methods=["GET", "POST"])
def search():

    title = ""
    genre = ""
    media_type = ""
    media = []

    if request.method == "POST":

        title = request.form["title"].strip()
        genre = request.form["genre"]
        media_type = request.form["type"]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Title + Genre + Type
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

        # Title + Genre
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

        # Title + Type
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

        # Genre + Type
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

        # Title only
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

        # Genre only
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

        # Type only
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

        # No filters
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

        conn.close()

        return render_template("search_results.html", media=media, title=title, genre=genre, media_type=media_type)

    return render_template("search.html")

if __name__ == "__main__":
    app.run(debug=True)