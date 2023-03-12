#LIBRERIE
#region
import spotipy
import spotipy.util as util
import pandas as pd
import streamlit as st
import numpy as np
from spotipy.oauth2 import SpotifyOAuth

import songrecommendations
import polarplot

import os
import datetime as dt
import json
import smtplib
from config import *
from stats_gen import *
from streamlit_option_menu import option_menu
import utils as utl
import os
import sys
import signal
import threading
import webbrowser

from PIL import Image
import requests
from io import BytesIO

import streamlit as st
from streamlit_metrics import metric, metric_row

import matplotlib.pyplot as plt
from datetime import datetime

import funzioni

import altair as alt
#endregion



st.set_page_config(page_title="Spotify Ultra Wrapped",page_icon=":shark:", layout="centered",
                   menu_items=None ,initial_sidebar_state="auto")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("test.css")
#TOKEN SPOTIFY 

client_id = '5e7881c6e05440c0895cfa3c2a52fe37'
client_secret = '50d6a378818745ff846018655d9aef4c'
#endregion

######################################################################################################

#CARATTERISTICHE CANZONI 
#region
def get_track_ids(time_frame):
    track_ids = []
    for song in time_frame['items']:
        track_ids.append(song['id'])
    return track_ids

def get_track_features(id):
    meta = sp.track(id)
    # meta
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    spotify_url = meta['external_urls']['spotify']
    album_cover = meta['album']['images'][1]['url']
    track_info = [name, album, artist, spotify_url, album_cover]
    return track_info
#endregion

######################################################################################################

#LAYOUT 
#region
#Home Page
st.title("My Spotify Wrapped")
st.subheader("I tuoi dati tutto l'anno :musical_note:")

######################################################################################################
#SideBar

with st.sidebar:
    selected = option_menu('',["Home", 'My Tracks', 'My Artists','My Playlists', 'My Podcasts', 'Analysis','Song/Track','Artist','Album','Community'], 
        icons=['house', 'bi bi-file-person-fill','bi bi-file-person-fill','bi bi-music-player-fill','bi bi-music-note-list','bi bi-bar-chart-fill','bi bi-vinyl-fill','bi bi-mic-fill','bi bi-disc-fill','bi bi-people-fill'], 
        menu_icon="house", default_index=0)
#endregion

######################################################################################################

#HOME 
#region
if selected == 'Home':
    col1, col2 = st.columns(2)
    with col1:
        if not st.button("Log in to Spotify"):
    # Non fare nulla se il bottone non viene cliccato
            pass
        else:
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    with col2:
        if st.button("Log out to Spotify"):
        # Non fare nulla se il bottone non viene cliccato
            os.remove('.cache-your-spotify-username')
        # aggiungi eventuali altre operazioni di log
        else:
            pass
#endregion



######################################################################################################
#region
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Everything is accessible via the st.secrets dict:

st.write("DB username:", st.secrets["SPOTIPY_CLIENT_ID"])
st.write("DB password:", st.secrets["SPOTIPY_CLIENT_SECRET"])
st.write("DB URI:", st.secrets["SPOTIPY_REDIRECT_URI"])

# And the root-level secrets are also accessible as environment variables:

import os

st.write(
    "Has environment variables been set:",
    os.environ["SPOTIPY_CLIENT_ID"] == st.secrets["SPOTIPY_CLIENT_ID"],
)

client_id = os.environ['SPOTIPY_CLIENT_ID']
client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
scope = ['user-library-read','user-top-read','user-read-recently-played','user-library-read']

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])

######################################################################################################

