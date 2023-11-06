--
-- PostgreSQL database dump
--

-- Dumped from database version 16.0
-- Dumped by pg_dump version 16.0

-- Started on 2023-11-04 16:53:20

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

--
-- TOC entry 4942 (class 1262 OID 16398)
-- Name: malvert_db; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE malvert_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_United States.1252';


ALTER DATABASE malvert_db OWNER TO postgres;

\connect malvert_db

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

--
-- TOC entry 5 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 863 (class 1247 OID 16400)
-- Name: url_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.url_type AS ENUM (
    'other',
    'malvert',
    'legit'
);


ALTER TYPE public.url_type OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 215 (class 1259 OID 16407)
-- Name: campaigns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.campaigns (
    campaign character varying(512) NOT NULL,
    last_seen timestamp without time zone
);


ALTER TABLE public.campaigns OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 16412)
-- Name: desktop_detailed_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.desktop_detailed_logs (
    url_id bigint,
    iteration bigint,
    info character varying,
    target_url character varying,
    landing_url character varying,
    url character varying,
    "timestamp" timestamp without time zone,
    log_id integer NOT NULL
);


ALTER TABLE public.desktop_detailed_logs OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16417)
-- Name: desktop_detailed_logs_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.desktop_detailed_logs_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.desktop_detailed_logs_log_id_seq OWNER TO postgres;

--
-- TOC entry 4944 (class 0 OID 0)
-- Dependencies: 217
-- Name: desktop_detailed_logs_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.desktop_detailed_logs_log_id_seq OWNED BY public.desktop_detailed_logs.log_id;


--
-- TOC entry 218 (class 1259 OID 16418)
-- Name: detailed_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.detailed_logs (
    url_id bigint,
    iteration bigint,
    info character varying,
    target_url character varying,
    landing_url character varying,
    url character varying,
    "timestamp" timestamp without time zone,
    log_id integer NOT NULL
);


ALTER TABLE public.detailed_logs OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16423)
-- Name: detailed_logs_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.detailed_logs_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.detailed_logs_log_id_seq OWNER TO postgres;

--
-- TOC entry 4945 (class 0 OID 0)
-- Dependencies: 219
-- Name: detailed_logs_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.detailed_logs_log_id_seq OWNED BY public.detailed_logs.log_id;


--
-- TOC entry 220 (class 1259 OID 16424)
-- Name: domains_seen; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.domains_seen (
    domain character varying(512),
    campaign character varying(512),
    first_seen timestamp without time zone,
    last_seen timestamp without time zone
);


ALTER TABLE public.domains_seen OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16429)
-- Name: gsb; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gsb (
    domain character varying(6000),
    first_query_time timestamp without time zone,
    first_flag boolean,
    first_se_flag boolean,
    first_result text,
    last_query_time timestamp without time zone,
    last_flag boolean,
    last_se_flag boolean,
    last_result text
);


ALTER TABLE public.gsb OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16434)
-- Name: mobile_detailed_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mobile_detailed_logs (
    pid bigint,
    info character varying,
    target_url character varying,
    landing_url character varying,
    url character varying,
    "timestamp" timestamp without time zone,
    log_id integer NOT NULL
);


ALTER TABLE public.mobile_detailed_logs OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16439)
-- Name: mobile_detailed_logs_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mobile_detailed_logs_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mobile_detailed_logs_log_id_seq OWNER TO postgres;

--
-- TOC entry 4946 (class 0 OID 0)
-- Dependencies: 223
-- Name: mobile_detailed_logs_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mobile_detailed_logs_log_id_seq OWNED BY public.mobile_detailed_logs.log_id;


--
-- TOC entry 224 (class 1259 OID 16440)
-- Name: notification_details; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_details (
    sw_url_id bigint,
    notification_title character varying(300),
    notification_body character varying,
    target_url character varying,
    image_url character varying,
    sw_url character varying,
    "timestamp" timestamp without time zone,
    notification_id bigint NOT NULL
);


ALTER TABLE public.notification_details OWNER TO postgres;


CREATE TABLE page_requests (
    sw_url_id bigint,            
    frame_url character varying,   
    local_url character varying,  
    request_url character varying, 
    "timestamp" timestamp without time zone     
);

--
-- TOC entry 225 (class 1259 OID 16445)
-- Name: notification_details_distinct; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.notification_details_distinct AS
 SELECT DISTINCT sw_url_id,
    notification_title,
    notification_body,
    target_url,
    image_url,
    sw_url,
    "timestamp"
   FROM public.notification_details;


