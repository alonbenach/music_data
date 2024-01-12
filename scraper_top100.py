# %%
import billboard
from datetime import date
import pandas as pd
import requests
from bs4 import BeautifulSoup

# %%
start_year = 1990
end_year = 2022

year_charts = {}  # Dictionary to hold data for all dates

for year in range(start_year, end_year + 1):
    daterange = (
        pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="W")
        .strftime("%Y-%m-%d")
        .tolist()[:52]
    )

    for idx, date in enumerate(daterange):
        print(f"Fetching data for {year}, week {idx + 1}")
        chart = billboard.ChartData("hot-100", date=date)
        song_list = []
        artist_list = []
        rank_list = []

        for song in chart:
            song_list.append(song.title)
            artist_list.append(song.artist)
            rank_list.append(song.rank)

        if date not in year_charts:
            year_charts[date] = {
                "song": [],
                "artist": [],
                "rank": [],
            }

        year_charts[date]["song"].extend(song_list)
        year_charts[date]["artist"].extend(artist_list)
        year_charts[date]["rank"].extend(rank_list)


# %%
# Initialize a dictionary to store song-rank mappings for each date
song_ranks = {}

# Collect song ranks for each date
for date, data in year_charts.items():
    for idx, song in enumerate(data["song"]):
        artist = data["artist"][idx]
        rank = data["rank"][idx]
        if (artist, song) not in song_ranks:
            song_ranks[(artist, song)] = {}
        song_ranks[(artist, song)][date] = rank

# Create a DataFrame from the collected song ranks
date_columns = list(year_charts.keys())
columns = ["Artist", "Song"] + date_columns
data_rows = []

for (artist, song), ranks in song_ranks.items():
    row = [artist, song]
    for date in date_columns:
        row.append(ranks.get(date, float("NaN")))
    data_rows.append(row)

songs_df = pd.DataFrame(data_rows, columns=columns)

# Display the resulting DataFrame
print(songs_df)

# %%
songs_df.to_excel("songs_df.xlsx", index=False)

# %%
# Load the data
excel_file_name = "songs_df.xlsx"
# Read the Excel file into a dictionary of dataframes
songs_df = pd.read_excel(excel_file_name)


# %%
# Function to generate Wikipedia URLs for artists
def generate_wikipedia_urls(artist):
    # Replace spaces with underscores and create Wikipedia URL
    return f"https://en.wikipedia.org/wiki/{artist.replace(' ', '_')}"


# Add a new column 'Wikipedia_Page' with Wikipedia URLs
songs_df["Wikipedia_Page"] = songs_df["Artist"].apply(generate_wikipedia_urls)

# Display the updated DataFrame
print(songs_df)


# %%
# Function to scrape artist's genre from Wikipedia
def scrape_artist_genre(url):
    try:
        response = requests.get(url, timeout=10)  # Set a timeout to prevent hanging
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            infobox = soup.find("table", {"class": "infobox"})
            if infobox:
                rows = infobox.find_all("tr")
                for row in rows:
                    if row.th and row.th.text.strip() == "Genres":
                        genres = row.td.text.strip()
                        return genres
        return None
    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        return None


# Iterate through each row and fetch genre for each artist's Wikipedia page
for index, row in songs_df.iterrows():
    url = row["Wikipedia_Page"]
    artist = row["Artist"]
    genre = scrape_artist_genre(url)
    songs_df.loc[songs_df["Artist"] == artist, "Genre"] = genre
    print(f"Artist: {artist} - Genre: {genre}")

# Display the updated DataFrame
print(songs_df["Genre"])
# %%
# Create a df of artists and genre and drop duplicates
genre_df = songs_df[["Artist", "Genre"]]
genre_df = genre_df.drop_duplicates(subset=["Artist"], keep="first")

# %%
# Compare artists with existing genre to missing
print(genre_df["Artist"].count() - genre_df["Genre"].count(), "songs have null genre.")
# %%
# Save genre_df to excel
genre_df.to_excel("genre_df.xlsx", index=False)

# %%
# Load the data
excel_file_name = "genre_df.xlsx"
# Read the Excel file into a dictionary of dataframes
genre_df = pd.read_excel(excel_file_name)

# %%
# Create a binary dataframe of genre
# List of genres
genre_list = [
    "rock",
    "pop",
    "jazz",
    "fusion",
    "soul",
    "r&b",
    "folk",
    "hip hop",
    "dance",
    "hard rock",
    "soft rock",
    "metal",
    "glam",
    "new wave",
    "swing",
    "blues",
    "funk",
    "progressive",
    "country",
    "reggae",
    "brit",
    "electronic",
    "psychedelic",
    "psychedelia",
    "new wave",
    "rap",
    "latin",
    "freestyle",
    "synth",
    "gothic",
    "alternative",
    "house",
    "christian",
    "salsa",
    "indie",
    "gospel",
    "christmas",
    "children",
    "edm",
]


# Function to check if a genre exists in the 'Genre' column
def check_genre(genre, genre_column):
    if genre_column is not None and isinstance(genre_column, str):
        return int(genre.lower() in genre_column.lower())
    return 0


# Create columns for each genre based on 'Genre' column
for genre in genre_list:
    genre_df[genre] = genre_df["Genre"].apply(lambda x: check_genre(genre, x))

# Combine and replace columns "psychedelia" and "psychefelic"
genre_df["psychedelic"] = genre_df[["psychedelia", "psychedelic"]].max(axis=1)

# Drop the "psychedelia" column
genre_df = genre_df.drop(columns=["psychedelia"], axis=1)
genre_list.remove("psychedelia")

# Display the DataFrame with genre columns as 0/1
print(genre_df[["Artist"] + genre_list])


# %%
# Save genre_df to excel after changes
genre_df.to_excel("genre_df.xlsx", index=False)
# %%
