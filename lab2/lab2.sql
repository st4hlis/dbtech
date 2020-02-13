DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS screenings;
DROP TABLE IF EXISTS theatres;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS tickets;

CREATE TABLE movies (
    movie_title  TEXT,
    year         INT,
    running_time TIME,
    IMDB_key     TEXT DEFAULT (lower(hex(randomblob(16)))),
    PRIMARY KEY (IMDB_key)
);

CREATE TABLE screenings (
    screening_id    TEXT DEFAULT (lower(hex(randomblob(16)))),
    theatre_name    TEXT REFERENCES theatres (theatre_name),
    start_time      DATETIME,
    IMDB_key        TEXT REFERENCES movies (IMDB_key),
    PRIMARY KEY (screening_id)
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
    screening_id    TEXT REFERENCES screenings (screening_id),
    username,       TEXT REFERENCES customers (username),
    PRIMARY KEY (ticket_id)
);

INSERT INTO movies(movie_title, year, running_time) VALUES ("Titanic", 1998, "3:15");
INSERT INTO movies(movie_title, year, running_time) VALUES ("Torkel i knipa", 2004, "1:28");
INSERT INTO movies(movie_title, year, running_time) VALUES ("Fantastic mr Fox", 2009, "1:28");
INSERT INTO movies(movie_title, year, running_time) VALUES ("The Matrix", 1999, "2:30");


INSERT 
INTO    theatres (theatre_name, capacity)
VALUES  ("Filmstaden Lund", 200),
        ("Rigoletto", 100),
        ("Saga", 50);

INSERT INTO customers (username, full_name, password) 
VALUES ("MrHaans", "Artur Lidstrom", "abc123"),
       ("ByggareBob", "Erik Stålberg", "cba321"),
       ("El_oso_panda", "Emanuel Eriksson", "hej123"),
       ("Rotten_tomatoes", "Rutten Tomatsson", "tomater94");