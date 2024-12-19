import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import requests
import json
#import streamlit.components.v1 as components
import plotly.graph_objects as go
import time
from streamlit_lottie import st_lottie

# JS Renderer
# Thumbnail renderer (for images column)
thumbnail_renderer = JsCode("""
        class ThumbnailRenderer {
            init(params) {
            this.eGui = document.createElement('div');
            this.eGui.style.display = 'flex';
            this.eGui.style.justifyContent = 'center';
            this.eGui.style.alignItems = 'center';
            const img = document.createElement('img');
            img.setAttribute('src', params.value);
            img.setAttribute('width', '120');
            img.setAttribute('height', 'auto');
            img.style.cursor = 'pointer';
            img.style.transition = 'transform 0.4s';
            img.addEventListener('mouseenter', () => img.style.transform = 'scale(2.5)');
            img.addEventListener('mouseleave', () => img.style.transform = 'scale(1)');
            this.eGui.appendChild(img);
            }

            getGui() {
                return this.eGui;
            }
        }
""")
counter_renderer = JsCode("""
class CounterRenderer {
    init(params) {
        this.count = params.value || 0;
        this.params = params;
        this.eGui = document.createElement('div');
        this.eGui.style.display = 'flex';
        this.eGui.style.alignItems = 'center';
        this.eGui.style.justifyContent = 'center';
        this.eGui.style.position = 'relative';

        const minusButton = document.createElement('button');
        minusButton.textContent = '-';
        this.styleButton(minusButton, '#FF6B6B', '#FFF');
        minusButton.addEventListener('click', () => this.updateCount(-1));

        this.counterDisplay = document.createElement('input');
        this.counterDisplay.type = 'text';
        this.counterDisplay.value = this.count;
        this.counterDisplay.style.width = '40px';
        this.counterDisplay.style.textAlign = 'center';
        this.counterDisplay.style.fontWeight = 'bold';
        this.counterDisplay.addEventListener('blur', this.onInputBlur.bind(this));
        this.counterDisplay.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') this.onInputBlur();
        });

        const plusButton = document.createElement('button');
        plusButton.textContent = '+';
        this.styleButton(plusButton, '#6BCB77', '#FFF');
        plusButton.addEventListener('click', () => this.updateCount(1));

        // Create the animation span (Initially hidden)
        this.animationSpan = document.createElement('span');
        this.animationSpan.style.position = 'absolute';
        this.animationSpan.style.top = '-20px';
        this.animationSpan.style.left = '50%';
        this.animationSpan.style.transform = 'translateX(-50%)';
        this.animationSpan.style.fontSize = '14px';
        this.animationSpan.style.fontWeight = 'bold';
        this.animationSpan.style.opacity = '0';
        this.animationSpan.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
        
        this.eGui.appendChild(minusButton);
        this.eGui.appendChild(this.counterDisplay);
        this.eGui.appendChild(plusButton);
        this.eGui.appendChild(this.animationSpan);
    }

    getGui() {
        return this.eGui;
    }

    styleButton(button, bgColor, textColor) {
        button.style.backgroundColor = bgColor;
        button.style.color = textColor;
        button.style.border = 'none';
        button.style.borderRadius = '5px';
        button.style.padding = '5px 10px';
        button.style.margin = '0 5px';
        button.style.cursor = 'pointer';
    }

    updateCount(delta) {
        this.count = Math.max(0, this.count + delta);
        this.counterDisplay.value = this.count;
        this.params.node.setDataValue('Counter', this.count);

        // Show animation based on the action (Added or Removed)
        const animationText = delta > 0 ? 'Product Added' : 'Product Removed';
        const animationColor = delta > 0 ? '#6BCB77' : '#FF6B6B';
        this.showAnimation(animationText, animationColor);
    }

    onInputBlur() {
        const newValue = parseInt(this.counterDisplay.value, 10);
        if (!isNaN(newValue)) {
            this.count = newValue;
            this.params.node.setDataValue('Counter', this.count);
        } else {
            this.counterDisplay.value = this.count;
        }
    }

    showAnimation(text, color) {
        this.animationSpan.textContent = text;
        this.animationSpan.style.color = color;

        // Animate: Fade in and move upward
        this.animationSpan.style.opacity = '1';
        this.animationSpan.style.transform = 'translate(-50%, -30px)';
        
        // After animation completes, reset opacity and position
        setTimeout(() => {
            this.animationSpan.style.opacity = '0';
            this.animationSpan.style.transform = 'translate(-50%, -20px)';
        }, 500); // Wait for animation to complete (500ms)
    }
}
""")
# CSS for styling the HTML table and the st.button
table_style = """
    <style>
    table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    th, td {
        padding: 12px 15px;
        text-align: left;
        border: 1px solid #ddd;
        font-size: 14px;
    }
    th {
        background-color: #f4f4f4;
        font-weight: bold;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    tr:hover {
        background-color: #f1f1f1;
    }
    td {
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
    }

    /* Styling the '>' symbol button */
    .stButton[data-testid="stButton.calculate_button"]>button {
        font-size: 18px;
        color: #4CAF50;
        background-color: transparent;
        border: none;
        cursor: pointer;
        padding: 5px 10px;
        text-align: center;
        display: inline-block;
        margin-top: 5px;
        transition: transform 0.3s ease;
    }

    /* Hover effect to show details text */
    .stButton>button:hover {
        color: #45a049;
        transform: scale(1.2);
    }

    /* Styling for text that appears on hover */
    .stButton>button .expand-text {
        visibility: hidden;
        position: absolute;
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        transition: visibility 0s, opacity 0.3s linear;
        opacity: 0;
        z-index: 1;
    }

    .stButton>button:hover .expand-text {
        visibility: visible;
        opacity: 1;
    }

    </style>
"""
# Set Streamlit page configuration
st.set_page_config(page_title="Notvorrat", page_icon=":fork_and_knife:", layout="wide")
# Background CSS
background_css = """
<style>
body {
    background-color: #f0f0f5;
    background-image: url('https://your-image-url.com/background.jpg');
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center;
}
footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background-image: url('/Users/ma/Downloads/storage room in a cozy mountain hut filled with colorful cans, other foodstuff, water bottles, grains, packs of spaghetti , beer, wine, drinks.jpg');
    color: white;
    text-align: center;
    padding: 10px;
}
</style>
"""

