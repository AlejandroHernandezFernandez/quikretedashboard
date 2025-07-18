import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import datetime

# --- Light/Dark Mode --
LIGHT_MODE_CSS = """
<style>
    /* Main background and default text colors for the entire app */
    body {
        background-color: white !important;
        color: black !important;
    }
    .stApp { /* This targets the main Streamlit app container */
        background-color: white !important;
        color: black !important;
    }
    /* Specific text elements (headers, paragraphs, markdown) */
    h1, h2, h3, h4, h5, h6, p, .stMarkdown, .stText {
        color: black !important;
    }
    /* Adjust horizontal rules for better visibility in light mode */
    hr {
        border-top: 1px solid #bbb !important; /* Lighter grey for separator */
    }
    /* Potentially adjust inputs/buttons if they don't look right */
    div.stButton > button {
        color: black !important;
        border: 1px solid #ccc !important;
        background-color: #f0f2f6 !important;
    }
    div.stButton > button:hover {
        background-color: #e0e2e6 !important;
    }
</style>
"""

DARK_MODE_CSS = """
<style>
    /* Main background and default text colors for the entire app */
    body {
        background-color: #0E1117 !important; /* Streamlit's default dark background */
        color: #FAFAFA !important; /* Streamlit's default dark text */
    }
    .stApp {
        background-color: #0E1117 !important;
        color: #FAFAFA !important;
    }
    /* Specific text elements (headers, paragraphs, markdown) */
    h1, h2, h3, h4, h5, h6, p, .stMarkdown, .stText {
        color: #FAFAFA !important;
    }
    /* Adjust horizontal rules for better visibility in dark mode */
    hr {
        border-top: 1px solid #333 !important; /* Darker grey for separator */
    }
    div.stButton > button {
        color: #FAFAFA !important;
        border: 1px solid #333 !important;
        background-color: #262730 !important;
    }
     div.stButton > button:hover {
        background-color: #383a45 !important;
    }
</style>
"""

# --- API ---
API_URL = "https://api.thingspeak.com/channels/3002831/feeds.json?api_key=C2GJTGX8RHAHCTIU&results=40"


# COLOR INDICATORS FOR CHANNELS
CHANNEL_COLOR_RANGES = {
    "field1": [ # Crusher
        {"range": (None, 700), "color": "#FF3333"},  # RED: Crusher rate < 700 t/h
        {"range": (700, 1000), "color": "#F6FF33"}, # YELLOW: 700 < rate < 1000
        {"range": (1000, None), "color": "#33FF57"}  # GREEN: > 1000
    ],
    "field2": [ # Raw Mill
        {"range": (None, 300), "color": "#FF3333"},
        {"range": (300, 350), "color": "#F6FF33"},
        {"range": (350, None), "color": "#33FF57"}
    ],
    "field3": [ # Kiln
        {"range": (None, 280), "color": "#FF3333"},
        {"range": (280, 335), "color": "#F6FF33"},
        {"range": (335, None), "color": "#33FF57"}
    ],
    "field4": [ # FM#1
        {"range": (None, 100), "color": "#FF3333"},
        {"range": (100, 120), "color": "#F6FF33"},
        {"range": (120, None), "color": "#33FF57"}
    ],
    "field5": [ # FM#2
        {"range": (None, 100), "color": "#FF3333"},
        {"range": (100, 120), "color": "#F6FF33"},
        {"range": (120, None), "color": "#33FF57"}
    ],
    "field6": [ # Coal Mill
        {"range": (None, 30.3), "color": "#FF3333"},
        {"range": (30.3, 32.7), "color": "#F6FF33"},
        {"range": (32.7, None), "color": "#33FF57"}
    ],
    "field7": [ # Blend Silo Level
        {"range": (None, 5), "color": "#FF3333"},
        {"range": (5, 95), "color": "#33FF57"},
        {"range": (95, None), "color": "#FF3333"}
    ]
}

# --- Function to Get Color Based on Value and Channel ---
def get_color_for_value(channel_key, value):
    if value is None:
        return "#808080"  # Grey for no data
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "#808080" # Grey if value cannot be converted

    ranges = CHANNEL_COLOR_RANGES.get(channel_key, [])
    for r in ranges:
        min_val, max_val = r["range"]
        
        if (min_val is None or value >= min_val) and \
           (max_val is None or value < max_val):
            return r["color"]
            
    return "#ADD8E6"  # Light blue as a default if no range matches

