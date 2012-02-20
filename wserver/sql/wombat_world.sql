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
-- Name: unit; Type: TABLE; Schema: public; Owner: wombat; Tablespace: 
--

CREATE TABLE unit (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    key bytea NOT NULL
);


ALTER TABLE public.unit OWNER TO wombat;

--
-- Name: unit_id_seq; Type: SEQUENCE; Schema: public; Owner: wombat
--

CREATE SEQUENCE unit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.unit_id_seq OWNER TO wombat;

--
-- Name: unit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wombat
--

ALTER SEQUENCE unit_id_seq OWNED BY unit.id;


--
-- Name: unit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: wombat
--

SELECT pg_catalog.setval('unit_id_seq', 1, true);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: wombat
--

ALTER TABLE unit ALTER COLUMN id SET DEFAULT nextval('unit_id_seq'::regclass);


--
-- Data for Name: unit; Type: TABLE DATA; Schema: public; Owner: wombat
--

COPY unit (id, name, key) FROM stdin;
1	Test	\\x0000000000000000000000000000000000000000000000000000000000000000
\.


--
-- Name: unit_pkey; Type: CONSTRAINT; Schema: public; Owner: wombat; Tablespace: 
--

ALTER TABLE ONLY unit
    ADD CONSTRAINT unit_pkey PRIMARY KEY (id);


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

