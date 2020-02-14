DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS screenings;
DROP TABLE IF EXISTS theatres;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS tickets;

CREATE TABLE movies (
    movie_title  TEXT,
    year         INT,
    running_time TIME,
    IMDB_key     TEXT DEFAULT (lower(hex(randomblob(6)))),
    PRIMARY KEY (IMDB_key)
);

CREATE TABLE screenings (
    screening_id    TEXT DEFAULT (lower(hex(randomblob(16)))),
    theatre_name    TEXT,
    start_time      DATETIME,
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
    ticket_id       TEXT DEFAULT (lower(hex(randomblob(16)))),
    screening_id    TEXT,
    username        TEXT,
    PRIMARY KEY (ticket_id),
    FOREIGN KEY (screening_id) REFERENCES screenings(screening_id),
    FOREIGN KEY (username) REFERENCES customers(username)
);

INSERT INTO movies(movie_title, year, running_time, IMDB_key) VALUES 
        ("Titanic",          1998, "3:15", "tt0001"),
        ("Torkel i knipa",   2004, "1:28", "tt0002"),
        ("Fantastic mr Fox", 2009, "1:28", "tt0003"),
        ("The Matrix",       1999, "2:30", "tt0004");


INSERT INTO theatres (theatre_name, capacity) VALUES  
        ("Filmstaden Lund", 200),
        ("Rigoletto", 100),
        ("Saga", 50),
        ("Hasses asfalt och bio", 5);

INSERT INTO screenings(theatre_name, start_time, IMDB_key, screening_id) VALUES 
        ("Saga",                    "2020-02-14 18:00", "tt0001", "sc0001"),
        ("Rigoletto",               "2020-02-16 15:00", "tt0003", "sc0002"),
        ("Hasses asfalt och bio",   "2020-03-02 19:00", "tt0003", "sc0003");

INSERT INTO customers (username, full_name, password) VALUES 
        ("MrHaans",          "Artur Lidstrom",       "abc123"),
        ("ByggareBob",       "Erik Stålberg",        "cba321"),
        ("El_oso_panda",     "Emanuel Eriksson",     "hej123"),
        ("Rotten_tomatoes",   "Rutten Tomatsson",    "tomater94");

INSERT INTO tickets (screening_id, username) VALUES
        ("sc0001", "MrHaans"),
        ("sc0002", "ByggareBob"),
        ("sc0003", "ByggareBob"),
        ("sc0003", "El_oso_panda"),
        ("sc0003", "Rotten_tomatoes"),
        ("sc0003", "MrHaans");
