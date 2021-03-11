import math

personalities = ["openness", "agreeableness", "emotionalStability", "conscientiousness", "extraversion"]

def get_page_num(movie_num):
    return math.ceil(movie_num/20)

def genres_csv_to_list(genres_csv):
    gernes = genres_csv.split(',')
    return [genre for genre in gernes]

def fix_movies_info_genres(movies_info, genres_index=4):
    return [[(info if index != genres_index else genres_csv_to_list(info)) for index, info in enumerate(movie_info)] for movie_info in movies_info]