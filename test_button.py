import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie
import requests
import json
import time

# Mock API response
api_response = {
    "products": [
        {"name": "Apple", "description": "Fresh red apple", "total": 5},
        {"name": "Banana", "description": "Yellow ripe banana", "total": 10},
        {"name": "Cherry", "description": "Sweet red cherries", "total": 2},
    ]
}

# Prepare data
table_data = [
    {"name": f"{item['name']} ({item['description']})", "total": item['total']}
    for item in api_response["products"]
]
response_df = pd.DataFrame(table_data)

# Icon URL (Coffee bean icon)
coffee_icon_url = "https://cdn-icons-png.flaticon.com/512/2812/2812007.png"

# CSS style for the buttons and layout
button_style = """
<style>
.stButton > button {
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 10px;
    margin: 0;
    background-color: white;
    display: flex;
    justify-content: space-between; /* Distribute space evenly between elements */
    align-items: center; /* Vertically center the content */
    width: 100%; /* Button takes full width */
    height: 60px; /* Fixed height for consistency */
}

.stButton > button .counter {
    font-size: 20px; /* Same style for counter */
    font-weight: bold;
    color: #333;
    width: 55%; /* Assign more width to the counter */
    text-align: center;
}

.stButton > button .total {
    font-size: 20px; /* Same style for total */
    font-weight: bold;
    color: #333;
    width: 35%; /* Smaller width for total */
    text-align: left;
}

.stButton > button img {
    width: 32px;
    height: 32px;
    vertical-align: middle; /* Ensures icon is aligned with text */
}
/* Green background when counter equals total */
.green-button {
    background-color: green !important;
    color: white;
}
</style>
"""

# Display the button styles
st.markdown(button_style, unsafe_allow_html=True)

# Display buttons for each product in columns
for index, row in response_df.iterrows():
    col1, col2 = st.columns([1, 4], gap="small")  # Adjust gap between columns
    
    # Initialize the counter in session_state if not already present
    counter_key = f"counter_{index}"
    edit_key = f"editing_{index}"
    
    if counter_key not in st.session_state:
        st.session_state[counter_key] = 0
    
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False

    # Handle button click to toggle editing state
    with col2:
        if st.button(f"Bitte {row['name']} auswählen", key=f"click_{index}"):
            st.session_state[edit_key] = not st.session_state[edit_key]

        if st.session_state[edit_key]:
            # Show the + and - buttons only when the product is clicked
            col3, col4 = st.columns([1, 1])  # Two small columns for the buttons
            with col3:
                if st.button("+", key=f"increment_{index}"):
                    st.session_state[counter_key] += 1  # Increment the counter
            with col4:
                if st.button("-", key=f"decrement_{index}"):
                    if st.session_state[counter_key] > 0:
                        st.session_state[counter_key] -= 1  # Decrement the counter
    # Dynamically generate button HTML based on current counter state
    # Check if the counter equals the total
    button_class = "green-button" if st.session_state[counter_key] >= row['total'] else ""
    button_html = f"""
    <div class="stButton">
        <button class="{button_class}">
            <span class="counter">{st.session_state[counter_key]}  /</span> <!-- Add separator -->
            <span class="total">{row['total']}</span>  <!-- Display Total -->
            <img src="{coffee_icon_url}" alt="Coffee Bean">  <!-- Display Icon -->
        </button>
    </div>
    """
    # st.markdown(button_html) has to be called after col2, because otherwise it wouldn't update correctly when changing the counter above
    with col1: 
        st.markdown(button_html, unsafe_allow_html=True)
    # If counter reaches total, trigger celebration
    if st.session_state[counter_key] == row['total']:
        # Load Lottie animation JSON
        def load_lottie_url(url):
            response = requests.get(url)
            if response.status_code != 200:
                return None
            return response.json()

        # Example animation URL from LottieFiles
        lottie_animation = load_lottie_url("https://lottie.host/7d489e39-eb4f-4458-8557-e96a4656f3e9/N43AdkBQDR.json")
        if lottie_animation:
            animation_placeholder = st.empty()
            with animation_placeholder.container():
                st_lottie(lottie_animation, height=60, width=60, loop=False)
            time.sleep(3)
            animation_placeholder.empty()
        else:
            st.error("Failed to load Lottie animation. Please check the URL.")