@st.cache_data(ttl=900) # Cache data for 120 seconds
def get_latest_feed_from_thingspeak():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        
        if data and 'feeds' in data and data['feeds']:
            all_feeds = data['feeds']
            
            current_api_values = {}
            current_api_timestamp = all_feeds[-1]['created_at'] if all_feeds else None 
            
            for feed in all_feeds: 
                if feed['created_at'] and (current_api_timestamp is None or feed['created_at'] > current_api_timestamp):
                    current_api_timestamp = feed['created_at']

                for i in range(1, 8):
                    field_key = f"field{i}"
                    if field_key in feed and feed[field_key] is not None:
                        current_api_values[field_key] = feed[field_key]
            
            current_api_values['created_at'] = current_api_timestamp

            if not current_api_values:
                return None
                
            return current_api_values
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API: {e}")
        return None
    except KeyError:
        st.error("Unexpected JSON format from API.")
        return None

# --- Streamlit App Layout ---

st.set_page_config(layout="wide")

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark' 

if st.session_state.theme == 'light':
    st.markdown(LIGHT_MODE_CSS, unsafe_allow_html=True)
else:
    st.markdown(DARK_MODE_CSS, unsafe_allow_html=True)

# Create a two-column layout for the top bar
col_title, col_logo = st.columns([5, 1])

with col_title:
    st.title("Dashboard")

with col_logo:
    # Use the full file path as you provided
    QUIKRETE_LOGO_PATH = 'Quikrete Cement.png'
    st.image(QUIKRETE_LOGO_PATH, width=300) # Increased width for better visibility

st_autorefresh(interval=15 * 1000, key="data_refresher") 

# Toggle Theme Button (simple version)
if st.button("Toggle Light/Dark Mode"):
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
    st.rerun() 

# --- Initialize session state for last good values if not already present ---
if 'last_good_channel_values' not in st.session_state:
    st.session_state.last_good_channel_values = {
        'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    }
    for i in range(1, 8):
        st.session_state.last_good_channel_values[f"field{i}"] = "---" 

# --- Get the latest data from ThingSpeak ---
new_api_data = get_latest_feed_from_thingspeak()

# --- Update last good values in session state ---
if new_api_data:
    if 'created_at' in new_api_data and new_api_data['created_at'] is not None:
        st.session_state.last_good_channel_values['created_at'] = new_api_data['created_at']
    
    for i in range(1, 8):
        field_key = f"field{i}"
        if new_api_data.get(field_key) is not None:
            st.session_state.last_good_channel_values[field_key] = new_api_data[field_key]

if st.session_state.last_good_channel_values:
    st.markdown(f"### **Last Updated:** {pd.to_datetime(st.session_state.last_good_channel_values.get('created_at', 'N/A')).strftime('%Y-%m-%d %H:%M:%S')}")
    
    channel_names = [
        "Crushing", "Raw Mill", "Kiln", "Finish Mill 1",
        "Finish Mill 2", "Coal Mill", "Blend Silo Level"
    ]
    
    for i in range(7):
        field_key = f"field{i+1}"
        
        display_value = st.session_state.last_good_channel_values.get(field_key, "N/A") 

        square_color = get_color_for_value(field_key, st.session_state.last_good_channel_values.get(field_key))
        
       #Rounding for values and format for type of value
        if field_key == "field7" and display_value != "N/A" and display_value is not None:
            try:
                display_value = f"{float(display_value):.1f}" + "%"
            except ValueError:
                display_value = "Error"
        elif display_value != "N/A" and display_value is not None:
             display_value = f"{float(display_value):.1f}" + "TPH"
        
        
        col_name, col_value_middle, col_square = st.columns([3, 2, 0.6]) 
        
        with col_name:
            st.markdown(f"# **{channel_names[i]}**") 

        with col_value_middle:
                st.markdown(f"<h1 style='text-align: center;'>{display_value}</h1>", unsafe_allow_html=True)

        with col_square:
            square_html = f"""
            <div style="
                width: 80px;    
                height: 80px;   
                background-color: {square_color};
                border-radius: 5px;
                margin-top: 5px;"> 
            </div>
            """
            st.markdown(square_html, unsafe_allow_html=True)
        
        st.write("---") 
            
else:
    st.warning("Could not retrieve any data. Please check the API key and channel ID.")