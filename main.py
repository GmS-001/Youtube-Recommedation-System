import pickle
import streamlit as st
import pandas as pd
import gdown
import os
import numpy as np
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
YOUTUBEAPIKEY = os.getenv('YOUTUBEAPIKEY')

video_list_id = "18B23YuS_XFyJZNE-c1uwzqmZhpYLBFnY"
similarity_id = "1wFXPr0ZfbiZVsYJdMwGhcEsXDeGC9m9F"
if not os.path.exists("video_list_dict.pkl"):
    gdown.download(f"https://drive.google.com/uc?id={video_list_id}", "video_list_dict.pkl", quiet=False)

if not os.path.exists("similarity.npy"):
    gdown.download(f"https://drive.google.com/uc?id={similarity_id}", "similarity.npy", quiet=False)

    
def get_poster(video_id):
    youtube = build("youtube", "v3", developerKey=YOUTUBEAPIKEY)
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()

    if 'items' in response and response['items']:
        return response['items'][0]['snippet']['thumbnails']['default']['url']
    else:
        return "https://via.placeholder.com/150"  # Placeholder URL for missing thumbnails


def recommend(movie):
    matching_rows = df_india[df_india['title'].str.lower() == movie.lower()]
    if matching_rows.empty:
        st.error("No matches found for the selected video.")
        return [], []

    index = matching_rows.index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    titles, video_posters,ids = [], [], []
    for i in distances[1:6]:
        titles.append(df_india.iloc[i[0]].title)
        video_posters.append(get_poster(df_india.iloc[i[0]].video_id))
        ids.append(df_india.iloc[i[0]].video_id)
    return titles, video_posters,ids

st.header('YouTube Video Recommendation System')

# Load data
df_india = pickle.load(open('video_list_dict.pkl', 'rb'))
if isinstance(df_india, dict):
    df_india = pd.DataFrame.from_dict(df_india)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# Prepare video list
video_list = df_india['title'].tolist()

# Streamlit UI
selected_video = st.selectbox("Type or select a video from the dropdown", video_list)
if st.button('Show Recommendation'):
    titles, video_posters, video_ids = recommend(selected_video)
    
    for i in range(5):
        col1, col2 = st.columns([3, 1])  # Create two columns: 3 parts for title, 1 part for poster
        
        with col1:
            st.subheader(titles[i])  # Display title of the recommended video
        
        with col2:
            # Creating clickable poster images
            video_url = f'https://www.youtube.com/watch?v={video_ids[i]}'
            st.markdown(f"[![{titles[i]}]({video_posters[i]})]({video_url})")