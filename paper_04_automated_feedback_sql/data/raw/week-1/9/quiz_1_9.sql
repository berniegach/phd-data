--
-- PostgreSQL database dump
--

-- Dumped from database version 14.9 (Ubuntu 14.9-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.9 (Ubuntu 14.9-0ubuntu0.22.04.1)

--
-- Name: teacher; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE teacher (
    teacher_id integer,
    name character varying
);




--
-- Name: theme; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE theme (
    theme_id integer,
    teacher_id integer,
    name character varying
);




--
-- Data for Name: teacher; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO Teacher(teacher_id, name) VALUES(1, 'Patrick van Bommel');
INSERT INTO Teacher(teacher_id, name) VALUES(2, 'Djoerd Hiemstra');
INSERT INTO Theme(theme_id, teacher_id, name) VALUES(1, 1, 'ORM');
INSERT INTO Theme(theme_id, teacher_id, name) VALUES(2, 2, 'SQL');
INSERT INTO Theme(theme_id, teacher_id, name) VALUES(3, 2, 'DB');
INSERT INTO Theme(theme_id, teacher_id, name) VALUES(4, 2, 'IR');


--
-- PostgreSQL database dump complete
--

