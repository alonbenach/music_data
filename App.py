# %%
import pandas as pd
import altair as alt
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta
from collections import defaultdict
import re
import numpy as np

# %%
# Load the data
excel_file_name = "songs_df.xlsx"
# Read the Excel file into a dictionary of dataframes
songs_df = pd.read_excel(excel_file_name)
excel_file_name = "genre_df.xlsx"
# Read the Excel file into a dictionary of dataframes
genre_df = pd.read_excel(excel_file_name)

#######################################################################################


# Function to extract multiple artists from a single string
def extract_artists(artist_string):
    # Define a regex pattern to capture various separators
    pattern = r",|&| and | with | featuring | x | X "

    # Split the artist string based on the pattern
    artists = re.split(pattern, artist_string, flags=re.IGNORECASE)

    return artists


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
        )  # Calculate days to subtract to get to the previous Sunday
        selected_date -= timedelta(
            days=days_to_subtract
        )  # Subtract days to get to the previous Sunday
    return selected_date


# Function to limit selectable dates based on date_list and adjust if needed
def select_date_from_list(date_list):
    min_date = pd.to_datetime(min(date_list))
    max_date = pd.to_datetime(max(date_list))

    selected_date = st.date_input(
        "Select a date to present",
        min_value=min_date,
        max_value=max_date,
        value=min_date,
    )
    selected_date = adjust_to_previous_sunday(selected_date)

    return selected_date


def select_date_range(date_list):
    min_date = pd.to_datetime(min(date_list))
    max_date = pd.to_datetime(max(date_list))

    # Display a caption for the date selection
    st.caption("Select start and end dates")

    start_date = st.date_input(
        f"Select start date:",
        min_value=min_date,
        max_value=max_date,
        value=min_date,  # Change the default value to the minimum date
    )
    start_date = adjust_to_previous_sunday(start_date)

    end_date = st.date_input(
        f"Select end date:",
        min_value=min_date,
        max_value=max_date,
        value=max_date,  # Change the default value to the maximum date
    )
    end_date = adjust_to_previous_sunday(end_date)

    return start_date, end_date


def display_longest_ranking_songs(
    filtered_songs_df, selected_start_date, selected_end_date
):
    # Extract the columns corresponding to the selected dates
    selected_columns = filtered_songs_df.loc[
        :, str(selected_start_date) : str(selected_end_date)
    ]

    # Create a list of columns including song and artist columns
    columns_to_display = ["Song", "Artist"] + list(selected_columns.columns)

    # Display the table with the specified columns
    # st.write(
    #     f"""Longest Ranking Songs Between {selected_start_date.strftime("%Y-%m-%d")} - {selected_end_date.strftime("%Y-%m-%d")}) :"""
    # )
    # st.write(songs_df[columns_to_display])

    # Aggregate non-NA values and count
    non_na_counts = filtered_songs_df[columns_to_display].T.count()

    # Select top 10 songs with the most non-NA values
    top_10_songs = non_na_counts.sort_values(ascending=False).head(10)

    # Extract song and artist names for the top 10 songs
    top_10_song_artist = filtered_songs_df.loc[top_10_songs.index, ["Song", "Artist"]]

    # Combine Song and Artist columns
    top_10_song_artist["Combined"] = (
        top_10_song_artist["Song"] + ", " + top_10_song_artist["Artist"]
    )

    # Create a DataFrame with top 10 songs and their counts
    top_10_counts = pd.DataFrame(
        {"Song": top_10_song_artist["Combined"], "Count": top_10_songs}
    )

    # Create a bar chart using Altair
    chart = (
        alt.Chart(top_10_counts)
        .mark_bar()
        .encode(x="Count", y=alt.Y("Song", sort="-x"), tooltip=["Song", "Count"])
        .properties(title=f"Top 10 Songs with Most Appearances")
        .configure_axis(labelFontSize=12)
    )

    # Show the chart using Streamlit's Altair component
    st.altair_chart(chart, use_container_width=True)


def filter_songs_by_genre(selected_genres, genre_df, songs_df):
    if not selected_genres:
        # If no genres are selected, return the original songs_df
        return songs_df
    # Filter genre_df based on selected_genres
    filtered_genre_df = genre_df[["Artist"] + selected_genres]

    # Get the list of artists associated with the selected genres
    filtered_artists = filtered_genre_df[
        filtered_genre_df[selected_genres].sum(axis=1) > 0
    ]["Artist"].tolist()

    # Subset songs_df based on the filtered artists
    filtered_songs_df = songs_df[songs_df["Artist"].isin(filtered_artists)]

    return filtered_songs_df


