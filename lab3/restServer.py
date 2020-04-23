from fastapi import FastAPI
import sqlite3
import json

connection = sqlite3.connect("movies.sqlite")
app  = FastAPI()

def hash(msg):
    import hashlib
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()

@app.get("/ping",status_code=200)
async def ping():
    return "pong".strip('\"')

@app.post("/reset",status_code=200)
async def reset_database():
    statements = """
            PRAGMA foreign_keys=OFF;
            DROP TABLE IF EXISTS tickets;
            DROP TABLE IF EXISTS customers;
            DROP TABLE IF EXISTS screenings;
            DROP TABLE IF EXISTS movies;
            DROP TABLE IF EXISTS theatres;
            
           

            CREATE TABLE movies (
                movie_title  TEXT,
                year         INT,
                IMDB_key     TEXT DEFAULT (lower(hex(randomblob(6)))),
                PRIMARY KEY (IMDB_key)
            );

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

            CREATE TABLE theatres (
                theatre_name    TEXT,
                capacity        INT,
                PRIMARY KEY (theatre_name)
            );

            CREATE TABLE customers (
                username        TEXT,
                full_name       TEXT,
                password        TEXT,
                PRIMARY KEY (username)
            );

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
                    ("Kino",     4),
                    ("Södran",   16),
                    ("Skandia", 100);

            INSERT INTO screenings(screening_id, theatre_name, date, time, IMDB_key) VALUES
                    ("sc1", "Skandia", "2020-03-02", "19:00", "tt2562232");

            PRAGMA foreign_keys=ON;
            """
            
    statements = statements.split(";")
    cursor     = connection.cursor()
    for statement in statements:
        cursor.execute(statement+";")
        connection.commit()
    cursor.execute(
            """
            INSERT INTO customers (username, full_name, password) VALUES 
                    ("erik",    "Erik",     ?),
                    ("alice",   "Alice",    ?),
                    ("bob",     "Bob",      ?);
            """, [hash("hej"),hash("dobido"),hash("whatsinaname")])

    connection.commit()

    cursor.execute(
            """
            INSERT INTO tickets(ticket_id, screening_id, username) VALUES
                    ("tc1", "sc1", "erik")
            """)

    connection.commit()
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
    return dict(data=movies)

@app.get("/movies")
async def movies(title: str = None, year: int = None, imdbKey: str = None):
    whereAnd = {False: " WHERE ", True: " AND "}
    whereUsed = False
    query = """
            SELECT *
            FROM   movies
            """
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
        # movies.append(dict(zipObj))
    
    return dict(data=movies)

@app.post("/performances", status_code=201)
async def postPerformances(imdbKey: str, theatre: str, date: str, time:str):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO screenings(theatre_name, date, time, IMDB_key) VALUES
            (?, ?, ?, ?)
            """,
            [theatre, date, time, imdbKey]
            )

        connection.commit()

        cursor.execute(
            """
            SELECT screening_id
            FROM   screenings
            WHERE  rowid = last_insert_rowid();
            """,
        )
        return "/performances/" + str(cursor.fetchone()[0]) # SHOULD RETURN RESOUCE
    except sqlite3.Error:
        return "No such movie or theater"

@app.get("/performances")
async def getPerformances():
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * 
        FROM   screenings
        """
    )
    dictKeys   = ["performanceId", "theater", "date", "startTime", "imdbKey"]
    screenings = []
    for row in cursor:
        zipObj = zip(dictKeys, row)
        screenings.append(dict(zipObj))
    for event in screenings:
        print(event["performanceId"])
        print(await getFreeSeats(event["performanceId"]))
        event["remainingSeats"] = await getFreeSeats(event["performanceId"])
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
    return dict(data=screenings)

@app.get("/freeseats/{screeningId}")
async def getFreeSeats(screeningId: str):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT capacity - coalesce(count(ticket_id), 0)
        FROM   screenings
        LEFT JOIN   tickets
        USING  (screening_id)
        LEFT JOIN   theatres
        USING  (theatre_name)
        WHERE  screening_id = ?
        """,
        [screeningId]
    )
    res = cursor.fetchone()
    if res is None:
        return 0
        
    return res[0]

@app.get("/tickets")
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
    return dict(data=tickets)

@app.get("/customers/{customer_id}/tickets")
async def get_tickets_by_customer(customer_id : str):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT date, time, theatre_name, movie_title, year, count() as NbrOfTickets
        FROM   tickets
        JOIN   screenings
        USING  (screening_id)
        JOIN   movies
        USING  (imdb_key)
        GROUP BY (screening_id)
        HAVING username == ?
        """, [customer_id]
    )
    dictKeys = ["date", "time", "theatre_name","movie_title", "year", "NbrOfTickets"]
    tickets = []
    for row in cursor:
        zipObj = zip(dictKeys,row)
        tickets.append(dict(zipObj))
    return dict(data=tickets)

@app.post("/tickets",status_code=201)
async def postTickets(screening_id: str, user_id: str, password: str):
    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT password
            FROM customers
            WHERE username = ?
            """,
            [user_id]
            )

        if hash(password) != cursor.fetchone()[0]: 
            return "Wrong password"

        if await getFreeSeats(screening_id) == 0: 
            return "No tickets left"
        
        cursor.execute(
            """
            INSERT INTO tickets(screening_id, username) VALUES
            (?, ?)
            """,
            [screening_id, user_id]
            )
        connection.commit()

        cursor.execute(
            """
            SELECT ticket_id
            FROM   tickets
            WHERE  rowid = last_insert_rowid();
            """,
        )
        return "/tickets/" + str(cursor.fetchone()[0])
    except sqlite3.Error:
        return "Error"










