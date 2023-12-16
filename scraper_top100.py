# %%
import billboard
from datetime import date
import pandas as pd

start_year = 2000
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
