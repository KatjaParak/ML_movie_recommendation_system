import pandas as pd 
from functools import lru_cache
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download("vader_lexicon")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

@lru_cache
def read_file():    
    movies = pd.read_csv("movies.csv")
    tags = pd.read_csv("tags.csv")

    return movies, tags

@lru_cache
def extract_features(): 
    movies, tags  = read_file()
    
    filtered_movies = movies.copy()
    filtered_tags = tags.copy()
    filtered_movies[["movie_title", "year"]] = filtered_movies["title"].str.rsplit(n=1, expand=True)
    filtered_movies["genres"], filtered_movies["movie_title"] = filtered_movies["genres"].str.replace('|', ','), filtered_movies["movie_title"].str.replace(',', '') 

    filtered_tags.dropna(inplace=True)
    filtered_tags.drop(["userId","timestamp"],axis=1,inplace=True)

    sia = SentimentIntensityAnalyzer()
    compound_score = []
    for tag in filtered_tags["tag"]:
        scores = sia.polarity_scores(tag)
        compound = scores["compound"]
        compound_score.append(compound)

    tags_with_scores = filtered_tags.copy()
    tags_with_scores["scores"] = compound_score

    years = filtered_movies[["year", "movieId"]]

    movies_with_tags = filtered_movies.merge(tags_with_scores, on="movieId").reset_index(drop=True)
    movies_with_tags = movies_with_tags[movies_with_tags["scores"] >= 0.05]    
    movies_with_tags.drop(["year", "scores"], axis=1,inplace=True)
    movies_df = movies_with_tags.groupby(["movieId"]).agg(lambda x: ','.join(x.unique()))
    movies_df["genre_and_tag"] = movies_df["genres"] + ',' + movies_df["tag"]
    movies_df.drop(["genres", "tag", "title"],axis=1,inplace=True)
    movies_df = movies_df.merge(years,on="movieId").reset_index(drop=True)

    return movies_df


def normalize_titles(movies_df):
    new_titles = []
    for title in movies_df["movie_title"]:
        new_title = re.sub(r'^(.*) (The|A|An)$', r'\2 \1', title)
        new_titles.append(new_title)
    
    movies_df["title"] = new_titles
    movies_df.drop("movie_title", axis=1, inplace=True)

    return movies_df


def vectorizer(movies_df):
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies_df["genre_and_tag"])

    return tfidf_matrix


def cos_similarity(tfidf_matrix):
    similarity_score = cosine_similarity(tfidf_matrix)
    
    return similarity_score


def similarity_df(similarity_score, movies_df):
    sim_df = pd.DataFrame(similarity_score, index=movies_df["title"], columns=movies_df["title"])

    return sim_df


def get_recommendations(movie_name,sim_df,similarity_score, movies_df):

    if movie_name not in sim_df.index:
        return f"{movie_name} was not found"

    index = [i for i, title in enumerate(sim_df.index) if title == movie_name][0]
    similar_movies = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:6]
    data = []

    for index, similarity in similar_movies:
        item = []
        temp_df = movies_df[movies_df["title"] == sim_df.index[index]]
        item.extend(temp_df["title"].values)
        item.extend(temp_df["year"].values)
        data.append(item)

    return data