ALTER VIEW public.notification_details_distinct OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16449)
-- Name: notification_details_notification_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_details_notification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notification_details_notification_id_seq OWNER TO postgres;

--
-- TOC entry 4947 (class 0 OID 0)
-- Dependencies: 226
-- Name: notification_details_notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_details_notification_id_seq OWNED BY public.notification_details.notification_id;


--
-- TOC entry 227 (class 1259 OID 16450)
-- Name: notifications; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.notifications AS
 SELECT url_id,
    info,
    landing_url,
    "timestamp",
    row_number() OVER (ORDER BY "timestamp") AS id
   FROM public.desktop_detailed_logs
  WHERE (((info)::text ~~ '%Notification click%'::text) OR ((info)::text ~~ '%Notification shown%'::text));


ALTER VIEW public.notifications OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16454)
-- Name: resource_info; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resource_info (
    url_id bigint,
    iteration integer,
    file_name character varying,
    file_hash character varying,
    resource_id integer NOT NULL
);


ALTER TABLE public.resource_info OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16459)
-- Name: resource_info_resource_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.resource_info_resource_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resource_info_resource_id_seq OWNER TO postgres;

--
-- TOC entry 4948 (class 0 OID 0)
-- Dependencies: 229
-- Name: resource_info_resource_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.resource_info_resource_id_seq OWNED BY public.resource_info.resource_id;


--
-- TOC entry 230 (class 1259 OID 16460)
-- Name: seed_urls; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.seed_urls (
    seed_url_id integer NOT NULL,
    seed_url character varying NOT NULL,
    seed_keyword character varying,
    is_visited boolean,
    has_permission_request boolean,
    is_analyzed_desktop boolean,
    is_analyzed_mobile boolean,
    trust_score bigint DEFAULT 0,
    visit_status integer DEFAULT 0,
    app_server_key character varying,
    auth_secret character varying,
    endpoint character varying
);


ALTER TABLE public.seed_urls OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16467)
-- Name: seed_urls_seed_url_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.seed_urls_seed_url_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.seed_urls_seed_url_id_seq OWNER TO postgres;

--
-- TOC entry 4949 (class 0 OID 0)
-- Dependencies: 231
-- Name: seed_urls_seed_url_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.seed_urls_seed_url_id_seq OWNED BY public.seed_urls.seed_url_id;


--
-- TOC entry 232 (class 1259 OID 16468)
-- Name: service_worker_details; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_worker_details (
    sw_url_id bigint,
    sw_url character varying,
    target_url character varying,
    "timestamp" timestamp without time zone,
    sw_event character varying,
    sw_id bigint NOT NULL
);


ALTER TABLE public.service_worker_details OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 16473)
-- Name: service_worker_details_sw_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.service_worker_details_sw_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_worker_details_sw_id_seq OWNER TO postgres;

--
-- TOC entry 4950 (class 0 OID 0)
-- Dependencies: 233
-- Name: service_worker_details_sw_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.service_worker_details_sw_id_seq OWNED BY public.service_worker_details.sw_id;


--
-- TOC entry 234 (class 1259 OID 16474)
-- Name: slds; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.slds (
    sld character varying(512),
    domain character varying(512) NOT NULL
);


ALTER TABLE public.slds OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 16479)
-- Name: sw_files; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.sw_files AS
 SELECT DISTINCT d.info,
    d.url_id,
    r.file_name,
    r.file_hash,
    d.target_url
   FROM (public.resource_info r
     JOIN public.desktop_detailed_logs d ON ((((d.info)::text ~~ '%Registered%'::text) AND (r.url_id = d.url_id) AND ((d.target_url)::text ~~ (('%'::text || (r.file_name)::text) || '%'::text)))));


ALTER VIEW public.sw_files OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 16484)
-- Name: sw_requests; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.sw_requests AS
 SELECT split_part(regexp_replace((target_url)::text, '^(https?://)?(www\.)?'::text, ''::text), '/'::text, 1) AS target_domain,
    split_part(regexp_replace((url)::text, '^(https?://)?(www\.)?'::text, ''::text), '/'::text, 1) AS sw_domain,
    target_url
   FROM public.detailed_logs
  WHERE ((info)::text ~~ '%Service Worker Request%'::text);


ALTER VIEW public.sw_requests OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 16488)
-- Name: urls; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.urls (
    url_id integer NOT NULL,
    url text,
    domain character varying(512),
    url_path text,
    class public.url_type,
    campaign character varying(512),
    count integer,
    site_id bigint
);


ALTER TABLE public.urls OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 16493)
-- Name: urls_url_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.urls_url_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.urls_url_id_seq OWNER TO postgres;

