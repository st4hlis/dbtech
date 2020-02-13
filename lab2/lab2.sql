CREATE TABLE movies (
    IMDB_key     TEXT,
    movie_title  TEXT,
    year         INT,
    running_time TIME,
    PRIMARY KEY (IMDB_key);
);

CREATE TABLE screening (
    screening_id    TEXT,
    start_time      DATETIME,
    IMDB_key        TEXT REFERENCES movies (IMDB_key),
    theatre_name    TEXT REFERENCES theatres (theatre_name),
    PRIMARY KEY (screening_id);
); 

CREATE TABLE theatres (
    theatre_name    TEXT,
    capacity        INT,
    PRIMARY KEY (theatre_name);
);

CREATE TABLE customers (
    username        TEXT,
    full_name       TEXT,
    password        TEXT,
    PRIMARY KEY (username);
);

CREATE TABLE tickets (
    ticket_id       TEXT,
    screening_id    TEXT,
    username,       TEXT REFERENCES customers (username),
    PRIMARY KEY (ticket_id);
);