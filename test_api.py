import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import requests
import json
import plotly.graph_objects as go
import time
import concurrent.futures

# Function to fetch API data
@st.cache_data(ttl=3600)


def fetch_api_data_request(payload_chunk):
    response = requests.post(
        'https://www.notvorratsrechner.bwl.admin.ch/api/v1/values/',
        json=payload_chunk,
        headers = {
            'accept': 'application/json',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'de',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'cookie': 'eportal-last-user-activity=1733846827591; i18n_redirected=de',
            'origin': 'https://www.notvorratsrechner.bwl.admin.ch',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-platform': '"macOS"'
        }
    )
    return response.json()

def fetch_api_data(payload):
    # Use cURL instead of requests
    import subprocess
    import json

    # Prepare the cURL command
    curl_command = [
        "curl",
        "-X", "POST",
        "https://www.notvorratsrechner.bwl.admin.ch/api/v1/values/",
        "-H", "accept: application/json",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]

    # Execute the cURL command and capture the response
    try:
        response = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        return json.loads(response.stdout)
    except Exception as e:
        st.error(f"cURL failed: {e}")
        return None


# Set Streamlit page configuration
st.set_page_config(page_title="Notvorrat", page_icon=":fork_and_knife:", layout="wide")

# Initialize session state for the API response
if "api_response" not in st.session_state:
    st.session_state["api_response"] = None

# Initialize session state for the dataframe
if "df" not in st.session_state:
    @st.cache_data
    def load_data():
        df = pd.read_csv("dataset/data/mais.csv")
        df['Counter'] = 0  # Add Counter column to the DataFrame for filtering
        return df

    st.session_state["df"] = load_data()

if "updated_data" not in st.session_state:
    st.session_state["updated_data"] = None

# Top panel setup
st.title("Notvorrat")
'''
# Custom counter function
def custom_counter(label, key, default_value=0, min_value=0, max_value=10):
    # Use session state to maintain counter value
    if key not in st.session_state:
        st.session_state[key] = default_value

    # Create expander-like styling
    with st.container():
        st.text(label)
        col1, col2, col3 = st.columns([1, 2, 1])

        # Minus button
        with col1:
            if st.button("-", key=f"{key}_minus"):
                if st.session_state[key] > min_value:
                    st.session_state[key] -= 1

        # Counter display
        with col2:
            st.write(f"**{st.session_state[key]}**", unsafe_allow_html=True)

        # Plus button
        with col3:
            if st.button("+", key=f"{key}_plus"):
                if st.session_state[key] < max_value:
                    st.session_state[key] += 1

    return st.session_state[key]

def custom_counter(label, key, default_value=0, min_value=0, max_value=10):
    # Initialize the counter in session state if not already set
    if key not in st.session_state:
        st.session_state[key] = default_value

    # Define callback functions for incrementing and decrementing
    def increment():
        if st.session_state[key] < max_value:
            st.session_state[key] += 1

    def decrement():
        if st.session_state[key] > min_value:
            st.session_state[key] -= 1

    # Create a container for the custom counter
    with st.container():
        st.text(label)
        col1, col2, col3 = st.columns([1, 2, 1])

        # Minus button with callback
        with col1:
            st.button("-", key=f"{key}_minus", on_click=decrement)

        # Display the current counter value
        with col2:
            st.write(f"**{st.session_state[key]}**", unsafe_allow_html=True)

        # Plus button with callback
        with col3:
            st.button("+", key=f"{key}_plus", on_click=increment)

    # Return the current counter value
    return st.session_state[key]
'''