# Header HTML
header_html = """
<div style="background-color: #4CAF50; padding: 0px; text-align: center; color: white; font-size: 24px; font-weight: bold;">
    Welcome to My Streamlit App!
</div>
"""

# Footer HTML
footer_html = """
<footer>
    <p>&copy; 2024 My Streamlit App. All Rights Reserved.</p>
</footer>
"""

# Inject CSS and HTML
st.markdown(background_css, unsafe_allow_html=True)
st.markdown(header_html, unsafe_allow_html=True)

# Your main app content
st.title("Main Content")
st.write("This is the main area of the app.")
# Inject custom HTML and CSS
st.markdown("""
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
        }

        .content {
            padding: 20px;
            text-align: center;
        }

        .image-bar {
            position: relative;
            width: 100%;
            height: 200px; /* Adjust height as needed */
            background-image: url('dataset/data/img/storage.jpg')
            background-position: center;
        }

        .image-bar::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 1) 100%);
            pointer-events: none; /* Ensure this doesn't block interaction */
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <div class="image-bar"></div>
""", unsafe_allow_html=True)

# Footer
st.markdown(footer_html, unsafe_allow_html=True)



# Initialize session state for API response
if "api_response" not in st.session_state:
    st.session_state["api_response"] = None
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
        "-H", 'accept-language: de',
        "-d", json.dumps(payload)
    ]

    # Execute the cURL command and capture the response
    try:
        response = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        return json.loads(response.stdout)
    except Exception as e:
        st.error(f"cURL failed: {e}")
        return None

