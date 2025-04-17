import pandas as pd 
from functools import cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

@cache
def read_file():    
    movies = pd.read_csv("movies.csv")
    tags = pd.read_csv("tags.csv")

    return movies, tags

@cache
def extract_features(): 
    movies, tags  = read_file()
    
    filtered_movies = movies.copy()
    filtered_tags = tags.copy()
    filtered_movies[["movie_title", "year"]] = filtered_movies["title"].str.rsplit(n=1, expand=True)
    filtered_movies["genres"], filtered_movies["movie_title"] = filtered_movies["genres"].str.replace('|', ','), filtered_movies["movie_title"].str.replace(',', ' ') 

    filtered_tags.dropna(inplace=True)
    filtered_tags.drop(["userId","timestamp"],axis=1,inplace=True)

    years = filtered_movies[["year", "movieId"]]

    movies_with_tags = filtered_movies.merge(filtered_tags, on="movieId").reset_index(drop=True)    
    movies_with_tags.drop(["year"], axis=1,inplace=True)
    movies_df = movies_with_tags.groupby(["movieId"]).agg(lambda x: ','.join(x.unique()))
    movies_df["genre_and_tag"] = movies_df["genres"] + ',' + movies_df["tag"]
    movies_df.drop(["genres", "tag", "title"],axis=1,inplace=True)
    movies_df = movies_df.merge(years,on="movieId").reset_index(drop=True)

    return movies_df

@cache
def vectorizer():
    movies_df = extract_features()
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies_df["genre_and_tag"])

    return tfidf_matrix

@cache
def cos_similarity():
    similarity_score = cosine_similarity(vectorizer())
    
    return similarity_score

@cache
def similarity_df():
    movies_df = extract_features()
    sim_score = cos_similarity()
    sim_df = pd.DataFrame(sim_score, index=movies_df["movie_title"], columns=movies_df["movie_title"])

    return sim_df

@cache
def get_recommendations(movie_name):
    sim_df = similarity_df()
    sim_score = cos_similarity()
    movies_df = extract_features()

    index = [i for i, title in enumerate(sim_df) if title == movie_name][0]
    similar_movies = sorted(list(enumerate(sim_score[index])), key=lambda x: x[1], reverse=True)[1:6]
    data = []

    for index, similarity in similar_movies:
        item = []
        temp_df = movies_df[movies_df["movie_title"] == sim_df.index[index]]
        item.extend(temp_df["movie_title"].values)
        item.extend(temp_df["year"].values)
        data.append(item)

    return data