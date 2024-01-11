CREATE TABLE IF NOT EXISTS post (
        id integer PRIMARY KEY,
        owner_id integer NOT NULL,
        date_post timestamp  NOT NULL,
        post_text text  NOT NULL,
        title text,
        post_source varchar(20)  NOT NULL);

CREATE TABLE IF NOT EXISTS photo (
        id_photo integer NOT NULL PRIMARY KEY,
        owner_id integer NOT NULL REFERENCES post (id)
);

CREATE TABLE IF NOT EXISTS video (
        id_video varchar(50) NOT NULL PRIMARY KEY,
        url_player varchar(300),
        owner_id integer NOT NULL REFERENCES post (id)
        width integer,
        height integer,
);