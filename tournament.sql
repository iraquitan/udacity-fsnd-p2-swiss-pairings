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
-- \connect tournament;

-- Create Player table
CREATE TABLE players (
  id SERIAL PRIMARY KEY,
  name TEXT,
  date_created TIMESTAMP DEFAULT current_timestamp
);

-- Create tournament table
CREATE TABLE tournaments (
  id SERIAL PRIMARY KEY,
  num_of_players INTEGER,
  date_created TIMESTAMP DEFAULT current_timestamp
);

-- Create Tournament Player table
CREATE TABLE tournament_players (
  id SERIAL PRIMARY KEY,
  player_id INTEGER REFERENCES players,
  tournament_id INTEGER REFERENCES tournaments,
  date_created TIMESTAMP DEFAULT current_timestamp
);

-- Create match table
CREATE TABLE matches (
  id SERIAL PRIMARY KEY,
  tournament_id INTEGER REFERENCES tournaments,
  winner_id INTEGER REFERENCES players,
  loser_id INTEGER REFERENCES players,
  date_created TIMESTAMP DEFAULT current_timestamp
);

-- Create new standings view
CREATE VIEW standings AS
  SELECT tournaments.id AS t_id, players.id AS p_id, players.name,
      (SELECT count(matches.id)
       FROM matches
       WHERE tournament_players.player_id = matches.winner_id
             AND matches.tournament_id = tournament_players.tournament_id
      ) AS wins,
      (SELECT count(matches.id)
       FROM matches
       WHERE (tournament_players.player_id = matches.winner_id
             AND matches.tournament_id = tournament_players.tournament_id)
             OR (tournament_players.player_id = matches.loser_id
                 AND matches.tournament_id = tournament_players.tournament_id)
      ) AS matches_played
    FROM players
      LEFT JOIN tournament_players
        ON players.id = tournament_players.player_id
      LEFT JOIN tournaments
        ON tournaments.id = tournament_players.tournament_id;

-- OMW (Opponent Match Wins)
CREATE VIEW omw AS
  SELECT a.t_id AS omw_tid, a.p_id AS omw_pid, sum(o.wins) AS OMW
  FROM standings AS a
    LEFT JOIN matches ON (
      a.p_id = matches.winner_id OR a.p_id = matches.loser_id) AND a.t_id = matches.tournament_id
    LEFT JOIN standings AS o
      ON a.p_id <> o.p_id AND (o.p_id = matches.winner_id OR o.p_id = matches.loser_id)
    WHERE a.t_id = matches.tournament_id AND a.t_id = o.t_id
  GROUP BY a.p_id, a.t_id;

CREATE VIEW standings_owm AS
  SELECT standings_new.t_id, standings_new.p_id, standings_new.name,
    standings_new.wins, standings_new.matches_played, standings_new.omw
  FROM (standings
    LEFT JOIN omw
      ON omw.omw_tid = standings.t_id AND omw.omw_pid = standings.p_id)
    AS standings_new;

-- Trigger to check if player is participating on tournament
CREATE FUNCTION check_player() RETURNS trigger AS $$
DECLARE
  player1 BOOLEAN;
  player2 BOOLEAN;
BEGIN
  player1 := (SELECT exists(
      SELECT * FROM tournament_players
      WHERE player_id = NEW.winner_id AND tournament_id = NEW.tournament_id));
  player2 := (SELECT exists(
      SELECT * FROM tournament_players
      WHERE player_id = NEW.loser_id AND tournament_id = NEW.tournament_id));
  IF player1 IS FALSE THEN
    RAISE EXCEPTION 'player1 id not in tournament_players TABLE';
  ELSIF player2 IS FALSE THEN
    RAISE EXCEPTION 'player2 id not in tournament_players TABLE';
  END IF;
  RETURN NEW;
END;
$$ language plpgsql;

CREATE TRIGGER check_player_trg
    BEFORE INSERT OR UPDATE
    ON matches
    FOR EACH ROW
    EXECUTE PROCEDURE check_player();

-- Trigger to check if player is participating on tournament
CREATE FUNCTION check_tournament() RETURNS trigger AS $$
DECLARE
  subscribed_players INTEGER;
  num_players INTEGER;
BEGIN
  subscribed_players := (SELECT count(player_id)
                         FROM tournament_players
                         WHERE tournament_id = NEW.tournament_id);
  num_players = (SELECT num_of_players
                 FROM tournaments
                 WHERE tournaments.id = NEW.tournament_id);
  IF subscribed_players >= num_players THEN
    RAISE EXCEPTION 'tournament already full!';
  END IF;
  RETURN NEW;
END;
$$ language plpgsql;

CREATE TRIGGER check_tournament_trg
    BEFORE INSERT OR UPDATE
    ON tournament_players
    FOR EACH ROW
    EXECUTE PROCEDURE check_tournament();
