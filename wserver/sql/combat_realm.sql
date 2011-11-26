--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: avatar; Type: TABLE; Schema: public; Owner: combat; Tablespace: 
--

CREATE TABLE avatar (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    world_unit integer NOT NULL,
    world_key bytea NOT NULL,
    world_id integer NOT NULL
);


ALTER TABLE public.avatar OWNER TO combat;

--
-- Name: avatar_id_seq; Type: SEQUENCE; Schema: public; Owner: combat
--

CREATE SEQUENCE avatar_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.avatar_id_seq OWNER TO combat;

--
-- Name: avatar_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: combat
--

ALTER SEQUENCE avatar_id_seq OWNED BY avatar.id;


--
-- Name: avatar_id_seq; Type: SEQUENCE SET; Schema: public; Owner: combat
--

SELECT pg_catalog.setval('avatar_id_seq', 5, true);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: combat
--

ALTER TABLE avatar ALTER COLUMN id SET DEFAULT nextval('avatar_id_seq'::regclass);


--
-- Data for Name: avatar; Type: TABLE DATA; Schema: public; Owner: combat
--

COPY avatar (id, name, world_unit, world_key, world_id) FROM stdin;
1	Test	1	\\x0000000000000000000000000000000000000000000000000000000000000000	1
\.


--
-- Name: avatar_pkey; Type: CONSTRAINT; Schema: public; Owner: combat; Tablespace: 
--

ALTER TABLE ONLY avatar
    ADD CONSTRAINT avatar_pkey PRIMARY KEY (id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