# %%
def main():
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
            <h1 class="header-text">Billboard 100 Analysis - 1990-2022</h1>
        </div>
        <div style="display: flex; align-items: center;">
            <p class="paragraph-text">Experience the Billboard 100 data journey. 
            Dive into weekly charts, discover top songs, and track the rise and fall of artists 
            throughout the years with real data from www.billboard.com.</p>
        </div>

    """

    # Display the header
    st.markdown(header_html, unsafe_allow_html=True)

    #######################################################################################
    # Add an HTML anchor to link to this section
    st.markdown("<a name='genre_filter'></a>", unsafe_allow_html=True)

    # Placeholder for Lineplot for Songs by Artist
    st.write("### Filter the Entire Dashboard by Selected Genres")

    # Add a multiple-choice selector for genres
    selected_genres = st.multiselect("Select genres:", genre_df.columns[2:].tolist())

    # Filter songs_df based on selected genres
    filtered_songs_df = filter_songs_by_genre(selected_genres, genre_df, songs_df)
    #######################################################################################

    # Add an HTML anchor to link to this section
    st.markdown("<a name='charts'></a>", unsafe_allow_html=True)

    # Placeholder for Lineplot for Songs by Artist
    st.write("### Present the Weekly Chart by a Selected Date")

    date_list = filtered_songs_df.columns[2:]
    selected_date = select_date_from_list(date_list)
    selected_data = filtered_songs_df[
        ["Artist", "Song", selected_date.strftime("%Y-%m-%d")]
    ]

    # Filter the data based on the selected date
    selected_data = selected_data.dropna(subset=[selected_date.strftime("%Y-%m-%d")])

    # Set the selected date column as the index and arrange it in ascending order
    selected_data.set_index(selected_date.strftime("%Y-%m-%d"), inplace=True)
    selected_data.sort_index(inplace=True)

    # Display the table without the index
    st.write(
        f"""Top 100 list for the selected week (week beginning on Sunday {selected_date.strftime("%Y-%m-%d")}) :"""
    )
    st.write(selected_data)
    ############################### PRESENT 1 SONG'S RANKINGS ########################################
    # Add an HTML anchor to link to this section
    st.markdown("<a name='onesong'></a>", unsafe_allow_html=True)

    # Placeholder for Lineplot for Songs by Artist
    st.write("### Present the Ranking of a Song over Time")

    # Allow the user to select a song from the dropdown menu
    selected_song = st.selectbox("Select a song:", filtered_songs_df["Song"].unique())

    # Filter data for the selected song
    selected_song_data = filtered_songs_df[filtered_songs_df["Song"] == selected_song]

    # Get the date columns and the corresponding ranks for the selected song
    date_columns = selected_song_data.columns[
        2:
    ]  # Assuming dates start from the third column onwards
    selected_song_ranks = selected_song_data.iloc[
        0, 2:
    ]  # Selecting the row corresponding to the selected song's ranks

    # Create a DataFrame with date and rank columns for the plot
    plot_data = pd.DataFrame({"Date": date_columns, "Rank": selected_song_ranks})

    # Convert 'Date' column to datetime format
    plot_data["Date"] = pd.to_datetime(plot_data["Date"])

    # Fill NA values in 'Rank' column with 0
    plot_data["Rank"].fillna(0, inplace=True)

    # Get indices of non-zero values in 'Rank' column
    nonzero_indexes = plot_data[plot_data["Rank"] != 0].index

    # Trim the DataFrame to include data between first and last non-zero appearances
    if len(nonzero_indexes) > 0:
        start_index = nonzero_indexes[0]
        end_index = nonzero_indexes[-1]
        plot_data = plot_data.loc[start_index:end_index]

    # Replace NA values in 'Rank' column with NaN
    plot_data["Rank"] = plot_data["Rank"].replace(0, np.nan)

    # Create a line plot using Plotly Express without connecting NA values
    fig = px.line(
        plot_data,
        x="Date",
        y="Rank",
        title=f'Popularity of {selected_song} by {selected_song_data["Artist"].iloc[0]}',
        labels={"Date": "Date", "Rank": "Rank"},
    )

    # Set y-axis to be reversed
    fig.update_yaxes(autorange="reversed", scaleanchor="x", scaleratio=1)

    # Filter the data to get only existing (non-NA) ranks for x-axis ticks
    existing_ranks = plot_data.dropna(subset=["Rank"])
    existing_dates = existing_ranks["Date"]

    # Customize x-axis tick labels to show years and months for existing dates only
    fig.update_xaxes(
        tickvals=existing_dates,
        tickformat="%Y-%m-%d",
        tickangle=45,
        title_text="Date",
    )
    # Manually set y-axis tick labels to replace 0 with 1
    fig.update_yaxes(
        tickvals=[1, 20, 40, 60, 80, 100],  # Adjust tick values as needed
        ticktext=[1, 20, 40, 60, 80, 100],  # Replace 0 with 1 in tick labels
    )

    # Display the chart using st.plotly_chart
    st.plotly_chart(fig)

    ############################### COMPARE SONGS RANKINGS ##################################
    # Add an HTML anchor to link to this section
    st.markdown("<a name='multisong'></a>", unsafe_allow_html=True)

    # Placeholder for Lineplot for Songs by Artist
    st.write("### Compare the Rankings of Multiple Songs over Time")

    default_songs = filtered_songs_df["Song"].unique()[
        :3
    ]  # Get the first three songs as default placeholders

    # Allow the user to select multiple songs from the dropdown menu
    selected_songs = st.multiselect(
        "Select songs:", filtered_songs_df["Song"].unique(), default=default_songs
    )

    if len(selected_songs) > 0:
        # Filter data for the selected songs
        selected_songs_data = filtered_songs_df[songs_df["Song"].isin(selected_songs)]

        # Initialize variables to track the first and last existing observations
        min_date = pd.Timestamp.max
        max_date = pd.Timestamp.min

        # Create an empty DataFrame to store combined plot data
        combined_plot_data = pd.DataFrame(columns=["Date", "Rank", "Song"])

        # Iterate through selected songs to collect their data
        for song in selected_songs:
            # Filter data for the current selected song
            current_song_data = selected_songs_data[selected_songs_data["Song"] == song]

            # Get the date columns and the corresponding ranks for the selected song
            date_columns = current_song_data.columns[
                2:
            ]  # Assuming dates start from the third column onwards
            current_song_ranks = current_song_data.iloc[
                0, 2:
            ]  # Selecting the row corresponding to the selected song's ranks

            # Create a DataFrame with date and rank columns for the plot
            plot_data = pd.DataFrame(
                {
                    "Date": date_columns,
                    "Rank": current_song_ranks,
                    "Song": f"{song}, {current_song_data['Artist'].iloc[0]}",
                }
            )

            # Convert 'Date' column to datetime format
            plot_data["Date"] = pd.to_datetime(plot_data["Date"])

            # Fill NA values in 'Rank' column with NaN
            plot_data["Rank"] = pd.to_numeric(plot_data["Rank"], errors="coerce")

            # Append plot data for the current song to combined plot data
            combined_plot_data = combined_plot_data.append(plot_data, ignore_index=True)

            # Update min_date and max_date based on existing observations for the current song
            song_min_date = plot_data.dropna(subset=["Rank"])["Date"].min()
            song_max_date = plot_data.dropna(subset=["Rank"])["Date"].max()
            if song_min_date < min_date:
                min_date = song_min_date
            if song_max_date > max_date:
                max_date = song_max_date

        # Create a line plot using Plotly Express for multiple songs comparison
        fig = px.line(
            combined_plot_data,
            x="Date",
            y="Rank",
            color="Song",
            title="Comparison of Song Popularity",
            labels={"Date": "Date", "Rank": "Rank"},
        )

        # Set y-axis to be reversed
        fig.update_yaxes(autorange="reversed")

        # Customize x-axis tick labels to show every second month
        month_ticks = pd.date_range(start=min_date, end=max_date, freq="2M")
        fig.update_xaxes(
            tickvals=month_ticks, tickformat="%Y-%m-%d", tickangle=45, title_text="Date"
        )

        # Set the x-axis range based on the first and last existing observation dates within selected songs
        fig.update_xaxes(range=[min_date, max_date])
        # Manually set y-axis tick labels to replace 0 with 1
        fig.update_yaxes(
            tickvals=[1, 20, 40, 60, 80, 100],  # Adjust tick values as needed
            ticktext=[1, 20, 40, 60, 80, 100],  # Replace 0 with 1 in tick labels
        )
        # Display the chart using st.plotly_chart
        st.plotly_chart(fig)
    else:
        st.write("Please select one or more songs.")

    ############################# Number of Appearances for Top Artists #############################
    # Add an HTML anchor to link to this section
    st.markdown("<a name='topartists'></a>", unsafe_allow_html=True)

    # Placeholder for Lineplot for Songs by Artist
    st.write("### See the Number of Appearances for Top Artists (1990-2022)")

    # Initialize a defaultdict to count artist appearances
    artist_appearances = defaultdict(int)

    # Iterate through each song to count artist appearances
    for song, artist in zip(filtered_songs_df["Song"], filtered_songs_df["Artist"]):
        # Extract individual artists from the song based on separators
        artists = extract_artists(artist)

        # Increment the appearance count for each artist
        for artist_name in artists:
            artist_appearances[artist_name.strip()] += 1

    # Convert the defaultdict to a DataFrame and get the top 100 artists
    top_artists = pd.DataFrame(
        artist_appearances.items(), columns=["Artist", "Number of Appearances"]
    )
    top_artists = top_artists.nlargest(100, "Number of Appearances")

    # Create a bar plot for top 100 artists
    fig = px.bar(
        top_artists,
        x="Number of Appearances",
        y="Artist",
        orientation="h",
        title="Top 100 Artists in Billboard100 by Number of Appearances",
        labels={"Number of Appearances": "Number of Appearances"},
    )

    # Display the chart using st.plotly_chart
    st.plotly_chart(fig)

    ################################# ALL SONGS BY AN ARTIST #################################
    # Add an HTML anchor to link to this section
    st.markdown("<a name='allsongs'></a>", unsafe_allow_html=True)

    # Placeholder for Lineplot for Songs by Artist
    st.write("### Present Rankings of all Songs by an Artist Throughout the Year")

    ### Create a lineplot for all songs by artist
    # Expand the DataFrame to include rows for each artist
    expanded_artists = filtered_songs_df.assign(
        Artist=filtered_songs_df["Artist"].apply(extract_artists)
    ).explode("Artist")

    # Get the list of unique artists from the expanded DataFrame
    unique_artists = expanded_artists["Artist"].unique()

    # Allow the user to select an artist from the dropdown menu
    selected_artist = st.selectbox("Select an artist:", unique_artists)

    # Filter data for the selected artist
    selected_artist_data = expanded_artists[
        expanded_artists["Artist"] == selected_artist
    ]

    # Melt the DataFrame to reshape the data for plotting
    melted_data = pd.melt(
        selected_artist_data,
        id_vars=["Artist", "Song"],
        var_name="Date",
        value_name="Rank",
    )

    # Sort the melted data by date
    melted_data["Date"] = pd.to_datetime(melted_data["Date"])
    melted_data = melted_data.sort_values("Date")

    # Filter the data to keep only rows where 'Rank' is not NA
    filtered_data = melted_data.dropna(subset=["Rank"])

    # Get the first and last non-NA dates for the selected artist
    first_date = filtered_data["Date"].min()
    last_date = filtered_data["Date"].max()

    # Create a line plot using Plotly Express
    fig = px.line(
        filtered_data,
        x="Date",
        y="Rank",
        color="Song",
        title=f"Ranking Over Time for Songs by {selected_artist}",
        labels={"Date": "Date", "Rank": "Rank", "Song": "Song"},
    )

    # Set y-axis to be reversed
    fig.update_yaxes(autorange="reversed")

    # Set x-axis range to the first and last non-NA dates
    fig.update_xaxes(range=[first_date, last_date])

    # Manually set y-axis tick labels to replace 0 with 1
    fig.update_yaxes(
        tickvals=[1, 20, 40, 60, 80, 100],  # Adjust tick values as needed
        ticktext=[1, 20, 40, 60, 80, 100],  # Replace 0 with 1 in tick labels
    )
    # Display the chart using st.plotly_chart
    st.plotly_chart(fig)
    ############################## LONGEST RANKING SONG  ####################################################
    # Add an HTML anchor to link to this section
    st.markdown("<a name='songbyappearance'></a>", unsafe_allow_html=True)

    # Placeholder for Lineplot for Songs by Artist
    st.write("### Present The Longest-Ranking Songs")

    date_list = filtered_songs_df.columns[2:]

    # Use select_date_range function with unique keys
    selected_start_date, selected_end_date = select_date_range(date_list)

    # Display the table
    display_longest_ranking_songs(
        filtered_songs_df, selected_start_date, selected_end_date
    )

    ###################################SIDEBAR FEATURES###########################################
    # Display an image at the top of the sidebar
    st.sidebar.image("Kozminski.png", width=100)

    # Add anchor links to the different plots in your app
    st.sidebar.markdown(
        """
    ### Navigation
    - [Top](#header)
    - [Genre Selector](#genre_filter)
    - [Charts](#charts)
    - [One Song Rankings](#onesong)
    - [Compare Song Rankings](#multisong)
    - [Top Artists by # of Entries](#topartists)
    - [All Songs by Artist](#allsongs)
    - [Longest Ranking Song](#songbyappearance)
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

    # Add project description at the bottom of the sidebar with adjusted style
    st.sidebar.markdown(
        """
    ---

    <span style="font-size:smaller; opacity:0.75">
    Created by Filip Sobota, Joanna Bańkowska, and Alon Benach
    under the supervision of Jacek Mańko, Web Mining course, Kozmiński University 2023.
    </span>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
