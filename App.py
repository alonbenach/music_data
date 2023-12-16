# %%
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import timedelta
from collections import defaultdict
import re


# %%
# Load the data
excel_file_name = "songs_df.xlsx"
# Read the Excel file into a dictionary of dataframes
songs_df = pd.read_excel(excel_file_name)
#######################################################################################


# Function to extract artists considering different separators
# Function to extract multiple artists from a single string
def extract_artists(artist_string):
    # Define a regex pattern to capture various separators
    pattern = r",|&| and | with | featuring | x | X "

    # Split the artist string based on the pattern
    artists = re.split(pattern, artist_string, flags=re.IGNORECASE)

    return artists


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

    date_list = songs_df.columns[2:]
    selected_date = select_date_from_list(date_list)
    selected_data = songs_df[["Artist", "Song", selected_date.strftime("%Y-%m-%d")]]

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
    ###########################################################################
    # Add an HTML anchor to link to this section
    st.markdown("<a name='onesong'></a>", unsafe_allow_html=True)

    # Placeholder for Lineplot for Songs by Artist
    st.write("### Present the Ranking of a Song over Time")

    # Allow the user to select a song from the dropdown menu
    selected_song = st.selectbox("Select a song:", songs_df["Song"].unique())

    # Filter data for the selected song
    selected_song_data = songs_df[songs_df["Song"] == selected_song]

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

    # Create a line plot using Plotly Express
    fig = px.line(
        plot_data,
        x="Date",
        y="Rank",
        title=f'Popularity of {selected_song} by {selected_song_data["Artist"].iloc[0]}',
        labels={"Date": "Date", "Rank": "Rank"},
    )

    # Customize x-axis tick labels to show years and months
    fig.update_xaxes(
        tickvals=plot_data["Date"],
        tickformat="%Y-%m",
        tickangle=45,
        title_text="Date",
    )

    # Display the chart using st.plotly_chart
    st.plotly_chart(fig)

    # %%
    # Add an HTML anchor to link to this section
    st.markdown("<a name='multisong'></a>", unsafe_allow_html=True)

    # Placeholder for Lineplot for Songs by Artist
    st.write("### Compare the Rankings of a Multiple Songs over Time")

    default_songs = songs_df["Song"].unique()[
        :3
    ]  # Get the first three songs as default placeholders

    # Allow the user to select multiple songs from the dropdown menu
    selected_songs = st.multiselect(
        "Select songs:", songs_df["Song"].unique(), default=default_songs
    )

    if len(selected_songs) > 0:
        # Filter data for the selected songs
        selected_songs_data = songs_df[songs_df["Song"].isin(selected_songs)]

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

            # Fill NA values in 'Rank' column with 0
            plot_data["Rank"].fillna(0, inplace=True)

            # Get indices of non-zero values in 'Rank' column
            nonzero_indexes = plot_data[plot_data["Rank"] != 0].index

            # Trim the DataFrame to include data between first and last non-zero appearances
            if len(nonzero_indexes) > 0:
                start_index = nonzero_indexes[0]
                end_index = nonzero_indexes[-1]
                plot_data = plot_data.loc[start_index:end_index]

            # Append plot data for the current song to combined plot data
            combined_plot_data = combined_plot_data.append(plot_data, ignore_index=True)

        # Create a line plot using Plotly Express for multiple songs comparison
        fig = px.line(
            combined_plot_data,
            x="Date",
            y="Rank",
            color="Song",
            title="Comparison of Song Popularity",
            labels={"Date": "Date", "Rank": "Rank"},
        )

        # Customize x-axis tick labels to show every second month
        month_ticks = pd.date_range(
            start=combined_plot_data["Date"].min(),
            end=combined_plot_data["Date"].max(),
            freq="2M",
        )
        fig.update_xaxes(
            tickvals=month_ticks,
            tickformat="%Y-%m",
            tickangle=45,
            title_text="Date",
        )

        # Display the chart using st.plotly_chart
        st.plotly_chart(fig)
    else:
        st.write("Please select one or more songs.")

    # %%
    # Add an HTML anchor to link to this section
    st.markdown("<a name='topartists'></a>", unsafe_allow_html=True)

    # Placeholder for Lineplot for Songs by Artist
    st.write("### See the Number of Appearances for Top Artists (1990-2022)")

    # Initialize a defaultdict to count artist appearances
    artist_appearances = defaultdict(int)

    # Iterate through each song to count artist appearances
    for song, artist in zip(songs_df["Song"], songs_df["Artist"]):
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

    # # can't get this part to work. leaving it here for future attempts outside the scope of this course
    # # Add an HTML anchor to link to this section
    # st.markdown("<a name='top10'></a>", unsafe_allow_html=True)

    # # Placeholder for Lineplot for Songs by Artist
    # st.write("### Compare Top 10 Most Played Artists by Month")

    # ### Create a heatmap to visualize the rankings of artists over time
    # # Get the list of unique months from the columns of songs_df
    # date_columns = songs_df.columns[2:]  # Assuming date columns start from index 2
    # unique_months = pd.to_datetime(date_columns).to_period("M").unique()

    # # Allow the user to select a month from the dropdown menu
    # selected_month = st.selectbox("Select a month:", unique_months)

    # # Filter data for the selected month
    # selected_month_data = songs_df[
    #     date_columns[pd.to_datetime(date_columns).to_period("M") == selected_month]
    # ]

    # # Get the top 10 ranked songs in the selected month
    # top_10_songs = selected_month_data.mean().sort_values().index[:10]

    # # Filter data for the top 10 ranked songs
    # selected_month_top_10 = selected_month_data[top_10_songs]

    # # Transpose the DataFrame for proper orientation
    # selected_month_top_10 = selected_month_top_10.T

    # # Create a heatmap using Plotly Express
    # fig = px.imshow(
    #     selected_month_top_10,
    #     labels={"color": "Rank"},
    #     x=selected_month_top_10.index,
    #     y=selected_month_top_10.columns,
    #     title=f"Top 10 Songs in {selected_month}",
    #     color_continuous_scale="Viridis",
    # )

    # # Make each vertical line wider
    # fig.update_traces(dx=0.5)

    # st.plotly_chart(fig)

    # %%
    # Add an HTML anchor to link to this section
    st.markdown("<a name='allsongs'></a>", unsafe_allow_html=True)

    # Placeholder for Lineplot for Songs by Artist
    st.write("### Present Rankings of all Songs by an Artist Throughout the Year")

    ### Create a lineplot for all songs by artist
    # Expand the DataFrame to include rows for each artist
    expanded_artists = songs_df.assign(
        Artist=songs_df["Artist"].apply(extract_artists)
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

    # Set x-axis range to the first and last non-NA dates
    fig.update_xaxes(range=[first_date, last_date])

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
    - [Top Artists by # of Entries](#topartists)
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
