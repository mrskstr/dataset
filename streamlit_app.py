import altair as alt
import pandas as pd
import streamlit as st

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


# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/mais.csv")
    return df


df = load_data()

# Show a multiselect widget with the genres using `st.multiselect`.
categories = st.multiselect(
    "Kategorie",
    df.category.unique(),
    ["Mais", "Maiskörner"],
)

# Show a slider widget with the years using `st.slider`.
price = st.slider("Preis", 0, 1, (0.2, 0.6))

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[(df["name"].isin(categories)) & (df["offer_price_unitPrice_value"].between(price[0], price[1]))]
df_filtered["Favorite"] = False

columns_order = ["Favorite"] + [col for col in df_filtered.columns if col != "Favorite"]
df_filtered = df_filtered[columns_order]

st.write("### Filtered Dataset with Favorite Selection")
edited_df = st.data_editor(
    df_filtered,
    column_config={
        "Favorite": st.column_config.CheckboxColumn(
            label="Your favorite?", help="Mark your favorite movies", default=False
        ),
    },
    hide_index=True,  # Hide the index column for a cleaner look
    use_container_width=True,  # Make it responsive
)
'''
# Display the updated data after checkbox selections
st.write("### Updated Dataset")
st.dataframe(edited_df)
'''
# Filter for selected rows (favorites) and sort them by year
selected_rows = edited_df[edited_df["Favorite"]].sort_values(by="year")

if not selected_rows.empty:
    # Display selected rows in a separate table
    st.write("### Selected Rows Ordered by Year")
    st.dataframe(selected_rows, use_container_width=True)
else:
    st.write("No favorites selected. Select your favorite movies to see them here.")


st.image("https://image.migros.ch/mo-boxed/v-w-960-h-720/50042af4e97791d9891cd42c3564b43dc176f45f/m-classic-ip-suisse-weissmehl.jpg", width= 50)

st.markdown(
    """
    <style>
    img {
        cursor: pointer;
        transition: all .2s ease-in-out;
    }
    img:hover {
        transform: scale(4);
    }
    </style>
    """,
    unsafe_allow_html=True,
)



'''
df_reshaped = df_filtered.pivot_table(
    index="year", columns="genre", values="gross", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="year", ascending=False)
'''

'''
# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_reshaped,
    use_container_width=True,
    column_config={"year": st.column_config.TextColumn("Year")},
)
'''



'''
# Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="year", var_name="genre", value_name="gross"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("year:N", title="Year"),
        y=alt.Y("gross:Q", title="Gross earnings ($)"),
        color="genre:N",
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)
'''