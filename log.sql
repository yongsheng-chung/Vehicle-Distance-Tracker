CREATE TABLE users (id INTEGER, username TEXT NOT NULL, hash TEXT NOT NULL, PRIMARY KEY(id));

CREATE UNIQUE INDEX username ON users (username);

CREATE TABLE records (
id INTEGER,
user_id INTEGER,
date TEXT,
origin_name TEXT,
origin_place_id TEXT,
destination_name TEXT,
destination_place_id,
distance NUMERIC,
duration TEXT,
travel_type TEXT,
FOREIGN KEY(user_id) REFERENCES users(id)
);