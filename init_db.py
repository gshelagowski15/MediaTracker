import sqlite3


connection = sqlite3.connect("instance/media.db")


with open("schema.sql", "r") as file:
    sql_script = file.read()


connection.executescript(sql_script)


connection.close()


print("Database created successfully!")