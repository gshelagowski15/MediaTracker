import sqlite3

# Connects to the media database located inside the instance folder
conn = sqlite3.connect("instance/media.db")

# Opens the schema.sql file so the SQL commands can be read from it
with open("schema.sql", "r") as file:

    # Reads the entire SQL file and stores it in sql_script
    sql_script = file.read()

# Runs all of the SQL commands from schema.sql to create the database tables
conn.executescript(sql_script)

# Closes the connection to the database after the setup is finished
conn.close()

print("Database created successfully!")