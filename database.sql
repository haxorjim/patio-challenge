CREATE TABLE team
(
    id serial primary key,
    name text NOT NULL
);

CREATE TABLE team_member
(
    id serial primary key,
    team_id integer references team (id),
    mobile_number text NOT NULL
);

CREATE TABLE post
(
    id serial primary key,
    sender text NULL,
    body text NULL,
    media_url text NULL,
    posted_on timestamptz NULL
);

ALTER TABLE post ADD CONSTRAINT post_sender_fkey FOREIGN KEY (sender) REFERENCES team_member (mobile_number);
