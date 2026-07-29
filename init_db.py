import sqlite3


conn = sqlite3.connect("instance/media.db")


with open("schema.sql", "r") as file:
    sql_script = file.read()


conn.executescript(sql_script)


conn.close()


print("Database created successfully!")