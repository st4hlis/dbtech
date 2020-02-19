from fastapi import FastAPI
import sqlite3

connection = sqlite3.connect("movies.sqlite")
app  = FastAPI()



# Test stuff

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# Lab stuff

@app.get("/ping",status_code=200)
async def ping():
    return "pong"

@app.post("/reset",status_code=200)
async def reset_database():
    statements = """
            DROP TABLE IF EXISTS movies;
            CREATE TABLE movies (
                movie_title  TEXT,
                year         INT,
                IMDB_key     TEXT DEFAULT (lower(hex(randomblob(6)))),
                PRIMARY KEY (IMDB_key)
            );

            DROP TABLE IF EXISTS screenings;
            CREATE TABLE screenings (
                screening_id    TEXT DEFAULT (lower(hex(randomblob(16)))),
                theatre_name    TEXT,
                start_time      DATETIME,
                IMDB_key        TEXT,
                PRIMARY KEY (screening_id),
                FOREIGN KEY (theatre_name) REFERENCES theatres(theatre_name),
                FOREIGN KEY (IMDB_key) REFERENCES movies(IMDB_key)
            ); 

            DROP TABLE IF EXISTS theatres;
            CREATE TABLE theatres (
                theatre_name    TEXT,
                capacity        INT,
                PRIMARY KEY (theatre_name)
            );

            DROP TABLE IF EXISTS customers;
            CREATE TABLE customers (
                username        TEXT,
                full_name       TEXT,
                password        TEXT,
                PRIMARY KEY (username)
            );

            DROP TABLE IF EXISTS tickets;
            CREATE TABLE tickets (
                ticket_id       TEXT DEFAULT (lower(hex(randomblob(16)))),
                screening_id    TEXT,
                username        TEXT,
                PRIMARY KEY (ticket_id),
                FOREIGN KEY (screening_id) REFERENCES screenings(screening_id),
                FOREIGN KEY (username) REFERENCES customers(username)
            );

            INSERT INTO movies(movie_title, year, IMDB_key) VALUES 
                    ("The Shape of Water",    2017, "tt5580390"),
                    ("Moonlight",             2016, "tt4975722"),
                    ("Spotlight",             2015, "tt1895587"),
                    ("Birdman",               2014, "tt2562232");


            INSERT INTO theatres (theatre_name, capacity) VALUES  
                    ("Kino",     10),
                    ("Södran",   16),
                    ("Skandia", 100);
            """
            
    statements = statements.split(";")
    cursor     = connection.cursor()
    for statement in statements:
        #print(statement+";")
        cursor.execute(statement+";")
        connection.commit()
    cursor.execute(
            """
            INSERT INTO customers (username, full_name, password) VALUES 
                    ("alice",   "Alice",    ?),
                    ("bob",     "Bob",      ?);

            """, [hash("dobido"),hash("whatsinaname")])
    return "OK"

@app.get("/movies")
async def movies():
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT *
        FROM   movies
        """
    )
    print(cursor)
    dictKeys = ["title", "year", "imdbKey"]
    movies   = []
    for row in cursor:
        zipObj = zip(dictKeys, row)
        movies.append(dict(zipObj))
    return movies

@app.get("/movies/{imdbKey}")
async def moviesByKey(imdbKey: str):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * 
        FROM   movies
        WHERE  imdb_key == ?
        """,
        [imdbKey]
    )
    dictKeys = ["title", "year", "imdbKey"]
    movies   = []
    for row in cursor:
        zipObj = zip(dictKeys, row)
        movies.append(dict(zipObj))
    return movies

@app.get("/movies")
async def movies():
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT *
        FROM   movies
        """
    )
    print(cursor)
    dictKeys = ["title", "year", "imdbKey"]
    movies   = []
    for row in cursor:
        zipObj = zip(dictKeys, row)
        movies.append(dict(zipObj))
    return movies


def hash(msg):
    import hashlib
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()


