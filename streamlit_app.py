import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

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

_func = st.sidebar.radio(label="Functions", options = ['Display', 'Highlight'])
gd = GridOptionsBuilder.from_dataframe(df)
gd.configure_pagination(enabled = True)
gd.configure_default_column(editable = True, groupable = True)

if _func == 'Display':
    sel_mode = st.radio('Selection Type', options = ['single', 'multiple'])
    gd.configure_selection(selection_mode = sel_mode, use_checkbox = True)
    gridoptions = gd.build()
    grid_table = AgGrid(df, gridOptions=gridoptions,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        height=500,
                        width = '100%',
                        allow_unsafe_jscode=True,
                        theme= 'alpine',
                        reload_data = True)

    sel_row = grid_table["selected_rows"]
    st.write(sel_row)
if _func == 'Highlight':
    col_opt = st.selectbox(label = 'Select column', options = df.columns)
    cellstyle_jscode = JsCode("""
        function(params){
            if (params.value == 'Mais') {
                return {
                    'color': 'black',
                    'backgroundColor': 'orange'
            }
            }
    };
    """)
    gd.configure_columns(col_opt, cellStyle = cellstyle_jscode)
    gridoptions = gd.build()
    grid_table = AgGrid(df, gridOptions=gridoptions,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        enable_enterprise_modules = True,
                        fit_columns_on_grid_load = True,
                        height = 800,
                        width = '100%',
                        allow_unsafe_jscode = True,
                        theme = 'material',
                        reload_data = True)