#MY TRACKS 
#region
#My Tracks Page
if selected == 'My Tracks':
    time_range_labels = {
            '1 mese': 'short_term',
            '6 mesi': 'medium_term',
            'sempre': 'long_term'
        }
        # ordina i brani in base alla selezione dell'utente
    time_range = time_range_labels['1 mese']
    col1,col2 = st.columns(2)
    color = col1.select_slider('Seleziona il periodo', options=['1 mese', '6 mesi', 'sempre'])
    if color == '1 mese':
        time_range = time_range_labels['1 mese']
    elif color == '6 mesi':
        time_range = time_range_labels['6 mesi']
    else:
        time_range = time_range_labels['sempre']
    
    order_by = col2.selectbox("Ordina per", ["Titolo 🎧", "Artista 🎤", "Album 💿","Durata ⏰","Data Rilascio 📆","Popolarità 🚀","Energia 🏋🏻‍♂️", "Tristezza 😢"])

    # loop over track ids
    if time_range == 'short_term':
            top_tracks = sp.current_user_top_tracks(limit=32, offset=0, time_range=time_range)
            # ordina i brani in base alla selezione dell'utente
            if order_by == "Titolo 🎧":
                top_tracks['items'].sort(key=lambda x: x['name'])
            elif order_by == "Artista 🎤":
                top_tracks['items'].sort(key=lambda x: x['artists'][0]['name'])
            elif order_by == "Album 💿":
                top_tracks['items'].sort(key=lambda x: x['album']['name'])
            elif order_by == "Durata ⏰":
                top_tracks['items'].sort(key=lambda x: x['duration_ms'])
            elif order_by == "Data Rilascio 📆":
                top_tracks['items'].sort(key=lambda x: x['album']['release_date'], reverse=True)
            elif order_by == "Popolarità 🚀":
                top_tracks['items'].sort(key=lambda x: x['popularity'], reverse=True)
            elif order_by == "Energia🏋🏻‍♂️":
                feat = {}
                for i in range(32):
                    track_id = top_tracks['items'][i]['id']
                    track_features = sp.audio_features(track_id)
                    feat[track_id] = track_features[0]['valence']
                sorted_tracks = sorted(feat.items(), key=lambda x: x[1], reverse=True)
                top_tracks['items'] = [sp.track(track[0]) for track in sorted_tracks]
            else:
                feat = {}
                for i in range(32):
                    track_id = top_tracks['items'][i]['id']
                    track_features = sp.audio_features(track_id)
                    feat[track_id] = track_features[0]['valence']
                sorted_tracks = sorted(feat.items(), key=lambda x: x[1], reverse=False)
                top_tracks['items'] = [sp.track(track[0]) for track in sorted_tracks]
            num_columns = 8
            items_per_column = len(top_tracks['items']) // num_columns
            q = 0
            # Loop through the artist results and display them in columns
            for i in range(num_columns):
                col_items = top_tracks['items'][i*items_per_column:(i+1)*items_per_column]
                col = st.columns(items_per_column)
                for j, item in enumerate(col_items):
                    with col[j]:
                        image = st.image(item['album']['images'][0]['url'], use_column_width=True)
                        name = item['artists'][0]['name']
                        hide = """
                        <style>
                        ul.streamlit-expander {
                            border: 2 !important;
                        </style>
                        """

                        st.markdown(hide, unsafe_allow_html=True)
                        with st.expander("🎵"):
                            titolo = item['name']
                            artista = item['artists'][0]['name']
                            track_album = item['album']['name']
                            pop = item['popularity']
                            st.audio(item['preview_url'], format="audio/mp3")
                            st.markdown(f"""
                                ###### 🎧 {titolo}
                                ###### 🎤 {artista}
                                ###### 💿 {track_album}
                                ###### 🚀 Popolarità: {pop}
                        """)
                        q = q+1
            total_a = 0
            for i in range(32):
                track_id = top_tracks['items'][i]['id']
                track_features = sp.audio_features(track_id)
                a = track_features[0]['valence']
                total_a += a
            valori = [total_a, 32-total_a]
            etichette = ['felice', 'triste']
            fig1, ax1 = plt.subplots()
            ax1.pie(valori, labels=etichette, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            st.pyplot(fig1)
######################################################################################################
    elif time_range == 'medium_term':
        top_tracks = sp.current_user_top_tracks(limit=32, offset=0, time_range=time_range)
        # ordina i brani in base alla selezione dell'utente
        if order_by == "Titolo 🎧":
            top_tracks['items'].sort(key=lambda x: x['name'])
        elif order_by == "Artista 🎤":
            top_tracks['items'].sort(key=lambda x: x['artists'][0]['name'])
        elif order_by == "Album 💿":
            top_tracks['items'].sort(key=lambda x: x['album']['name'])
        elif order_by == "Durata ⏰":
            top_tracks['items'].sort(key=lambda x: x['duration_ms'])
        elif order_by == "Data Rilascio 📆":
            top_tracks['items'].sort(key=lambda x: x['album']['release_date'], reverse=True)
        elif order_by == "Popolarità 🚀":
            top_tracks['items'].sort(key=lambda x: x['popularity'], reverse=True)
        elif order_by == "Energia🏋🏻‍♂️":
            feat = {}
            for i in range(32):
                track_id = top_tracks['items'][i]['id']
                track_features = sp.audio_features(track_id)
                st.write(track_features)
                feat[track_id] = track_features[0]['valence']
            sorted_tracks = sorted(feat.items(), key=lambda x: x[0], reverse=True)
            top_tracks['items'] = [sp.track(track[0]) for track in sorted_tracks]
        else:
            feat = {}
            for i in range(32):
                track_id = top_tracks['items'][i]['id']
                track_features = sp.audio_features(track_id)
                feat[track_id] = track_features[0]['valence']
            sorted_tracks = sorted(feat.items(), key=lambda x: x[1], reverse=False)
            top_tracks['items'] = [sp.track(track[0]) for track in sorted_tracks]

        num_columns = 8
        items_per_column = len(top_tracks['items']) // num_columns
        q = 0
        # Loop through the artist results and display them in columns
        for i in range(num_columns):
            col_items = top_tracks['items'][i*items_per_column:(i+1)*items_per_column]
            col = st.columns(items_per_column)
            for j, item in enumerate(col_items):
                with col[j]:
                    image = st.image(item['album']['images'][0]['url'], use_column_width=True)
                    name = item['artists'][0]['name']
                    with st.expander("🎵"):
                            id_track = item['id']
                            track_features = sp.audio_features(id_track)
                            valence = track_features[0]['valence']
                            titolo = item['name']
                            artista = item['artists'][0]['name']
                            track_album = item['album']['name']
                            pop = item['popularity']
                            st.audio(item['preview_url'], format="audio/mp3")
                            st.markdown(f"""
                                ###### 🎧 {titolo}
                                ###### 🎤 {artista}
                                ###### 💿 {track_album}
                                ###### 🚀 Popolarità: {pop}
                                ###### 🥳 {valence}

                        """)
                    q = q+1
        total_a = 0
        for i in range(32):
            track_id = top_tracks['items'][i]['id']
            track_features = sp.audio_features(track_id)
            a = track_features[0]['valence']
            total_a += a
        valori = [total_a, 32-total_a]
        etichette = ['felice', 'triste']
        fig1, ax1 = plt.subplots()
        ax1.pie(valori, labels=etichette, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        st.pyplot(fig1)

######################################################################################################
    if time_range == 'long_term':
        top_tracks = sp.current_user_top_tracks(limit=32, offset=0, time_range=time_range)
        # ordina i brani in base alla selezione dell'utente
        if order_by == "Titolo 🎧":
            top_tracks['items'].sort(key=lambda x: x['name'])
        elif order_by == "Artista 🎤":
            top_tracks['items'].sort(key=lambda x: x['artists'][0]['name'])
        elif order_by == "Album 💿":
            top_tracks['items'].sort(key=lambda x: x['album']['name'])
        elif order_by == "Durata ⏰":
            top_tracks['items'].sort(key=lambda x: x['duration_ms'])
        elif order_by == "Data Rilascio 📆":
            top_tracks['items'].sort(key=lambda x: x['album']['release_date'], reverse=True)
        elif order_by == "Popolarità 🚀":
            top_tracks['items'].sort(key=lambda x: x['popularity'], reverse=True)
        elif order_by == "Energia🏋🏻‍♂️":
            feat = {}
            for i in range(32):
                track_id = top_tracks['items'][i]['id']
                track_features = sp.audio_features(track_id)
                feat[track_id] = track_features[0]['valence']
            sorted_tracks = sorted(feat.items(), key=lambda x: x[1], reverse=True)
            top_tracks['items'] = [sp.track(track[0]) for track in sorted_tracks]
        else:
            feat = {}
            for i in range(32):
                track_id = top_tracks['items'][i]['id']
                track_features = sp.audio_features(track_id)
                feat[track_id] = track_features[0]['valence']
            sorted_tracks = sorted(feat.items(), key=lambda x: x[1], reverse=False)
            top_tracks['items'] = [sp.track(track[0]) for track in sorted_tracks]

        num_columns = 8
        items_per_column = len(top_tracks['items']) // num_columns
        q = 0

        for i in range(num_columns):
            col_items = top_tracks['items'][i*items_per_column:(i+1)*items_per_column]
            col = st.columns(items_per_column)
            for j, item in enumerate(col_items):
                with col[j]:
                    image = st.image(item['album']['images'][0]['url'], use_column_width=True)
                    name = item['artists'][0]['name']
                    track_id = item['id']
                    track_features = sp.audio_features(track_id)
                    with st.expander("🎵"):
                            titolo = item['name']
                            artista = item['artists'][0]['name']
                            track_album = item['album']['name']
                            pop = item['popularity']
                            happy = track_features[0]['valence']
                            st.audio(item['preview_url'], format="audio/mp3")
                            st.markdown(f"""
                                ###### 🎧 {titolo}
                                ###### 🎤 {artista}
                                ###### 💿 {track_album}
                                ###### 🚀 Popolarità: {pop}
                        """)
                    q = q+1
        total_a = 0
        for i in range(32):
            track_id = top_tracks['items'][i]['id']
            track_features = sp.audio_features(track_id)
            a = track_features[0]['valence']
            total_a += a
        valori = [total_a, 32-total_a]
        etichette = ['felice', 'triste']
        fig1, ax1 = plt.subplots()
        ax1.pie(valori, labels=etichette, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        st.pyplot(fig1)
#endregion

######################################################################################################

#ANALYSIS 
#region
if selected == 'Analysis':
    user_id = sp.current_user()["id"]
    recently_played = sp.current_user_recently_played(limit=50)['items']
    song_names = []
    artists = []
    artists_id = [] 
    albums = []
    times = []
    durations_ms = []
    track_ids = []
    genere = []
    album_image = []
    for track in recently_played:
        song = track['track']['name']
        artist = track['track']['artists'][0]['name']
        artist_id = track['track']['artists'][0]['id']
        album = track['track']['album']['name']
        album_im = track['track']['album']['images'][1]['url']
        played_at = track['played_at']
        duration = track['track']['duration_ms']
        id = track['track']['id']
        song_names.append(song)
        artists.append(artist)
        artists_id.append(artist_id)
        albums.append(album)
        played_at_dt = funzioni.str_to_datetime(played_at)
        times.append(played_at_dt)
        durations_ms.append(duration)
        track_ids.append(id)
        album_image.append(album_im)
    # Reverse The Lists So The Data Is Aligned From Oldest Played Songs To Newest Played Songs
    song_names.reverse()
    artists.reverse()
    artists_id.reverse()
    albums.reverse()
    times.reverse()
    durations_ms.reverse()
    track_ids.reverse()
    album_image.reverse()


    #result = sp.search("Capri sun")
    #track = result['tracks']['items'][0]

    #artist = sp.artist(track["artists"][0]["external_urls"]["spotify"])
    #st.write("artist genres:", artist["genres"])

    #album = sp.album(track["album"]["external_urls"]["spotify"])
    #st.write("album genres:", album["genres"])
    #st.write("album release-date:", album["release_date"])

    songs_data_dict = {
            'song_names': song_names,
            'artists': artists,
            'artists_id':artists_id,
            'albums': albums,
            'time_played': times,
            'duration_ms': durations_ms,
            'track_ids': track_ids,
            'albums_image': album_image,
            'id_name':sp.current_user()["id"]

        }


    # Create an empty list to store the genres
    genres = []

    # Loop through the list of artists in the songs_data_dict
    for artist in songs_data_dict['artists']:
        # Search for the artist on Spotify
        result = sp.search(artist, type='artist')
        
        # Get the first artist in the search results
        first_artist = result['artists']['items'][0]
        
        # Get the genres of the first artist
        artist_genres = first_artist['genres']
        
        # Add the genres to the list of genres
        genres.append(artist_genres)

    test1 = pd.DataFrame(songs_data_dict)
    test1 = test1.assign(genres=genres)
    with open(r"/Users/fabiotraina/Desktop/Project Work😱/SpotifyWrapped/my_data.csv", mode = 'a') as f:
        test1.to_csv(f, header=f.tell()==0, index=False)
    st.write(test1)

    weekly_tracks = create_track_list(songs_data_dict)
    num_songs_played = len(weekly_tracks)
    calc_most_freq_song_result = calc_most_freq_played_song(weekly_tracks)
    most_freq_played_song = calc_most_freq_song_result[0]
    max_freq = calc_most_freq_song_result[1]
    most_freq_played_album = calc_most_freq_played_album(weekly_tracks)
    most_freq_played_artist = calc_most_freq_played_artist(weekly_tracks)
    total_time_played = 0
    for duration in songs_data_dict['duration_ms']:
        total_time_played += duration
    total_time_played_mins = round(total_time_played / 60000)
    #st.write(weekly_tracks)
    st.write("Numero di canzoni ascoltate: ", num_songs_played)
    st.write("Album più ascoltato: ", most_freq_played_album[0],"-",most_freq_played_album[1])
    st.write("Canzone più ascoltata: ", most_freq_played_song[0],"-",most_freq_played_song[2], "/", max_freq,"times")
    st.write("Artista più ascoltato: ", most_freq_played_artist[1])
    st.write("Minuti di ascolto totali: ", total_time_played_mins,"mins")
    
    #grafico artista più ascoltato
    test1['count'] = test1.groupby('artists')['artists'].transform('count')
    st.line_chart(test1, x="artists", y="count")
    
    #grafico canzone più ascoltata
    test1['count'] = test1.groupby('song_names')['song_names'].transform('count')
    st.line_chart(test1, x="song_names", y="count")
    
    #grafico album più ascoltato
    test1['count'] = test1.groupby('albums')['albums'].transform('count')
    st.line_chart(test1, x="albums", y="count")
    
    test1['count'] = test1.groupby('song_names')['time_played'].transform('count')
    st.line_chart(test1, x="song_names", y="time_played")
    
    test1['count'] = test1.groupby('artists')['time_played'].transform('count')
    st.line_chart(test1, x="artists", y="time_played")
    
    test1['count'] = test1.groupby('albums')['time_played'].transform('count')
    st.line_chart(test1, x="albums", y="time_played")
    
#endregion

######################################################################################################

#GENIUS API 
#region
import lyricsgenius as lg

genius = lg.Genius('JVn88pTEEYxo2YohYF04aACXZWlZ-roBywYSx2UwUiCxCctBcq6nRuyo3GwS6FTP',  # Client access token from Genius Client API page
                             skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"],
                             remove_section_headers=True)
#endregion

######################################################################################################

#SONG/TRACKS 
#region
search_results = []
canzone = []
tracks = []
artists = []
albums = []


if selected == 'Song/Track':
    search_keyword = st.text_input(selected + " (Keyword Search)")
    button_clicked = st.button("search")
    if search_keyword is not None and len(str(search_keyword)) > 0:
        st.write("Start song/track search")
        tracks = sp.search(q='track:'+ search_keyword, type='track', limit=20)
        track_list = tracks['tracks']['items']
        if len(track_list) > 0:
            for track in track_list:
                #st.write(track['name'] + ' - By - ' + track['artists'][0]['name'])
                search_results.append(track['name'] + '  by  '+ track['artists'][0]['name'])

selected_track = None
if  selected == 'Song/Track':
    selected_track = st.selectbox("Select your song/track: ", search_results)
    canzone.append(selected_track)
if selected_track is not None and len(tracks) > 0:
    track_list = tracks['tracks']['items']
    track_id = None
    if len(track_list) > 0:
        for track in track_list:
            str_temp = track['name'] + '  by  ' + track['artists'][0]['name']
            if str_temp == selected_track:
                track_id = track['id']
                track_album = track['album']['name']
                img_album = track['album']['images'][1]['url']
                #st.write(track_id, track_album, img_album)
                songrecommendations.save_album_image(img_album, track_id)
    selected_track_choice = None
    if track_id is not None:
        image = songrecommendations.get_album_mage(track_id)
        page = st.empty()
        canzone = selected_track.split("  by  ")
        titolo = canzone[0]
        artista = canzone[1]
        with page.container():
                img, title = st.columns([2, 4])
                with img:
                    st.image(image)

                with title:
                    st.markdown(f"""
                    #### 🎧 {titolo}
                    #### 🎤 {artista}
                    💿 {track_album} 
                    """)
        image = songrecommendations.get_album_mage(track_id)
        #st.image(image)
        track_choices = ['Song Features', 'Similar Songs Recommendation', 'Lyrics']
        selected_track_choice = st.sidebar.selectbox('Please select track choice: ', track_choices)
        if selected_track_choice == 'Song Features':
            track_features = sp.audio_features(track_id)
            df = pd.DataFrame(track_features, index=[0])
            df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness','liveness','speechiness','valence']]
            st.dataframe(df_features)
            polarplot.feature_plot(df_features)
        elif selected_track_choice == 'Similar Songs Recommendation':
            token = songrecommendations.get_token(client_id, client_secret)
            similar_song_json=songrecommendations.get_track_recommendations(track_id, token)
            recommendation_list = similar_song_json['tracks']
            recommendation_list_df = pd.DataFrame(recommendation_list)
            #st.dataframe(recommendation_list_df)
            recommendation_df = recommendation_list_df[['name', 'explicit','duration_ms', 'popularity']]
            st.dataframe(recommendation_df)
            #st.write("Reccomandations....")
            songrecommendations.song_recommendation_vis(recommendation_df)
        elif selected_track_choice == 'Lyrics':
            token = songrecommendations.get_token(client_id, client_secret)
            canzone = selected_track.split("  by  ")
            titolo = canzone[0]
            artista = canzone[1]
            song = genius.search_song(title=titolo, artist=artista)
            try:
                lyrics = song.lyrics
                lyrics = lyrics.split("Embed")[0]
                url = song.url
                st.write()
                st.write(lyrics)
                st.write(url)
            except:
                st.write()
                st.write(">> lyrics were not found")
                st.write()
    else:
        st.write("Please select a track from the list")
#endregion        

######################################################################################################

#ARTIST 
#region
if selected == "Artist":
    search_keyword = st.text_input(selected + " (Keyword Search)")
    button_clicked = st.button("search")
    search_results = []
    artist = []
    if search_keyword is not None and len(str(search_keyword)) > 0:
        st.write("Start artist search")
        artists = sp.search(q='artist:'+ search_keyword, type='artist', limit=20)
        artists_list = artists['artists']['items']
        if len(artists_list) > 0:
            for artist in artists_list:
                #st.write(artist['name'])
                search_results.append(artist['name'])

selected_artist = None
if selected == "Artist":
    selected_artist = st.selectbox("Select your artist: ", search_results)

if selected_artist is not None and len(artists) > 0:
    artists_list = artists['artists']['items']
    artist_id = None
    artist_uri = None
    artist_image = None
    selected_artist_choice = None
    if len(artists_list) > 0:
        for artist in artists_list:
            if selected_artist == artist['name']:
                artist_id = artist['id']
                artist_uri = artist['uri']
                artist_image = artist['images'][1]['url']
    st.image(artist_image,width=200)

    if artist_id is not None:
        artist_choice = ['Albums', 'Top Songs']
        selected_artist_choice = st.sidebar.selectbox('Select artist choice', artist_choice)
        
    if selected_artist_choice is not None:
        if selected_artist_choice == 'Albums':
            artist_uri = 'spotify:artist:' + artist_id
            album_result = sp.artist_albums(artist_uri, album_type='album')
            all_albums = album_result['items']
            col1, col2, col3 = st.columns((6,4,2))
            for album in all_albums:
                col1.write(album['name'])
                col2.write(album['release_date'])
                col3.write(album['total_tracks'])
        elif selected_artist_choice == 'Top Songs':
            artist_uri = 'spotify:artist:' + artist_id
            top_songs_result = sp.artist_top_tracks(artist_uri)
            for track in top_songs_result['tracks']:
                with st.container():
                    col1, col2, col3, col4 = st.columns((4,4,2,2))
                    col11, col12 = st.columns((10,2))
                    col21, col22 = st.columns((11,1))
                    col31, col32 = st.columns((11,1))
                    col1.write(track['id'])
                    col2.write(track['name'])
                    if track['preview_url'] is not None:
                        col11.write(track['preview_url'])
                        with col12:
                            st.audio(track['preview_url'], format="audio/mp3")
                    with col3:
                        def feature_requested():
                            track_features = sp.audio_features(track['id'])
                            df = pd.DataFrame(track_features, index=[0])
                            df_features = df.loc[:,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']]
                            with col21:
                                st.dataframe(df_features)
                            with col31:
                                polarplot.feature_plot(df_features)
                        
                        feature_button_state = st.button('Track Audio Features', key=track['id'], on_click=feature_requested)
                    
                    with col4:
                        def similar_song_requested():
                            token = songrecommendations.get_token(client_id, client_secret)
                            similar_song_json = songrecommendations.get_track_recommendations(track['id'], token)
                            recommendation_list = similar_song_json['tracks']
                            recommendation_list_df = pd.DataFrame(recommendation_list)
                            recommendation_df = recommendation_list_df[['name', 'explicit', 'duration_ms', 'popularity']]
                            with col21:
                                st.dataframe(recommendation_df)
                            with col31:
                                songrecommendations.song_recommendation_vis(recommendation_df)    
                        
                        similar_song_state = st.button('Similar Songs', key=track['name'], on_click=similar_song_requested)
                    st.write('----')
#endregion

######################################################################################################                

#ALBUM 
#region
if selected == "Album":
    search_keyword = st.text_input(selected + " (Keyword Search)")
    button_clicked = st.button("search")
    search_results = []
    album = []
    if search_keyword is not None and len(str(search_keyword)) > 0:
        st.write("Start album search")
        albums = sp.search(q='album:'+ search_keyword, type='album', limit=20)
        album_list = albums['albums']['items']
        if len(album_list) > 0:
            for album in album_list:
                #st.write(album['name'] + ' - By - ' + album['artists'][0]['name'])
                #print("Album ID: " + album['id'] + " / Artist ID - " + album['artists'][0]['id'])
                search_results.append(album['name'] + ' - By - ' + album['artists'][0]['name'])

selected_album = None
if selected == 'Album':
    selected_album = st.selectbox("Select your album: ", search_results)

if selected_album is not None and len(albums) > 0:
    albums_list = albums['albums']['items']
    album_id = None
    album_uri = None
    album_name = None
    if len(albums_list) > 0:
        for album in albums_list:
            str_temp = album['name'] + ' - By - ' + album['artists'][0]['name']
            if selected_album == str_temp:
                album_id = album['id']
                album_uri = album['uri']
                album_name = album['name']
    
    if album_id is not None and album_uri is not None:
        st.write("Collecting all the tracks for the album: " + album_name)
        album_tracks = sp.album_tracks(album_id)
        df_album_tracks = pd.DataFrame(album_tracks['items'])
        #st.dataframe(df_album_tracks)
        df_tracks_min =df_album_tracks.loc[:,
                        ['id', 'name', 'duration_ms', 'explicit', 'preview_url']]
        #st.dataframe(df_tracks_min)
        
        for idx in df_tracks_min.index:
            with st.container():
                col1, col2, col3, col4 = st.columns((4,4,1,1))
                col11, col12 = st.columns((8,2))
                col1.write(df_tracks_min['id'][idx])
                col2.write(df_tracks_min['name'][idx])
                col3.write(df_tracks_min['duration_ms'][idx])
                col4.write(df_tracks_min['explicit'][idx])
                if df_tracks_min['preview_url'][idx] is not None:
                    col11.write(df_tracks_min['preview_url'][idx])
                    with col12:
                        st.audio(df_tracks_min['preview_url'][idx], format="audio/mp3")
#endregion

###################################################################################################### 

#MY ARTIST
#region
#My Artists Page
if selected == 'My Artists':
    time_range_labels = {
        '1 mese': 'short_term',
        '6 mesi': 'medium_term',
        'sempre': 'long_term'
    }
    # ordina i brani in base alla selezione dell'utente

    time_range = time_range_labels['1 mese']
    col1,col2 = st.columns(2)
    color = col1.select_slider(
        'Seleziona il periodo',
        options=['1 mese', '6 mesi', 'sempre'])
    if color == '1 mese':
        time_range = time_range_labels['1 mese']
    elif color == '6 mesi':
        time_range = time_range_labels['6 mesi']
    else:
        time_range = time_range_labels['sempre']

    order_by = col2.selectbox("Ordina per", ["Artista 🎤", "Popolarità 🎉", "Followers"])

    # loop over Artist ids
    if time_range == 'short_term':
        top_artists = sp.current_user_top_artists(limit=32, offset=0, time_range=time_range)
        if order_by == "Artista 🎤":
            top_artists['items'].sort(key=lambda x: x['name'])
        elif order_by == "Popolarità 🎉":
            top_artists['items'].sort(key=lambda x: x['popularity'], reverse=True)
        else:
            foll = {}
            for i in range(len(top_artists)):
                artist_uri = top_artists['items'][i]['uri']
                art = sp.artist(artist_uri)
                foll[artist_uri] = art['followers']['total']
            sorted_artist = sorted(foll.items(), key=lambda x: x[1], reverse=True)
            top_artists['items'] = [sp.artist(artist[0]) for artist in sorted_artist]

        # Set the number of columns and items per column
        num_columns = 8
        items_per_column = 4
        q = 0

        # Loop through the artist results and display them in columns
        for i in range(32):
            col_items = top_artists['items'][i*items_per_column:(i+1)*items_per_column]
            col = st.columns(items_per_column)
            for j, item in enumerate(col_items):
                with col[j]:
                    st.image(item['images'][2]['url']) 
                    artist_uri = item['uri']
                    top_songs_result = sp.artist_top_tracks(artist_uri)
                    art = sp.artist(artist_uri)
                    top_songs_result = sp.artist_top_tracks(artist_uri)
                    top_songs = []
                    top_songs_url = []
                    for track in top_songs_result['tracks']:
                        top_songs.append(track['name'])
                        top_songs_url.append(track['preview_url'])
                    with st.expander("🎵"):
                        name = item['name']
                        follower = art['followers']['total']
                        popularity = item['popularity']
                        st.markdown(f"""
                                ###### 🎤 {name}
                                ###### 🚀 Popolarità: {popularity}
                                ###### N° Followers: {follower}
                                """)
                        st.markdown(f"""
                                ###### 1. {top_songs[0]}
                        """)
                        st.audio(top_songs_url[0], format="audio/mp3")
                        st.markdown(f"""
                                ###### 2. {top_songs[1]}
                        """)
                        st.audio(top_songs_url[1], format="audio/mp3")
                        st.markdown(f"""
                                ###### 3. {top_songs[2]}
                        """)
                        st.audio(top_songs_url[2], format="audio/mp3")
                        st.markdown(f"""
                                ###### 4. {top_songs[3]}
                        """)
                        st.audio(top_songs_url[4], format="audio/mp3")
                        st.markdown(f"""
                                ###### 5. {top_songs[4]}
                        """)
                        st.audio(top_songs_url[5], format="audio/mp3")
                    q = q+1    
            
######################################################################################################
    elif time_range == 'medium_term':
        top_artists = sp.current_user_top_artists(limit=32, offset=0, time_range=time_range)
        if order_by == "Artista 🎤":
            top_artists['items'].sort(key=lambda x: x['name'])
        elif order_by == "Popolarità 🎉":
            top_artists['items'].sort(key=lambda x: x['popularity'], reverse=True)
        else:
            foll = {}
            for i in range(len(top_artists)):
                artist_uri = top_artists['items'][i]['uri']
                art = sp.artist(artist_uri)
                foll[artist_uri] = art['followers']['total']
            sorted_artist = sorted(foll.items(), key=lambda x: x[1], reverse=True)
            top_artists['items'] = [sp.artist(artist[0]) for artist in sorted_artist]

        # Set the number of columns and items per column
        num_columns = 8
        items_per_column = 4
        q = 0
 
        # Loop through the artist results and display them in columns
        for i in range(32):
            col_items = top_artists['items'][i*items_per_column:(i+1)*items_per_column]
            col = st.columns(items_per_column)
            for j, item in enumerate(col_items):
                with col[j]:
                    st.image(item['images'][2]['url']) 
                    artist_uri = item['uri']
                    art = sp.artist(artist_uri)
                    top_songs_result = sp.artist_top_tracks(artist_uri)
                    top_songs = []
                    top_songs_url = []
                    for track in top_songs_result['tracks']:
                        top_songs.append(track['name'])
                        top_songs_url.append(track['preview_url'])
                    with st.expander("🎵"):
                        name = item['name']
                        follower = art['followers']['total']
                        popularity = item['popularity']
                        st.markdown(f"""
                                ###### 🎤 {name}
                                ###### 🚀 Popolarità: {popularity}
                                ###### N° Followers: {follower}
                                """)
                        st.markdown(f"""
                                ###### 1. {top_songs[0]}
                        """)
                        st.audio(top_songs_url[0], format="audio/mp3")
                        st.markdown(f"""
                                ###### 2. {top_songs[1]}
                        """)
                        st.audio(top_songs_url[1], format="audio/mp3")
                        st.markdown(f"""
                                ###### 3. {top_songs[2]}
                        """)
                        st.audio(top_songs_url[2], format="audio/mp3")
                        st.markdown(f"""
                                ###### 4. {top_songs[3]}
                        """)
                        st.audio(top_songs_url[4], format="audio/mp3")
                        st.markdown(f"""
                                ###### 5. {top_songs[4]}
                        """)
                        st.audio(top_songs_url[5], format="audio/mp3")
                    q = q+1
                
######################################################################################################
    if time_range == 'long_term':
        top_artists = sp.current_user_top_artists(limit=32, offset=0, time_range=time_range)
        if order_by == "Artista 🎤":
            top_artists['items'].sort(key=lambda x: x['name'])
        elif order_by == "Popolarità 🎉":
            top_artists['items'].sort(key=lambda x: x['popularity'], reverse=True)
        else:
            foll = {}
            for i in range(32):
                artist_uri = top_artists['items'][i]['uri']
                art = sp.artist(artist_uri)
                foll[artist_uri] = art['followers']['total']
            sorted_artist = sorted(foll.items(), key=lambda x: x[1], reverse=True)
            top_artists['items'] = [sp.artist(artist[0]) for artist in sorted_artist]

    # Set the number of columns and items per column
        num_columns = 8
        items_per_column = 4
        q = 0

        # Loop through the artist results and display them in columns
        for i in range(32):
            col_items = top_artists['items'][i*items_per_column:(i+1)*items_per_column]
            col = st.columns(items_per_column)
            for j, item in enumerate(col_items):
                with col[j]:
                    st.image(item['images'][2]['url']) 
                    artist_uri = item['uri']
                    art = sp.artist(artist_uri)
                    top_songs_result = sp.artist_top_tracks(artist_uri)
                    top_songs = []
                    top_songs_url = []
                    for track in top_songs_result['tracks']:
                        top_songs.append(track['name'])
                        top_songs_url.append(track['preview_url'])
                    with st.expander("🎵"):
                        name = item['name']
                        follower = art['followers']['total']
                        popularity = item['popularity']
                        st.markdown(f"""
                                ###### 🎤 {name}
                                ###### 🚀 Popolarità: {popularity}
                                ###### N° Followers: {follower}
                                """)
                        st.markdown(f"""
                                ###### 1. {top_songs[0]}
                        """)
                        st.audio(top_songs_url[0], format="audio/mp3")
                        st.markdown(f"""
                                ###### 2. {top_songs[1]}
                        """)
                        st.audio(top_songs_url[1], format="audio/mp3")
                        st.markdown(f"""
                                ###### 3. {top_songs[2]}
                        """)
                        st.audio(top_songs_url[2], format="audio/mp3")
                        st.markdown(f"""
                                ###### 4. {top_songs[3]}
                        """)
                        st.audio(top_songs_url[4], format="audio/mp3")
                        st.markdown(f"""
                                ###### 5. {top_songs[4]}
                        """)
                        st.audio(top_songs_url[5], format="audio/mp3")
                    q = q+1


#endregion

######################################################################################################

#MY PLAYLISTS 
#region

if selected == 'My Playlists':
    
    # Display the user's playlists
    playlists = sp.current_user_playlists()

    # set the number of images to display per row
    images_per_row = 3
    q = 0

    # add a selectbox to choose the track order
    order_by = st.selectbox("Order tracks by:", ["Appearance", "Popularity"])


    # iterate over the playlists
    for playlist in playlists['items']:
        # write the playlist name to the app
        st.write("Playlist:", playlist['name'])
        
        # get a list of the tracks in the playlist, ordered by appearance or popularity
        if order_by == "Popularity":

            # Sort the tracks by popularity
            #tracks = sorted(playlist['id'], key=lambda k: k['popularity'], reverse=True)

            #tracks = sp.playlist_tracks(playlist['id'], fields='items(track(name,album(images(url))), popularity)', sort_by='popularity')['items']
            tracks = sp.playlist_tracks(playlist['id'], fields='items(track(name,album(images(url))))')['items']
        else:
            tracks = sp.playlist_tracks(playlist['id'], fields='items(track(name,album(images(url))))')['items']
           
        # divide the app layout into columns
        columns = st.columns(images_per_row)

        # iterate over the tracks
        for i, track in enumerate(tracks):
            # get the image URL and display the image in the app
            image_url = track['track']['album']['images'][0]['url']
            image = Image.open(requests.get(image_url, stream=True).raw)
            
            # display the image in the appropriate column
            with columns[i % images_per_row]:
                # write the track name to the app
                if order_by == "Popularity":
                    st.write(f"{q+1}. {track['track']['name']}")
                    #st.write(f"Popularity: {track['popularity']}")
                    #st.write(track['track']['name'], " (popularity:", track['popularity'], ")")
                else:
                    st.write(f"{q+1}. {track['track']['name']}")
                st.image(image, width=200)
                q = q+1
#endregion

######################################################################################################

#MY PODCASTS
#region
if selected == 'My Podcasts':
    podcast_save = sp.current_user_saved_shows(limit=50)
    num_columns = 8
    items_per_column = 4
    q = 0

    # Loop through the artist results and display them in columns
    for i in range(32):
        col_items = podcast_save['items'][i*items_per_column:(i+1)*items_per_column]
        col = st.columns(items_per_column)
        for j, item in enumerate(col_items):
            with col[j]:
                st.image(item['show']['images'][1]['url']) 
                with st.expander("🎵"):
                    podcast = item['show']['name']
                    publisher = item['show']['publisher']
                    dataagg = item['added_at']
                    epid = item['show']['id']
                    epis_r = sp.show_episodes(epid)
                    epis = []
                    epiprev = []
                    for ep in epis_r['items']:
                        epis.append(ep['name'])
                        epiprev.append(ep['audio_preview_url'])
                    dt = datetime.strptime(dataagg, '%Y-%m-%dT%H:%M:%SZ')
                    dt_a = (dt.strftime('%Y-%m-%d'))
                    episodi = item['show']['total_episodes']
                    st.markdown(f"""
                            ###### 🎤 {podcast}
                            ###### 🎧 {publisher}
                            ###### 📆 {dt_a}
                            ###### ⏳ {episodi}
                            ###### 1. {epis[0]}
                     """)
                    st.audio(epiprev[0], format="audio/mp3")
                    st.markdown(f"""
                            ###### 2. {epis[1]}
                    """)
                    st.audio(epiprev[1], format="audio/mp3")
                    st.markdown(f"""
                            ###### 3. {epis[2]}
                    """)
                    st.audio(epiprev[2], format="audio/mp3")
                    st.markdown(f"""
                            ###### 4. {epis[3]}
                    """)
                    st.audio(epiprev[3], format="audio/mp3")
                    st.markdown(f"""
                            ###### 5. {epis[4]}
                    """)
                    st.audio(epiprev[4], format="audio/mp3")
                q = q+1

#endregion

######################################################################################################

#ANALISI CANZONI
#region
if selected == 'Community':
    user_id = sp.current_user()["id"]
    st.write(user_id)

    recently_played = sp.current_user_recently_played(limit=50)['items']
    song_names = []
    artists = []
    artists_id = [] 
    albums = []
    times = []
    durations_ms = []
    track_ids = []
    genere = []
    album_image = []
    for track in recently_played:
        song = track['track']['name']
        artist = track['track']['artists'][0]['name']
        artist_id = track['track']['artists'][0]['id']
        album = track['track']['album']['name']
        album_im = track['track']['album']['images'][1]['url']
        played_at = track['played_at']
        duration = track['track']['duration_ms']
        id = track['track']['id']
        song_names.append(song)
        artists.append(artist)
        artists_id.append(artist_id)
        albums.append(album)
        played_at_dt = funzioni.str_to_datetime(played_at)
        times.append(played_at_dt)
        durations_ms.append(duration)
        track_ids.append(id)
        album_image.append(album_im)
    # Reverse The Lists So The Data Is Aligned From Oldest Played Songs To Newest Played Songs
    song_names.reverse()
    artists.reverse()
    artists_id.reverse()
    albums.reverse()
    times.reverse()
    durations_ms.reverse()
    track_ids.reverse()
    album_image.reverse()


    #result = sp.search("Capri sun")
    #track = result['tracks']['items'][0]

    #artist = sp.artist(track["artists"][0]["external_urls"]["spotify"])
    #st.write("artist genres:", artist["genres"])

    #album = sp.album(track["album"]["external_urls"]["spotify"])
    #st.write("album genres:", album["genres"])
    #st.write("album release-date:", album["release_date"])

    songs_data_dict = {
            'song_names': song_names,
            'artists': artists,
            'artists_id':artists_id,
            'albums': albums,
            'time_played': times,
            'duration_ms': durations_ms,
            'track_ids': track_ids,
            'albums_image': album_image,
            'id_name':sp.current_user()["id"]

        }


    # Create an empty list to store the genres
    genres = []

    # Loop through the list of artists in the songs_data_dict
    for artist in songs_data_dict['artists']:
        # Search for the artist on Spotify
        result = sp.search(artist, type='artist')
        
        # Get the first artist in the search results
        first_artist = result['artists']['items'][0]
        
        # Get the genres of the first artist
        artist_genres = first_artist['genres']
        
        # Add the genres to the list of genres
        genres.append(artist_genres)

    test1 = pd.DataFrame(songs_data_dict)
    test1 = test1.assign(genres=genres)
    with open(r"/Users/fabiotraina/Desktop/Project Work😱/SpotifyWrapped/my_data.csv", mode = 'a') as f:
        test1.to_csv(f, header=f.tell()==0, index=False)

    df_songs = pd.read_csv('/Users/fabiotraina/Desktop/Project Work😱/SpotifyWrapped/my_data.csv',delimiter=',')
    df_songs.drop_duplicates(subset=['time_played'], inplace=True)
    #st.write(df_songs)

    # Converti i millisecondi in minuti
    df_songs['minuti'] = round(df_songs['duration_ms'] / 60000)
    # Estrai la data dall'ora di ascolto
    df_songs['time_played'] = pd.to_datetime(df_songs['time_played'], format='%Y-%m-%d %H:%M').dt.date
    # Raggruppa per data e somma i minuti
    df_gruppo = df_songs.groupby(['time_played'])['minuti'].sum().reset_index()
    # Crea il grafico a linee
    #st.line_chart(df_gruppo.set_index('time_played'))


    # Raggruppa per data e ID e somma i minuti
    df_gruppo1 = df_songs.groupby(['time_played', 'id'])['minuti'].sum().reset_index()
    #st.write(df_gruppo)
    #st.write(df_gruppo1)
    # Crea il grafico a linee per la somma dei minuti per data
    #st.line_chart(df_gruppo1.groupby(['time_played'])['minuti'].sum().reset_index().set_index('time_played'))

    chart = alt.Chart(df_gruppo1).mark_line().encode(
        x='yearmonthdate(time_played):Q',
        y='minuti:Q',
        color='id:N'
    )

    #st.altair_chart(chart, use_container_width=True)

    df_user = df_gruppo1[df_gruppo1['id'] == user_id]
    #st.write(df_user)

    df_merged = pd.concat([df_gruppo1, df_user])
    #st.write(df_merged)



    # Calcola i minuti al giorno per user_id
    df_user = df_songs[df_songs['id'] == user_id].groupby('time_played')['minuti'].sum().reset_index()
    df_user['id'] = str(user_id)

    # Calcola i minuti al giorno per tutti gli utenti
    df_others = df_songs.groupby('time_played')['minuti'].sum().reset_index()
    df_others['id'] = 'others'

    # Unisci i dati
    df_merged = pd.concat([df_user, df_others])
    #st.write(df_merged)

    # Crea il grafico
    chart = alt.Chart(df_merged).mark_line().encode(
        x='time_played:T',
        y='minuti:Q',
        color='id:N',
        tooltip='minuti:Q',
    )

    st.altair_chart(chart, use_container_width=True)
#endregion
