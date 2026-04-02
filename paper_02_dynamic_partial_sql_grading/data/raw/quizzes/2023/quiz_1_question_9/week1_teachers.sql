CREATE TABLE Teacher (
	teacher_id integer,
	name text
);
CREATE TABLE Theme (
	theme_id integer,
	teacher_id integer,
	name text
);

INSERT INTO Teacher VALUES(11, 'Patrick van Bommel');
INSERT INTO Teacher VALUES(12, 'Djoerd Hiemstra');

INSERT INTO Theme VALUES(11, 11, 'ORM');
INSERT INTO Theme VALUES(12, 12, 'SQL');
INSERT INTO Theme VALUES(13, 12, 'DB');
INSERT INTO Theme VALUES(14, 12, 'IR');
