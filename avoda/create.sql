DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
CREATE TABLE user (
    id       INTEGER   PRIMARY KEY
                       UNIQUE
                       NOT NULL,
    name     TEXT (30) UNIQUE
                       NOT NULL,
    password TEXT (40) NOT NULL
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