# Initialize session state
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
        #st.write("Household Payload:", household_payload)
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
        if st.button("Notvorrat berechnen"):
            try:
                start_time = time.time()
                response_data = fetch_api_data(household_payload)
                elapsed_time = time.time() - start_time
                st.write(f"Response time: {elapsed_time:.2f} seconds")
                st.session_state["api_response"] = response_data
                st.success("Data fetched successfully!")
                def load_lottie_url(url):
                    response = requests.get(url)
                    if response.status_code != 200:
                        return None
                    return response.json()
                with col2:
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
            except Exception as e:
                st.error(f"Error fetching API data: {e}")

    with col2:
        if st.session_state["api_response"]:
            st.header("Ihr Notvorrat")
            api_response = st.session_state["api_response"]
            
            if "products" in api_response:
                # Extract and display as a table
                table_data = [
                    {"name": f"{item['name']} ({item['description']})", "total": item['total']}
                    for item in api_response["products"]
                ]
                response_df = pd.DataFrame(table_data)
                # Icon URL (Coffee bean icon)
                icons_url = ["https://cdn-icons-png.flaticon.com/512/2812/2812007.png", 
                             "https://cdn-icons-png.flaticon.com/512/14355/14355134.png"]

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

                # Display buttons for each product in columns
                for index, row in response_df.iloc[:2].iterrows():
                    # Unique keys for this row
                    expand_key = f"expand_{index}"
                    counter_0_key = f"counter_0_{expand_key}"  # Tracks session-specific changes to Counter
                    counter_key = f"counter_{expand_key}"  # Tracks total Counter for this row (final result)

                    # Initialize session state variables if not already present
                    if "expanded" not in st.session_state:
                        st.session_state["expanded"] = {}

                    if counter_0_key not in st.session_state:
                        st.session_state[counter_0_key] = 0

                    if counter_key not in st.session_state:
                        st.session_state[counter_key] = 0

                    col1, col2 = st.columns([2, 5], gap="small")

                    # Handle button click to toggle expanded state
                    with col2:
                        st.markdown(table_style, unsafe_allow_html=True) # Important!! Without this here, the col1 and col2 are not aligned and the buttons look weird
                        if st.button(f"{row['name']} auswählen", key=expand_key):
                            st.session_state["expanded"][index] = not st.session_state["expanded"].get(index, False)

                    # If the row is expanded, display the grid and handle updates
                    if st.session_state["expanded"].get(index, False):
                        df = st.session_state["df"]

                        # Ensure Counter_0 column for this row exists in the DataFrame
                        column_counter_0 = f"Counter_0_expand_{index}"
                        if column_counter_0 not in df.columns:
                            df[column_counter_0] = 0  # Initialize as 0

                        default_search_term = "Type to search products..."
                        search_key = f"grid_{row['name']}" if row['name'] else "grid_default"
                        search_term = st.text_input("Search for products:", value=row['name'], placeholder=default_search_term, key = search_key)
                        if search_term:
                            filtered_df = df[df[df.columns[0]].str.contains(search_term, case=False, na=False)]
                        else:
                            filtered_df = df
                        if not filtered_df.empty:
                            # Preserve original indices for accurate updates
                            filtered_df["original_index"] = filtered_df.index

                            # Generate a dynamic key for the grid
                            grid_key = f"grid_{search_term}_{expand_key}" if search_term else f"grid_{expand_key}"

                            # Grid Configuration
                            gd = GridOptionsBuilder.from_dataframe(filtered_df.drop(columns=["original_index"]))
                            gd.configure_pagination(enabled=False)
                            gd.configure_default_column(editable=True, groupable=False)

                            gd.configure_columns('images_0_url', cellRenderer=thumbnail_renderer, autoHeight=True)
                            gd.configure_column('Counter', headerName='Counter', cellRenderer=counter_renderer, editable=True, width=190)
                            gridoptions = gd.build()

                            # Render the AgGrid component with dynamic key
                            grid_table = AgGrid(
                                filtered_df,
                                gridOptions=gridoptions,
                                update_mode=GridUpdateMode.VALUE_CHANGED,
                                reload_data=False,
                                enable_enterprise_modules=True,
                                fit_columns_on_grid_load=True,
                                allow_unsafe_jscode=True,
                                theme='material',
                                #key="grid_table",
                                key=grid_key  # Dynamic key based on search term. It has to be dynamic, otherwise the search button does not work
                            )
                            # Capture updates without triggering reload
                            if grid_table['data'] is not None:
                                st.session_state["updated_data"] = pd.DataFrame(grid_table["data"])

                            # Process updates to Counter and Counter_0
                            if st.session_state["updated_data"] is not None:
                                updated_df = st.session_state["updated_data"]

                                for _, updated_row in updated_df.iterrows():
                                    original_idx = updated_row["original_index"]

                                    # Track changes made to the Counter column
                                    previous_counter = st.session_state["df"].loc[original_idx, "Counter"]
                                    new_counter = updated_row["Counter"]

                                    # Calculate the session-specific change
                                    delta = new_counter - previous_counter

                                    # Update the original DataFrame
                                    st.session_state["df"].loc[original_idx, "Counter"] = new_counter

                                    # Update Counter_0 for this specific grid
                                    st.session_state["df"].loc[original_idx, column_counter_0] += delta

                                    # Update total Counter for this specific grid
                                    st.session_state[counter_0_key] = st.session_state["df"].loc[original_idx, column_counter_0]
                                    st.session_state[counter_key] = (
                                        st.session_state[counter_0_key] + st.session_state["df"].loc[original_idx, "Counter"]
                                    )
                                if column_counter_0 in st.session_state["df"].columns:
                                    # Sum all values in the column_counter_0 column
                                    total_column_counter_0 = st.session_state["df"][column_counter_0].sum()
                                    st.write(f"Total of {column_counter_0}: {total_column_counter_0}")
                                else:
                                    st.write(f"Column '{column_counter_0}' does not exist in the DataFrame.")
                                st.session_state[counter_key] = total_column_counter_0
                                print(f"Updated {counter_key}: {st.session_state[counter_key]}")
                        else:
                            st.write("No additional details available.")
                        
                    # Dynamically generate button HTML based on current counter state
                    # Check if the counter equals the total
                    response_df_row = response_df.iloc[[index]]
                    button_class = "green-button" if st.session_state[counter_key] >= response_df_row['total'].item() else ""
                    button_html = f"""
                    <div class="stButton">
                        <button class="{button_class}">
                            <span class="counter">{st.session_state[counter_key]}  /</span> <!-- Add separator -->
                            <span class="total">{response_df_row['total'].item()}</span>  <!-- Display Total -->
                            <img src="{icons_url[index]}" alt="Coffee Bean">  <!-- Display Icon -->
                        </button>
                    </div>
                    """
                    # st.markdown(button_html) has to be called after col2, because otherwise it wouldn't update correctly when changing the counter above
                    with col1: 
                        # Display the button styles
                        st.markdown(button_style, unsafe_allow_html=True)
                        st.markdown(button_html, unsafe_allow_html=True)
                        st.markdown(table_style, unsafe_allow_html=True)
                        #st.markdown(html_table, unsafe_allow_html=True)