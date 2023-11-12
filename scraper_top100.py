# %%
import billboard
from datetime import date
import pandas as pd

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
# %%
