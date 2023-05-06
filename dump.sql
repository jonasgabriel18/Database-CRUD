--
-- PostgreSQL database dump
--

-- Dumped from database version 15.2
-- Dumped by pg_dump version 15.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE ONLY public.personals DROP CONSTRAINT linkedgym;
ALTER TABLE ONLY public.personals DROP CONSTRAINT personals_pkey;
ALTER TABLE ONLY public.gym DROP CONSTRAINT gym_pkey;
ALTER TABLE public.personals ALTER COLUMN trainer_id DROP DEFAULT;
ALTER TABLE public.gym ALTER COLUMN gym_id DROP DEFAULT;
DROP SEQUENCE public.personals_trainer_id_seq;
DROP TABLE public.personals;
DROP SEQUENCE public.gym_gym_id_seq;
DROP TABLE public.gym;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: gym; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gym (
    gym_id integer NOT NULL,
    gym_name character varying(20) NOT NULL,
    addres character varying(40) NOT NULL,
    opening_time timestamp without time zone NOT NULL,
    closing_time timestamp without time zone NOT NULL,
    CONSTRAINT gym_check CHECK ((closing_time >= opening_time))
);


ALTER TABLE public.gym OWNER TO postgres;

--
-- Name: gym_gym_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gym_gym_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gym_gym_id_seq OWNER TO postgres;

--
-- Name: gym_gym_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gym_gym_id_seq OWNED BY public.gym.gym_id;


--
-- Name: personals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.personals (
    trainer_id integer NOT NULL,
    trainer_name character varying(30) NOT NULL,
    price integer NOT NULL,
    linked_gym integer NOT NULL,
    client_id integer,
    schedule json NOT NULL
);


ALTER TABLE public.personals OWNER TO postgres;

--
-- Name: personals_trainer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.personals_trainer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.personals_trainer_id_seq OWNER TO postgres;

--
-- Name: personals_trainer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.personals_trainer_id_seq OWNED BY public.personals.trainer_id;


--
-- Name: gym gym_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gym ALTER COLUMN gym_id SET DEFAULT nextval('public.gym_gym_id_seq'::regclass);


--
-- Name: personals trainer_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personals ALTER COLUMN trainer_id SET DEFAULT nextval('public.personals_trainer_id_seq'::regclass);


--
-- Data for Name: gym; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: personals; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Name: gym_gym_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gym_gym_id_seq', 1, false);


--
-- Name: personals_trainer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.personals_trainer_id_seq', 1, false);


--
-- Name: gym gym_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gym
    ADD CONSTRAINT gym_pkey PRIMARY KEY (gym_id);


--
-- Name: personals personals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personals
    ADD CONSTRAINT personals_pkey PRIMARY KEY (trainer_id);


--
-- Name: personals linkedgym; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personals
    ADD CONSTRAINT linkedgym FOREIGN KEY (linked_gym) REFERENCES public.gym(gym_id);


--
-- PostgreSQL database dump complete
--

