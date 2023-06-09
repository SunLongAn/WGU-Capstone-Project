# AUTOGENERATED! DO NOT EDIT! File to edit: movie-rec.ipynb.

# %% auto 0
__all__ = []

# %% movie-rec.ipynb 0
# imports to be used in .py file
import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# %% movie-rec.ipynb 3
# create title for web app
st.title(":blue[Fanz O' Filmz] Movie Recommender")

# %% movie-rec.ipynb 5
# import data to dataframe
df = pd.read_csv('movie_data.csv')

# %% movie-rec.ipynb 7
# create copy of dataframe for editing to prevent errors, selecting features used for recommendations
movies = df[['Movie_Title', 'Year', 'Director', 'Actors', 'main_genre', 'side_genre']].copy()

# %% movie-rec.ipynb 10
# function to combine genre columns
def combine_genres(data):
    comb_genres = []
    for i in range(0, data.shape[0]):
        comb_genres.append(data['main_genre'][i] + ' ' + data['side_genre'][i])
        
    return comb_genres

# %% movie-rec.ipynb 11
# prepare column for combination
movies['side_genre'] = movies['side_genre'].str.replace(",","")

# %% movie-rec.ipynb 12
# combine genre columns
movies['genres'] = combine_genres(movies)

# %% movie-rec.ipynb 13
# drop original genre columns - no longer needed
movies = movies.drop(columns = ['main_genre', 'side_genre'])

# %% movie-rec.ipynb 15
# combine Movie_Title and Year columns to make unique titles in the case of different movies having the same name
def get_clean_title(data):
    clean_title = []
    for i in range(0, data.shape[0]):
        clean_title.append(data['Movie_Title'][i] + ' (' + str(data['Year'][i]) + ')')
        
    return clean_title

# %% movie-rec.ipynb 16
# create clean_title column
movies['clean_title'] = get_clean_title(movies)

# %% movie-rec.ipynb 18
# remove duplicate rows from dataframe
movies = movies.drop_duplicates(subset = ['clean_title']).copy()

# %% movie-rec.ipynb 20
# reset indices in dataframe to clear empty duplicate indices
movies.reset_index(inplace = True, drop = True)

# %% movie-rec.ipynb 22
# prepare columns then split into lists
movies['Director'] = movies["Director"].str.replace("Directors:", "")
movies['Director'] = movies['Director'].map(lambda x: x.replace(" ", "").lower().split(',')[:3])

movies['Actors'] = movies['Actors'].map(lambda x: x.replace(" ", "").lower().split(',')[:4])

movies['genres'] = movies['genres'].map(lambda x: x.lower().split())

# %% movie-rec.ipynb 27
# initialize variable and create function to round year down to find decade of movie release
y = 2003

def round_down(year):
    return year - (year % 10)

# %% movie-rec.ipynb 29
# create decade column based on movie release year
movies['decade'] = movies['Year'].apply(round_down)

# %% movie-rec.ipynb 31
# join on columns to turn them into strings
movies['Director'] = movies['Director'].str.join(" ")

movies['Actors'] = movies['Actors'].str.join(" ")

movies['genres'] = movies['genres'].str.join(" ")

# %% movie-rec.ipynb 33
# combine feature columns into a single column to use as corpus for TF-IDF vectorization
def combine_features(data):
    combined_features = []
    for i in range(0, data.shape[0]):
        combined_features.append(str(data['decade'][i]) + ' ' +
                                 data['genres'][i] + ' ' +
                                 data['Actors'][i] + ' ' +
                                 data['Director'][i])
        
    return combined_features

# %% movie-rec.ipynb 34
# create the combined_feature column
movies['combined_features'] = combine_features(movies)

# %% movie-rec.ipynb 37
# vectorize the combined_features column and transform into a matrix
vec = TfidfVectorizer()
vec_matrix = vec.fit_transform(movies['combined_features'])

# %% movie-rec.ipynb 39
# get cosine similarity maxtrix from the TF-IDF vectorized matrix
cs = cosine_similarity(vec_matrix)

# %% movie-rec.ipynb 41
# finds index of user-chosen movie, then provides a sorted list based on the
# cosine similarity distance between other movies and recommends the top 5 matches
def recommend_movies(movie):
    movie_index = movies[movies['clean_title'] == movie].index[0]
    cs_distances = cs[movie_index]
    movie_list = sorted(list(enumerate(cs_distances)), reverse = True, key = lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movie_list:
        recommended_movies.append(movies.iloc[i[0]].clean_title)

    return recommended_movies

# %% movie-rec.ipynb 43
# provides a Streamlit selection box for the user to select a movie
selected_movie_name = st.selectbox('Please select a movie you enjoy:', movies['clean_title'].values)

# %% movie-rec.ipynb 44
# creates a Streamlit recommendation button that when clicked will provide 
# the user with movie recommendations based on the chosen movie
if st.button('Get Recommendations'):
    recommendations = recommend_movies(selected_movie_name)
    st.write(":blue[Based on your selection, we recommend the following movies:]")
    for j in recommendations:
        st.write(j)