--
-- TOC entry 4951 (class 0 OID 0)
-- Dependencies: 238
-- Name: urls_url_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.urls_url_id_seq OWNED BY public.urls.url_id;


--
-- TOC entry 4758 (class 2604 OID 18358)
-- Name: desktop_detailed_logs log_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.desktop_detailed_logs ALTER COLUMN log_id SET DEFAULT nextval('public.desktop_detailed_logs_log_id_seq'::regclass);


--
-- TOC entry 4759 (class 2604 OID 18359)
-- Name: detailed_logs log_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detailed_logs ALTER COLUMN log_id SET DEFAULT nextval('public.detailed_logs_log_id_seq'::regclass);


--
-- TOC entry 4760 (class 2604 OID 18360)
-- Name: mobile_detailed_logs log_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mobile_detailed_logs ALTER COLUMN log_id SET DEFAULT nextval('public.mobile_detailed_logs_log_id_seq'::regclass);


--
-- TOC entry 4761 (class 2604 OID 18361)
-- Name: notification_details notification_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_details ALTER COLUMN notification_id SET DEFAULT nextval('public.notification_details_notification_id_seq'::regclass);


--
-- TOC entry 4762 (class 2604 OID 18362)
-- Name: resource_info resource_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_info ALTER COLUMN resource_id SET DEFAULT nextval('public.resource_info_resource_id_seq'::regclass);


--
-- TOC entry 4763 (class 2604 OID 18363)
-- Name: seed_urls seed_url_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seed_urls ALTER COLUMN seed_url_id SET DEFAULT nextval('public.seed_urls_seed_url_id_seq'::regclass);


--
-- TOC entry 4766 (class 2604 OID 18364)
-- Name: service_worker_details sw_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_worker_details ALTER COLUMN sw_id SET DEFAULT nextval('public.service_worker_details_sw_id_seq'::regclass);


--
-- TOC entry 4767 (class 2604 OID 18365)
-- Name: urls url_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.urls ALTER COLUMN url_id SET DEFAULT nextval('public.urls_url_id_seq'::regclass);


--
-- TOC entry 4769 (class 2606 OID 18320)
-- Name: campaigns campaigns_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.campaigns
    ADD CONSTRAINT campaigns_pkey PRIMARY KEY (campaign);


--
-- TOC entry 4771 (class 2606 OID 18322)
-- Name: desktop_detailed_logs desktop_detailed_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.desktop_detailed_logs
    ADD CONSTRAINT desktop_detailed_logs_pkey PRIMARY KEY (log_id);


--
-- TOC entry 4773 (class 2606 OID 18324)
-- Name: detailed_logs detailed_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detailed_logs
    ADD CONSTRAINT detailed_logs_pkey PRIMARY KEY (log_id);


--
-- TOC entry 4775 (class 2606 OID 18326)
-- Name: mobile_detailed_logs mobile_detailed_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mobile_detailed_logs
    ADD CONSTRAINT mobile_detailed_logs_pkey PRIMARY KEY (log_id);


--
-- TOC entry 4777 (class 2606 OID 18328)
-- Name: notification_details notification_details_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_details
    ADD CONSTRAINT notification_details_pkey PRIMARY KEY (notification_id);


--
-- TOC entry 4780 (class 2606 OID 18330)
-- Name: resource_info resource_info_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_info
    ADD CONSTRAINT resource_info_pkey PRIMARY KEY (resource_id);


--
-- TOC entry 4782 (class 2606 OID 18332)
-- Name: seed_urls seed_urls_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seed_urls
    ADD CONSTRAINT seed_urls_pkey PRIMARY KEY (seed_url_id);


--
-- TOC entry 4785 (class 2606 OID 18334)
-- Name: service_worker_details service_worker_details_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_worker_details
    ADD CONSTRAINT service_worker_details_pkey PRIMARY KEY (sw_id);


--
-- TOC entry 4787 (class 2606 OID 18336)
-- Name: slds slds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slds
    ADD CONSTRAINT slds_pkey PRIMARY KEY (domain);


--
-- TOC entry 4789 (class 2606 OID 18338)
-- Name: urls urls_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.urls
    ADD CONSTRAINT urls_pkey PRIMARY KEY (url_id);


--
-- TOC entry 4778 (class 1259 OID 18339)
-- Name: hash_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX hash_index ON public.resource_info USING btree (file_hash varchar_ops);


--
-- TOC entry 4783 (class 1259 OID 18353)
-- Name: url_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX url_hash ON public.seed_urls USING btree (seed_url);


--
-- TOC entry 4943 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2023-11-04 16:53:21

--
-- PostgreSQL database dump complete
--

