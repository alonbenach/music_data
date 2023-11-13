# %%
import billboard
from datetime import date
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import numpy as np

# %%
# Set the start and end date for the dictionary
start_date = date(2022, 11, 1)
end_date = date(2022, 12, 31)
daterange = pd.date_range(start_date, end_date, freq="W").strftime("%Y-%m-%d").tolist()
# %%
# Create a dictionary of dataframes by months of the year with ranking data
charts = {}
for date in daterange:
    print(date)
    chart = billboard.ChartData("hot-100", date=date)
    song_list = []
    artist_list = []
    rank_list = []
    for song in chart:
        song_list.append(song.title)
        artist_list.append(song.artist)
        rank_list.append(song.rank)
    charts[date] = {
        "song": song_list,
        "artist": artist_list,
        "rank": rank_list,
    }
for key in charts:
    charts[key] = pd.DataFrame.from_dict(charts[key])
    charts[key].set_index("rank")

# %%
# Custom HTML/CSS/JavaScript code for the impressive header
header_html = """
    <style>
        @keyframes swirl {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @keyframes flash {
            0% { color: red; }
            16.66% { color: orange; }
            33.33% { color: yellow; }
            50% { color: green; }
            66.66% { color: blue; }
            83.33% { color: indigo; }
            100% { color: violet; }
        }

        .impressive-header {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            animation: swirl 5s ease-in-out, flash 2s infinite;
        }
    </style>
    <script>
        let header = document.querySelector('.impressive-header');

        header.addEventListener("mouseover", function() {
            header.style.animation = 'swirl 5s ease-in-out';
            header.addEventListener('animationend', function() {
                header.style.animation = 'flash 2s infinite';
            }, {once: true});
        });
    </script>
    <div class="impressive-header">Here is Billboard 100 for 2022 - Have Fun Exploring the Data!</div>
"""

# Display the impressive header
st.markdown(header_html, unsafe_allow_html=True)

# %%
date_list = list(charts.keys())
selected_date = st.selectbox("Select a date:", date_list)

st.write(f"Table for {selected_date}")
st.write(charts[selected_date])

# %%
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
### Create a lineplot for all songs by artist
# Combine dataframes from all dates into one dataframe
all_data = pd.concat(
    (df.assign(date=date) for date, df in charts.items()), ignore_index=True
)

# Get the list of unique artists
unique_artists = all_data["artist"].unique()

# Allow the user to select an artist from the dropdown menu
selected_artist = st.selectbox("Select an artist:", unique_artists)

# Filter data for the selected artist
selected_artist_data = all_data[all_data["artist"] == selected_artist]

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

########
# Display a sidebar with a text input for users to enter their email
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
