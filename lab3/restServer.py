from fastapi import FastAPI
import sqlite3

connection = sqlite3.connect("movies.sqlite")
app  = FastAPI()

def hash(msg):
    import hashlib
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()

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
                screening_id    TEXT DEFAULT (lower(hex(randomblob(6)))),
                theatre_name    TEXT,
                date            DATE,
                time            TIME,
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
                ticket_id       TEXT DEFAULT (lower(hex(randomblob(6)))),
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


            INSERT INTO theatres(theatre_name, capacity) VALUES  
                    ("Kino",     10),
                    ("Södran",   16),
                    ("Skandia", 100);

            INSERT INTO screenings(screening_id, theatre_name, date, time, IMDB_key) VALUES
                    ("sc1", "Kino", "2020-03-02", "19:00", "tt2562232");

                    PRAGMA foreign_keys=ON;
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
    cursor.execute(
            """
            INSERT INTO tickets(ticket_id, screening_id, username) VALUES
                    ("tc1", "sc1", "bob")
            """)
    return "OK"




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
async def movies(title: str = None, year: int = None, imdbKey: str = None):
    whereAnd = {False: " WHERE ", True: " AND "}
    whereUsed = False
    if title   != None:
        query += whereAnd[whereUsed] + "movie_title == '" + title     + "'"
        whereUsed = True
    if year    != None:
        query += whereAnd[whereUsed] + "year == '"        + str(year) + "'"
        whereUsed = True
    if imdbKey != None:
        query += whereAnd[whereUsed] + "IMDB_key == '"    + imdbKey   + "'"
        whereUsed = True
    cursor = connection.cursor()
    cursor.execute(query)
    dictKeys = ["title", "year", "imdbKey"]
    movies   = []
    for row in cursor:
        zipObj = zip(dictKeys, row)
        movies.append(dict(zipObj))
    return movies

@app.post("/performances")
async def postPerformances(imdbKey: str, theatre: str, date: str, time:str):
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO screenings(theatre_name, date, time, IMDB_key) VALUES
        (?, ?, ?, ?)
        """,
        [theatre, date, time, imdbKey]
        )
    return cursor

@app.get("/performances/")
async def getPerformances():
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * 
        FROM   screenings
        """
    )
    dictKeys   = ["screeningId", "theatre", "date", "startTime", "imdbKey"]
    screenings = []
    for row in cursor:
        zipObj = zip(dictKeys, row)
        screenings.append(dict(zipObj))
    for event in screenings:
        cursor.execute(
            """
            SELECT capacity
            FROM   theatres
            WHERE  theatre_name == ?
            """,
            [event["theatre"]]
        )
        totalSeats = cursor.fetchone()
        totalSeats = totalSeats[0]
        freeSeats  = totalSeats - getFreeSeats(event["screeningId"])
        event["freeSeats"] = freeSeats
        cursor.execute(
            """
            SELECT movie_title, year
            FROM   movies
            WHERE  IMDB_key == ?
            """,
            [event["imdbKey"]]
        )
        res = cursor.fetchone()
        event["title"] = res[0]
        event["year"]  = res[1]
    return screenings

@app.get("/freeseats/{screeningId}")
def getFreeSeats(screeningId: str):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT *
        FROM   tickets
        WHERE  screening_id == ?
        """,
        [screeningId]
    )
    return len(cursor.fetchall())

@app.get("/tickets/")
async def getTickets():
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT *
        FROM   tickets
        """
    )
    dictKeys = ["ticket_id", "screening_id", "username"]
    tickets   = []
    for row in cursor:
        zipObj = zip(dictKeys, row)
        tickets.append(dict(zipObj))
    return tickets










