# %%
import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
from datetime import datetime, timedelta

# %%
# Load the data
excel_file_name = "output_file.xlsx"
# Read the Excel file into a dictionary of dataframes
charts = pd.read_excel(excel_file_name, sheet_name=None)
#######################################################################################
# %%
### HEADER
# Add an HTML anchor to link to this section
st.markdown("<a name='header'></a>", unsafe_allow_html=True)

# Present simple header
header_html = """
    <link href="https://fonts.googleapis.com/css2?family=EB+Garamond&display=swap" rel="stylesheet">
    <style>
        .header-text {
            font-family: 'EB Garamond', serif;
            font-size: 36px;
            font-weight: bold;
        }
        .paragraph-text {
            font-family: 'EB Garamond', serif;
            font-size: 18px;
        }
    </style>
    <div style="display: flex; align-items: center;">
        <h1 class="header-text">Billboard 100 Analysis - 2022</h1>
    </div>
    <div style="display: flex; align-items: center;">
        <p class="paragraph-text">Experience the 2022 Billboard 100 journey. 
        Dive into weekly charts, discover top songs, and track the rise and fall of artists 
        throughout the year with real data from the www.billboard.com.</p>
    </div>

"""

# Display the header
st.markdown(header_html, unsafe_allow_html=True)


#######################################################################################
# %%
# Add an HTML anchor to link to this section
st.markdown("<a name='charts'></a>", unsafe_allow_html=True)

# Placeholder for Lineplot for Songs by Artist
st.write("### Present the Weekly Chart by a Selected Date")


# Function to check if the given date is a Sunday
def is_sunday(date):
    return (
        date.weekday() == 6
    )  # 6 corresponds to Sunday in Python's datetime module (0 is Monday)


# Function to adjust the selected date to the previous Sunday if necessary
def adjust_to_previous_sunday(selected_date):
    # Check if the selected date is a Sunday, if not, find the previous Sunday
    if not is_sunday(selected_date):
        days_to_subtract = (
            selected_date.weekday() + 1
        )  # Calculate the days to subtract to get to the previous Sunday
        selected_date -= timedelta(
            days=days_to_subtract
        )  # Subtract days to get to the previous Sunday
    return selected_date


# Function to limit selectable dates based on date_list and adjust if needed
def select_date_from_list(date_list):
    min_date = datetime.strptime(min(date_list), "%Y-%m-%d")
    max_date = datetime.strptime(max(date_list), "%Y-%m-%d")

    selected_date = st.date_input(
        "Select a date to present",
        min_value=min_date,
        max_value=max_date,
        value=min_date,
    )
    selected_date = adjust_to_previous_sunday(selected_date)

    return selected_date


# Assuming date_list is defined as list(charts.keys())
date_list = list(charts.keys())
selected_date = select_date_from_list(date_list)
selected_data = charts[selected_date.strftime("%Y-%m-%d")]

# Set the 'rank' column as the index
selected_data.set_index("rank", inplace=True)

st.write(
    f"""Top 100 list for the selected week (week beginning on Sunday {selected_date}) :"""
)
st.write(selected_data)
# %%

# Add an HTML anchor to link to this section
st.markdown("<a name='onesong'></a>", unsafe_allow_html=True)

# Placeholder for Lineplot for Songs by Artist
st.write("### Present the Ranking of a Song over Time")

# Create a line plot for a song's popularity through time for a selected song
# Combine dataframes from all dates into one dataframe
all_data = pd.concat(
    (df.assign(date=date) for date, df in charts.items()), ignore_index=True
)

# Get the list of unique songs
song_list = all_data["song"].unique()

# Allow the user to select a song from the dropdown menu
selected_song = st.selectbox("Select a song:", song_list)

# Filter data for the selected song
selected_song_data = all_data[all_data["song"] == selected_song]

# Create a line chart using Plotly Express
fig = px.line(
    selected_song_data,
    x="date",
    y="rank",
    title=f'Billboard100 Ranks for {selected_song} ({selected_song_data["artist"].iloc[0]})',
    labels={"date": "Date", "rank": "Rank"},
)

# Display the chart using st.plotly_chart
st.plotly_chart(fig)
# %%
# Add an HTML anchor to link to this section
st.markdown("<a name='multisong'></a>", unsafe_allow_html=True)

# Placeholder for Lineplot for Songs by Artist
st.write("### Compare the Rankings of a Multiple Songs over Time")
# Combine dataframes from all dates into one dataframe
all_data = pd.concat(
    (df.assign(date=date) for date, df in charts.items()), ignore_index=True
)

# Get the list of unique songs
unique_songs = all_data["song"].unique()

# Allow the user to select up to 4 songs from the multiselect dropdown menu
selected_songs = st.multiselect(
    "Select songs to compare:",
    unique_songs,
    default=unique_songs[:4],
    key="song_selection",
)

# Filter data for the selected songs
selected_songs_data = all_data[all_data["song"].isin(selected_songs)]

