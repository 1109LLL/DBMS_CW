USE movie_site;

LOAD DATA LOCAL INFILE './generated_csv/user_personality.csv' 
INTO TABLE userPersonality
FIELDS TERMINATED BY ","
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

LOAD DATA LOCAL INFILE './generated_csv/user_movie_rating.csv' 
INTO TABLE userMovieRatings
FIELDS TERMINATED BY ","
LINES TERMINATED BY '\n'
IGNORE 1 LINES;