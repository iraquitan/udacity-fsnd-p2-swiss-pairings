-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Drop database if exist
-- DROP DATABASE IF EXISTS tournament;

-- Create Database
-- CREATE DATABASE tournament;

-- Connect to tournament database
-- \c tournament;

-- Create Players table
CREATE TABLE players (
  id SERIAL PRIMARY KEY,
  first_name VARCHAR(20),
  last_name VARCHAR(30),
  date_created TIMESTAMP DEFAULT current_timestamp
);

-- Create tournament table
-- CREATE TABLE tournament (
--   id SERIAL PRIMARY KEY,
--   num_of_players INTEGER,
--   date_created TIMESTAMP DEFAULT current_timestamp
-- );

-- Create matches table
CREATE TABLE matches (
  id SERIAL PRIMARY KEY,
--   tournament_id INTEGER REFERENCES tournament,
  winner_id INTEGER REFERENCES players,
  loser_id INTEGER REFERENCES players,
  date_created TIMESTAMP DEFAULT current_timestamp
);

-- Create standings view
CREATE VIEW standings AS
    SELECT players.id, players.first_name, players.last_name,
      (SELECT count(matches.id)
       FROM matches
       WHERE players.id = matches.winner_id) AS wins,
      (SELECT count(matches.id)
       FROM matches
       WHERE players.id = matches.winner_id
             OR players.id = matches.loser_id) AS matches_num
    FROM players LEFT JOIN matches
         ON matches.id = players.id
--     GROUP BY players.id
    ORDER BY wins DESC;

-- Trigger
CREATE FUNCTION check_player() RETURNS trigger AS $$
DECLARE
  player1 BOOLEAN;
  player2 BOOLEAN;
BEGIN
  player1 := (SELECT exists(SELECT * FROM players WHERE id = NEW.winner_id));
  player2 := (SELECT exists(SELECT * FROM players WHERE id = NEW.loser_id));
  IF player1 IS FALSE THEN
    RAISE EXCEPTION 'player1 id not in players TABLE';
  ELSIF player2 IS FALSE THEN
    RAISE EXCEPTION 'player2 id not in players TABLE';
  END IF;
  RETURN NEW;
END;
$$ language plpgsql;

CREATE TRIGGER check_player_trg
    BEFORE INSERT OR UPDATE
    ON matches
    FOR EACH ROW
    EXECUTE PROCEDURE check_player();
