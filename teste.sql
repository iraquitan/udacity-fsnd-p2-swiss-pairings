INSERT INTO players (first_name, last_name) VALUES ('Iraquitan', 'Filho');
INSERT INTO players (first_name, last_name) VALUES ('Djenifer', 'Paula');
INSERT INTO players (first_name, last_name) VALUES ('Alexandre', 'Gomes');
INSERT INTO players (first_name, last_name) VALUES ('Adan', 'Salazar');

-- SELECT players.id, players.first_name, players.last_name,
--       (SELECT count(matches.id)
--        FROM matches
--        WHERE players.id = matches.winner_id) AS wins,
--       (SELECT count(matches.id)
--        FROM matches
--        WHERE players.id = matches.winner_id
--              OR players.id = matches.loser_id) AS matches_num
--     FROM players LEFT JOIN matches
--          ON matches.id = players.id
--     GROUP BY players.id
--     ORDER BY  wins DESC;

-- DROP VIEW standings;

-- DELETE FROM matches;
INSERT INTO matches (winner_id, loser_id) VALUES (98, 100);
INSERT INTO matches (winner_id, loser_id) VALUES (99, 98);
INSERT INTO matches (winner_id, loser_id) VALUES (1, 4);
-- INSERT INTO matches (winner_id, loser_id) VALUES (2, 3);
-- INSERT INTO matches (winner_id, loser_id) VALUES (2, 1);
-- INSERT INTO matches (winner_id, loser_id) VALUES (3, 4);

INSERT INTO matches (tournament_id, winner_id, loser_id) VALUES (5, 33, 35);

-- SELECT * from standings;

-- SELECT count(id) FROM players;

-- Opponents with same number of wins
SELECT a.p_id AS a_id, b.p_id AS b_id, b.name AS b_name, a.wins
FROM standings AS a LEFT JOIN standings AS b
        ON a.p_id <> b.p_id AND a.t_id = b.t_id
WHERE a.wins = b.wins AND a.p_id = 177 AND a.t_id = 27;

-- Opponents with one win less than player
SELECT a.p_id AS a_id, b.p_id AS b_id, b.name AS b_name, b.wins
FROM standings AS a LEFT JOIN standings AS b
        ON a.p_id <> b.p_id AND a.t_id = b.t_id
WHERE b.wins = a.wins-1 AND a.p_id = 177 AND a.t_id = 27;


SELECT * FROM (SELECT a.p_id AS a_id, b.p_id AS b_id, a.wins
               FROM standings AS a
                 LEFT JOIN standings AS b ON a.p_id < b.p_id
               WHERE a.wins = b.wins) AS swiss;

-- OMW (Opponent Match Wins)
SELECT a.t_id, a.p_id AS a_id, sum(o.wins) AS OMW
FROM standings AS a
  LEFT JOIN matches ON (
    a.p_id = matches.winner_id OR a.p_id = matches.loser_id) AND a.t_id = matches.tournament_id
  LEFT JOIN standings AS o
    ON a.p_id <> o.p_id AND (o.p_id = matches.winner_id OR o.p_id = matches.loser_id)
  WHERE a.t_id = matches.tournament_id AND a.t_id = o.t_id
GROUP BY a.p_id, a.t_id;

-- OMP (Opponent Match Percentage)
SELECT a.id AS a_id, sum(o.wins::FLOAT/(o.matches_num))/count(o.wins) AS OMP
FROM standings AS a
  JOIN matches ON a.id = matches.winner_id OR a.id = matches.loser_id
  JOIN standings AS o
    ON a.id <> o.id AND (o.id = matches.winner_id OR o.id = matches.loser_id)
GROUP BY a.id;

-- Check if value exist on column
SELECT exists(SELECT * FROM players WHERE id = 97);

-- DROP TRIGGER check_player_trg ON matches;

SELECT * FROM standings JOIN
  (SELECT a.t_id, a.p_id AS a_id, sum(o.wins) AS OMW
FROM standings AS a
  LEFT JOIN matches ON (
    a.p_id = matches.winner_id OR a.p_id = matches.loser_id) AND a.t_id = matches.tournament_id
  LEFT JOIN standings AS o
    ON a.p_id <> o.p_id AND (o.p_id = matches.winner_id OR o.p_id = matches.loser_id)
  WHERE a.t_id = matches.tournament_id AND a.t_id = o.t_id
GROUP BY a.p_id, a.t_id) as OMW2 ON OMW2.t_id = standings.t_id AND OMW2.a_id = standings.p_id;

SELECT *
FROM standings_owm WHERE t_id = 21 ORDER BY wins DESC, omw DESC ;