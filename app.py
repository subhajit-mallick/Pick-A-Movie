import streamlit as st
import pickle
import pandas as pd
import time
import json
import requests

api_key = st.secrets.API_KEY

movie_dict = pickle.load(open('movies.pkl', 'rb'))
movies_df = pd.DataFrame(movie_dict)
similarity_matrix = pickle.load(open('similarity.pkl', 'rb'))

st.set_page_config(
    page_title="Pick-A-Movie",
    page_icon="📺",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        'About': "Made with ❤ by Subhajit Mallick, KGEC-CSE-23', "
                 "for the purpose of self learning & implementation of ML concepts. "
                 "This Project is not meant for commercial use."
    }
)


def fetch_overview(movie_id):
    res = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US')
    data = json.loads(res.text)
    return data['overview']


def recommend(movie, is_lang_pref):
    i = movies_df[movies_df['title'] == movie].index[0]
    dist_arr = similarity_matrix[i]

    pref_lang = movies_df.iloc[i].tags[-2:]
    lst = sorted(list(enumerate(dist_arr)), reverse=True, key=lambda x: x[1])
    lst_pl = [x for x in lst if movies_df.iloc[x[0]]['tags'][-2:] == pref_lang][:6]
    lst = lst[:6]

    top_movies = lst_pl if is_lang_pref else lst
    return [(movies_df.iloc[i[0]].title, movies_df.iloc[i[0]].poster_path) for i in top_movies]


st.title("Pick-A-Movie")

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@500&display=swap" rel="stylesheet">
<style>
.big-font {
    font-size:30px;
    font-family: 'Dancing Script', cursive;
    }
</style>
""", unsafe_allow_html=True)
st.markdown('<p class="big-font">A Movie Recommender Engine.</p>', unsafe_allow_html=True)

option = st.selectbox(
    'Pick a movie YOU Like',
    movies_df['title'].values)

agree = st.checkbox('I prefer Movies of the same Language.', True)


def displayMovie(pos, ifw=False):
    st.write(movies[pos][0])

    if ifw:
        st.image(f"https://image.tmdb.org/t/p/w500{movies[pos][1]}", width=200)
    else:
        st.image(f"https://image.tmdb.org/t/p/w500{movies[pos][1]}", use_column_width='auto')

    # st.write("-------------------------")
    st.markdown('<hr>', unsafe_allow_html=True)


if st.button('Recommend'):
    if agree:
        movies = recommend(option, True)
    else:
        movies = recommend(option, False)

    tab1, tab2 = st.tabs(["Recommendations", "Your Pick"])

    with tab1:
        with st.spinner('Finding the best movies...'):
            time.sleep(1)
        st.success('Here You Go! Add this movies to your Watchlist.')

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            displayMovie(1)

        with col2:
            displayMovie(2)

        with col3:
            displayMovie(3)

        with col4:
            displayMovie(4)

        with col5:
            displayMovie(5)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            displayMovie(0, ifw=True)

        with col2:
            m_id = movies_df[movies_df['title'] == option].id.iloc[0]
            st.subheader('Overview')
            st.write(fetch_overview(m_id))
