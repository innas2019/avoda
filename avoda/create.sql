BEGIN TRANSACTION;
CREATE TABLE user (
    id       INTEGER   PRIMARY KEY
                       UNIQUE
                       NOT NULL,
    name     TEXT (30) UNIQUE
                       NOT NULL,
    password TEXT (40) NOT NULL,
    isactive INTEGER
);
CREATE TABLE post (
    id          INTEGER    PRIMARY KEY
                           NOT NULL
                           UNIQUE,
    name        TEXT (40)  NOT NULL,
    place       TEXT (40)  NOT NULL,
    phone       TEXT (40)  UNIQUE
                           NOT NULL,
    text        TEXT (255),
    len         TEXT (100),
    occupations TEXT (100),
    o_kind      TEXT (100),
    sex         INTEGER,
    created     DATETIME  NOT NULL,
    updated     DATETIME  NOT NULL
);

-- Table: role
CREATE TABLE IF NOT EXISTS role (
    id INTEGER PRIMARY KEY UNIQUE NOT NULL, 
    name TEXT (40) UNIQUE NOT NULL);

-- Table: user_role
CREATE TABLE IF NOT EXISTS user_role (
    user_id INTEGER REFERENCES user (id) ON DELETE NO ACTION ON UPDATE NO ACTION, 
    role_id INTEGER REFERENCES role (id) ON DELETE NO ACTION ON UPDATE NO ACTION);

INSERT INTO role (id, name) VALUES (1, 'administrators');
INSERT INTO role (id, name) VALUES (2, 'create_post');

COMMIT TRANSACTION;


