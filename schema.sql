CREATE TABLE IF NOT EXISTS Media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('TV', 'Movie')),
    rating REAL NOT NULL CHECK (rating >= 1 AND rating <= 10)
);


CREATE TABLE IF NOT EXISTS Genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);


CREATE TABLE IF NOT EXISTS MediaGenres (
    media_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,

    PRIMARY KEY (media_id, genre_id),

    FOREIGN KEY (media_id) REFERENCES Media(id),
    FOREIGN KEY (genre_id) REFERENCES Genres(id)
);