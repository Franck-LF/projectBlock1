DROP DATABASE IF EXISTS movies2;
CREATE DATABASE IF NOT EXISTS movies2;
USE movies2;

SELECT 'CREATING DATABASE STRUCTURE' as 'INFO';

DROP TABLE IF EXISTS directors,
                     actors,
                     composers,
		     users,
		     infos,
		     categories,
                     countries, 
                     similar_movies,
		     reviews,
   		     director_movie,
		     actor_movie,
		     composer_movie,
		     category_movie,
		     country_movie,
             	     movies;

/*!50503 set default_storage_engine = InnoDB */;
/*!50503 select CONCAT('storage engine: ', @@default_storage_engine) as INFO */;

CREATE TABLE directors (
    director_id		VARCHAR(255)		NOT NULL,
    director_name	VARCHAR(255)		NOT NULL,
    PRIMARY KEY (director_id),
    UNIQUE  KEY (director_name)
);

CREATE TABLE actors (
    actor_id	VARCHAR(255)		NOT NULL,
    actor_name	VARCHAR(255)		NOT NULL,
    PRIMARY KEY (actor_id),
    UNIQUE  KEY (actor_name)
);

CREATE TABLE composers (
    composer_id		VARCHAR(255)	NOT NULL,
    composer_name	VARCHAR(255)	NOT NULL,
    PRIMARY KEY (composer_id),
    UNIQUE  KEY (composer_id)
);

CREATE TABLE users (
    user_id		VARCHAR(255)	NOT NULL,
    user_name		VARCHAR(255)	NOT NULL,
    nb_reviews		VARCHAR(255)    DEFAULT 0,
    PRIMARY KEY (user_id),
    UNIQUE  KEY (user_id)
);

CREATE TABLE infos (
    info_id		VARCHAR(255)	NOT NULL,
    summary		TEXT(65535),
    url_thumbnail VARCHAR(255) NOT NULL,
    PRIMARY KEY (info_id),
    UNIQUE  KEY (info_id)
);

CREATE TABLE categories (
    category_id	VARCHAR(255)	NOT NULL,
    category	VARCHAR(255)	NOT NULL,
    PRIMARY KEY (category_id),
    UNIQUE  KEY (category_id)
);

CREATE TABLE countries (
    country_id	VARCHAR(255)	NOT NULL,
    country	VARCHAR(255)	NOT NULL,
    PRIMARY KEY (country_id),
    UNIQUE  KEY (country_id)
);

CREATE TABLE movies (
    movie_id		VARCHAR(255)	NOT NULL,
    title		VARCHAR(255)	NOT NULL,
    original_title	VARCHAR(255)	NOT NULL,
    duration		INT     DEFAULT 0,
    release_date	DATE	NOT NULL,
    nb_notes		INT	DEFAULT 0,
    nb_reviews		INT	DEFAULT 0,
    info_id		VARCHAR(255)	NOT NULL,
    star_rating		FLOAT	NOT NULL,
    PRIMARY KEY (movie_id),
    UNIQUE  KEY (movie_id),
    FOREIGN KEY (info_id) REFERENCES infos (info_id) ON DELETE CASCADE
);

CREATE TABLE director_movie (
    director_id		VARCHAR(255)	NOT NULL,
    movie_id        	VARCHAR(255)	NOT NULL,
    PRIMARY KEY (director_id, movie_id),
    FOREIGN KEY (director_id)	REFERENCES directors	(director_id)	ON DELETE CASCADE,
    FOREIGN KEY (movie_id)	REFERENCES movies	(movie_id)	ON DELETE CASCADE
);

CREATE TABLE actor_movie (
    actor_id	VARCHAR(255)	NOT NULL,
    movie_id    VARCHAR(255)	NOT NULL,
    PRIMARY KEY (actor_id, movie_id),
    FOREIGN KEY (actor_id)	REFERENCES actors	(actor_id)	ON DELETE CASCADE,
    FOREIGN KEY (movie_id)	REFERENCES movies	(movie_id)	ON DELETE CASCADE
);

CREATE TABLE composer_movie (
    composer_id		VARCHAR(255)		NOT NULL,
    movie_id        	VARCHAR(255)		NOT NULL,
    PRIMARY KEY (composer_id, movie_id),
    FOREIGN KEY (composer_id)	REFERENCES composers	(composer_id)	ON DELETE CASCADE,
    FOREIGN KEY (movie_id)	REFERENCES movies	(movie_id)	ON DELETE CASCADE
);

CREATE TABLE category_movie (
    category_id		VARCHAR(255)		NOT NULL,
    movie_id        	VARCHAR(255)		NOT NULL,
    PRIMARY KEY (category_id, movie_id),
    FOREIGN KEY (category_id)	REFERENCES categories	(category_id)	ON DELETE CASCADE,
    FOREIGN KEY (movie_id)	REFERENCES movies	(movie_id)	ON DELETE CASCADE
);

CREATE TABLE country_movie (
    country_id	VARCHAR(255)		NOT NULL,
    movie_id    VARCHAR(255)		NOT NULL,
    PRIMARY KEY (country_id, movie_id),
    FOREIGN KEY (country_id)	REFERENCES countries	(country_id)	ON DELETE CASCADE,
    FOREIGN KEY (movie_id)	REFERENCES movies	(movie_id)	ON DELETE CASCADE
);

CREATE TABLE reviews (
    review_id	VARCHAR(255)	NOT NULL,
    movie_id    VARCHAR(255)    NOT NULL,
    date        DATE,
    star_rating ENUM('0.5', '1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5') NOT NULL,
    review 	TEXT(65535) 	NOT NULL,
    user_id	VARCHAR(255)	NOT NULL,

    PRIMARY KEY (review_id),
    UNIQUE KEY (review_id),
    FOREIGN KEY (movie_id)	REFERENCES movies	(movie_id)	ON DELETE CASCADE
);





SELECT 'EVERYTHING IS OK' as 'INFO';