# Create a line plot using Plotly Express
fig = px.line(
    selected_songs_data,
    x="date",
    y="rank",
    color="song",
    title="Ranking Over Time for Selected Songs",
    labels={"date": "Date", "rank": "Rank", "song": "Song"},
)

# Display the chart using st.plotly_chart
st.plotly_chart(fig)

# %%
# Add an HTML anchor to link to this section
st.markdown("<a name='topartists'></a>", unsafe_allow_html=True)

# Placeholder for Lineplot for Songs by Artist
st.write("### See the Number of Appearances for Top Artists in 2022")

### Create a barplot for all songs per top performers
top_artists = all_data["artist"].value_counts().reset_index()
top_artists.columns = ["Artist", "Number of Appearances"]

fig = px.bar(
    top_artists,
    x="Number of Appearances",
    y="Artist",
    orientation="h",
    title="Top Artists in Billboard100",
    labels={"Number of Appearances": "Number of Appearances"},
)
st.plotly_chart(fig)
# %%
# Add an HTML anchor to link to this section
st.markdown("<a name='top10'></a>", unsafe_allow_html=True)

# Placeholder for Lineplot for Songs by Artist
st.write("### Compare Top 10 Most Played Artists by Month")
### Create a heatmap to visualize the rankings of artists over time
# Combine dataframes from all dates into one dataframe
all_data = pd.concat(
    (df.assign(date=date) for date, df in charts.items()), ignore_index=True
)

# Get the list of unique months
unique_months = pd.to_datetime(all_data["date"]).dt.to_period("M").unique()

# Allow the user to select a month from the dropdown menu
selected_month = st.selectbox("Select a month:", unique_months)

# Filter data for the selected month
selected_month_data = all_data[
    pd.to_datetime(all_data["date"]).dt.to_period("M") == selected_month
]

# Get the top 10 ranked artists of the selected month
top_10_artists = (
    selected_month_data.groupby("artist")["rank"].mean().sort_values().head(10).index
)

# Filter data for the top 10 ranked artists
selected_month_data_top_10 = selected_month_data[
    selected_month_data["artist"].isin(top_10_artists)
]

# Create a heatmap using Plotly Express
heatmap_data = selected_month_data_top_10.pivot_table(
    index="artist", columns="date", values="rank", aggfunc="mean"
)

fig = px.imshow(
    heatmap_data,
    labels={"color": "Rank"},
    x=heatmap_data.columns,
    y=heatmap_data.index,
    title=f"Top 10 Ranked Artists in {selected_month}",
    color_continuous_scale="Viridis",
)

# Make each vertical line wider
fig.update_traces(dx=0.5)

st.plotly_chart(fig)
# %%
# Add an HTML anchor to link to this section
st.markdown("<a name='allsongs'></a>", unsafe_allow_html=True)

# Placeholder for Lineplot for Songs by Artist
st.write("### Present Rankings of all Songs by an Artist Throughout the Year")


### Create a lineplot for all songs by artist
# Combine dataframes from all dates into one dataframe
all_data = pd.concat(
    (df.assign(date=date) for date, df in charts.items()), ignore_index=True
)

# Get the list of unique artists
unique_artists = all_data["artist"].unique()

# Allow the user to select an artist from the dropdown menu
selected_artist = st.selectbox("Select an artist:", unique_artists)


# Function to filter data for the selected artist and its variations
def filter_artist_data(artist):
    return all_data[all_data["artist"].str.contains(artist, case=False)]


# Filter data for the selected artist and variations
selected_artist_data = filter_artist_data(selected_artist)

# Create a line plot using Plotly Express
fig = px.line(
    selected_artist_data,
    x="date",
    y="rank",
    color="song",
    title=f"Ranking Over Time for Songs by {selected_artist}",
    labels={"date": "Date", "rank": "Rank", "song": "Song"},
)

# Display the chart using st.plotly_chart
st.plotly_chart(fig)

###################################SIDEBAR FEATURES###########################################
# Display an image at the top of the sidebar
st.sidebar.image("Kozminski.png", width=100)

# Add anchor links to the different plots in your app
st.sidebar.markdown(
    """
### Navigation
- [Top](#header)
- [Charts](#charts)
- [One Song Rankings](#onesong)
- [Compare Song Rankings](#multisong)
- [Top Artists by of Entries](#topartists)
- [Top 10 Artists by Month](#top10)
- [All Songs by Artist](#allsongs)
"""
)


# Display a text input for users to enter their email in the sidebar
user_email = st.sidebar.text_input(
    "Enter your email to be notified when next year's charts are available:"
)

# Store the user's email in a file or database when submitted
if st.sidebar.button("Submit"):
    if user_email:
        # Save the email to a file, database, or send it to your backend for processing
        with open("user_emails.txt", "a") as f:
            f.write(user_email + "\n")
        st.sidebar.success(
            "Thank you! We'll notify you when next year's charts are available."
        )
    else:
        st.sidebar.warning("Please enter a valid email address.")
