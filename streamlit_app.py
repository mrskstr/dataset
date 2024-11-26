import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

# Show the page title and description.
st.set_page_config(page_title="Dataset", page_icon="🎬")
st.title("🎬 Dataset")
st.write(
    """
    This app visualizes food data from [The Movie Database (TMDB)](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata).
    It shows which movie genre performed best at the box office over the years. Just 
    click on the widgets below to explore!
    """
)

# Load the data from a CSV. We're caching this so it doesn't reload every time the app reruns.
@st.cache_data
def load_data():
    df = pd.read_csv("data/mais.csv")
    return df

df = load_data()
st.dataframe(data = df)
st.info(len(df))

'''
gd = GridOptionsBuilder.from_dataframe(df)
gd.configure_pagination(enabled = True)
gd.configure_default_column(editable = True, groupable = True)
sel_mode = st.radio('Selection Type', options = ['single', 'multiple'])
gd.configure_selection(selection_mode = sel_mode, use_checkbox = True)
AgGrid(df)
'''