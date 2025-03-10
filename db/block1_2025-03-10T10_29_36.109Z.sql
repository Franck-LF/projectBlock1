CREATE TABLE `movies` (
	`movie_id` INTEGER NOT NULL UNIQUE,
	`title` VARCHAR(255) NOT NULL,
	`release_date` DATE,
	`duration` INTEGER DEFAULT 0 COMMENT 'expressed in minutes',
	`nb_notes` INTEGER NOT NULL DEFAULT 0,
	`nb_reviews` INTEGER NOT NULL DEFAULT 0,
	`info_id` INTEGER NOT NULL,
	`star_rating` FLOAT NOT NULL DEFAULT 0,
	PRIMARY KEY(`movie_id`)
);


CREATE TABLE `categories` (
	`category_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`category` VARCHAR(255) NOT NULL,
	PRIMARY KEY(`category_id`)
);


CREATE TABLE `category_movie` (
	`category_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`movie_id` INTEGER NOT NULL,
	PRIMARY KEY(`category_id`, `movie_id`)
);


CREATE TABLE `countries` (
	`country_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`country` VARCHAR(255) NOT NULL,
	PRIMARY KEY(`country_id`)
);


CREATE TABLE `country_movie` (
	`country_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`movie_id` INTEGER,
	PRIMARY KEY(`country_id`, `movie_id`)
);


CREATE TABLE `actors` (
	`actor_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`actor_name` VARCHAR(255) NOT NULL,
	PRIMARY KEY(`actor_id`)
);


CREATE TABLE `actor_movie` (
	`actor_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`movie_id` INTEGER NOT NULL,
	PRIMARY KEY(`actor_id`, `movie_id`)
);


CREATE TABLE `directors` (
	`director_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`director_name` VARCHAR(255) NOT NULL,
	PRIMARY KEY(`director_id`)
);


CREATE TABLE `director_movie` (
	`director_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`movie_id` INTEGER NOT NULL,
	PRIMARY KEY(`director_id`, `movie_id`)
);


CREATE TABLE `composers` (
	`composer_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`composer_name` VARCHAR(255) NOT NULL,
	PRIMARY KEY(`composer_id`)
);


CREATE TABLE `composer_movie` (
	`composer_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`movie_id` INTEGER NOT NULL,
	PRIMARY KEY(`composer_id`, `movie_id`)
);


ALTER TABLE `actor_movie`
ADD FOREIGN KEY(`movie_id`) REFERENCES `movies`(`movie_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `director_movie`
ADD FOREIGN KEY(`movie_id`) REFERENCES `movies`(`movie_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `composer_movie`
ADD FOREIGN KEY(`movie_id`) REFERENCES `movies`(`movie_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `category_movie`
ADD FOREIGN KEY(`movie_id`) REFERENCES `movies`(`movie_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `country_movie`
ADD FOREIGN KEY(`movie_id`) REFERENCES `movies`(`movie_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `directors`
ADD FOREIGN KEY(`director_id`) REFERENCES `director_movie`(`director_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `actors`
ADD FOREIGN KEY(`actor_id`) REFERENCES `actor_movie`(`actor_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `composers`
ADD FOREIGN KEY(`composer_id`) REFERENCES `composer_movie`(`composer_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `categories`
ADD FOREIGN KEY(`category_id`) REFERENCES `category_movie`(`category_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `countries`
ADD FOREIGN KEY(`country_id`) REFERENCES `country_movie`(`country_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;