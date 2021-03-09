USE movie_site;

START TRANSACTION;

CREATE TABLE IF NOT EXISTS userPersonality(
    userID VARCHAR(32) NOT NULL PRIMARY KEY, 
    openness FLOAT, 
    agreeableness FLOAT, 
    emotionalStability FLOAT, 
    conscientiousness FLOAT, 
    extraversion FLOAT,
    assignedMetric VARCHAR(20),
    assignedCondition VARCHAR(10),
    isPersonalised INT,
    enjoyWatching INT
);

CREATE TABLE IF NOT EXISTS userMovieRatings(
    userID VARCHAR(32) NOT NULL, 
    movieID INT NOT NULL,
    predictedRating FLOAT,
    FOREIGN KEY (userID) REFERENCES userPersonality(userID),
    FOREIGN KEY (movieID) REFERENCES movies(movieID)
);

COMMIT;

SHOW TABLES;