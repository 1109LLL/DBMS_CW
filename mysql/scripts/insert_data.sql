-- Insert data into tables;
-- 如果要试试的话记得改path

USE movie_site;

load data local infile './generated_csv/users.csv' 
into table users
FIELDS TERMINATED BY ","
lines terminated by '\n'
ignore 1 lines;

load data local infile './generated_csv/genres.csv' 
into table genres
FIELDS TERMINATED BY ","
lines terminated by '\n'
ignore 1 lines;

load data local infile './generated_csv/movies.csv' 
into table movies
FIELDS TERMINATED BY "," 
lines terminated by '\n'
ignore 1 lines;
 
load data local infile './generated_csv/tags.csv' 
into table tags
FIELDS TERMINATED BY "," 
lines terminated by '\n'
ignore 1 lines;

load data local infile './generated_csv/movies_genreses.csv' 
into table moviesGenres
FIELDS TERMINATED BY "," 
lines terminated by '\n'
ignore 1 lines;

-- type of ts?
load data local infile './generated_csv/ratings.csv' 
into table ratings
FIELDS TERMINATED BY "," 
lines terminated by '\n'
ignore 1 lines
(movieID, userID, ratingFigure, @ts) SET ts = FROM_UNIXTIME(@ts);

-- type of ts?
load data local infile './generated_csv/users_tags_movies.csv' 
into table userTagsMovie
FIELDS TERMINATED BY "," 
lines terminated by '\n'
ignore 1 lines
(userID, movieID, tagID, @ts) SET ts = FROM_UNIXTIME(@ts);