def custom_counter(label, key, default_value=0, min_value=0, max_value=10):
    # Initialize the counter in session state if not already set
    if key not in st.session_state:
        st.session_state[key] = default_value

    # Define callback functions for incrementing and decrementing
    def increment():
        if st.session_state[key] < max_value:
            st.session_state[key] += 1

    def decrement():
        if st.session_state[key] > min_value:
            st.session_state[key] -= 1

    # Custom CSS for buttons and layout
    st.markdown(
        """
        <style>
        .counter-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .counter-button {
            display: inline-block;
            padding: 6px 12px;
            font-size: 18px;
            font-weight: bold;
            background-color: #f0f2f6;
            color: black;
            border: 1px solid #d9d9d9;
            border-radius: 5px;
            text-align: center;
            cursor: pointer;
        }
        .counter-value {
            font-size: 20px;
            font-weight: bold;
            min-width: 30px;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Display the counter UI
    st.text(label)  # Counter label
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        # Minus button
        if st.button("➖", key=f"{key}_minus", on_click=decrement):
            pass

    with col2:
        # Counter display
        st.markdown(
            f"<div class='counter-value'>{st.session_state[key]}</div>",
            unsafe_allow_html=True,
        )

    with col3:
        # Plus button
        if st.button("➕", key=f"{key}_plus", on_click=increment):
            pass

    return st.session_state[key]

intolerances_options = ["GLUTEN", "LACTOSE", "NUTS"]

# Create a form to configure the household
with st.container():
    col1, col2 = st.columns([2, 5])  # Left and right columns with relative widths

    with col1:
        st.header("Haushaltsgrösse")

        # Custom counters for number of adults and kids
        num_adults = custom_counter("Erwachsene, Jugendliche (16+ Jahre)", key="num_adults", default_value=2)
        num_kids = custom_counter("Kinder (2 bis 16 Jahre)", key="num_kids", default_value=1)

        # Initialize the payload
        household_payload = {"persons": [], "daysCount": 7}
        # Custom mapping for options and display labels
        preferences_map = {
            "CONSUMING_MEAT": "Fleischkonsumierend",
            "VEGETARIAN": "Vegetarisch"
        }

        # Function to handle radio with custom labels
        def custom_radio(label, options, custom_labels, key):
            # Reverse map for retrieving the original option from the label
            reverse_map = {v: k for k, v in preferences_map.items()}

            # Display the custom labels as a radio selection
            selected_label = st.radio(
                label,
                options=[custom_labels[opt] for opt in options],
                horizontal=True,
                key=key,
                label_visibility="collapsed"
            )
            # Return the original option
            return reverse_map[selected_label]

        # Custom mapping for intolerances and display labels
        intolerances_map = {
            "GLUTEN": "Gluten",
            "LACTOSE": "Laktose",
            "NUTS": "Nüsse"
        }
        # Reverse mapping to retrieve the original keys for the payload
        reverse_intolerances_map = {v: k for k, v in intolerances_map.items()}
        # Generate sections for adults
        st.subheader("Details zu den Ernährungsgewohnheiten")
        for i in range(num_adults):
            with st.expander(f"Erwachsene, Jugendliche {i + 1}"):
                st.text("Ernährungsform")
                preference = custom_radio(f"Ernährungsform",
                    options=["CONSUMING_MEAT", "VEGETARIAN"],
                    key=f"adult_{i + 1}",
                    custom_labels=preferences_map
                )

                # Checkboxes for intolerances
                intolerances_selected = []
                st.text("Unverträglichkeiten")
                for option, label in intolerances_map.items():
                    if st.checkbox(label, key=f"adult_{i + 1}_{option}"):
                        intolerances_selected.append(option)

                household_payload["persons"].append({
                    "type": "adult",
                    "preferences": preference,
                    "intolerances": intolerances_selected,
                    "key": f"adult_{i + 1}"
                })

        # Generate sections for kids
        #st.subheader("Kids Configuration")
        for i in range(num_kids):
            with st.expander(f"Kind {i + 1}"):
                st.text("Ernährungsform")
                preference = custom_radio(f"Ernährungsform",
                    options=["CONSUMING_MEAT", "VEGETARIAN"],
                    key=f"kid_{i + 1}",
                    custom_labels=preferences_map
                )

                # Checkboxes for intolerances
                intolerances_selected = []
                st.text("Unverträglichkeiten")
                for option, label in intolerances_map.items():
                    if st.checkbox(label, key=f"kid_{i + 1}_{option}"):
                        intolerances_selected.append(option)

                household_payload["persons"].append({
                    "type": "kid",
                    "preferences": preference,
                    "intolerances": intolerances_selected
                })

        # Show the payload for debugging
        st.write("Household Payload:", household_payload)
        # Slider for daysCount
        st.header("Zeitraum (3-14 Tage)")
        days_count = st.slider(
            "Für welchen Zeitraum möchten Sie sich unabhängig versorgen?",
            min_value=3,
            max_value=14,
            value=7,
            step=1,
            key="days_count"
        )
        household_payload["daysCount"] = days_count
        # Button to fetch API data with the generated payload
        if st.button("Fetch API Data"):
            try:
                start_time = time.time()
                response_data = fetch_api_data(household_payload)
                elapsed_time = time.time() - start_time
                st.write(f"Response time: {elapsed_time:.2f} seconds")
                st.session_state["api_response"] = response_data
                st.success("Data fetched successfully!")
            except Exception as e:
                st.error(f"Error fetching API data: {e}")

# Display the API response (if available)
if st.session_state["api_response"]:
    st.subheader("API Response")
    st.json(st.session_state["api_response"])
