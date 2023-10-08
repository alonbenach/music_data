import requests
import spotipy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Prepare to make a request to Spotify server
url = "https://accounts.spotify.com/api/token"
client_id = "7c2c77f7146a408bbd8aade210c853c1"
client_secret = "0e92d709e3b4442fac06b8c58b17bbfd"

auth_response = requests.post(
    url,
    {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    },
)

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data["access_token"]

access_token

# Format a get request
headers = {"Authorization": "Bearer {token}".format(token=access_token)}
# base URL of all Spotify API endpoints
BASE_URL = "https://api.spotify.com/v1/"

sp = spotipy.Spotify(auth=headers)

artist = input("Please enter artist name: ")

artist_id = sp.search(q="artist:" + artist, type="artist")

artistID = artist_id["artists"]["items"][0]["id"]

# pull all artists albums
r = requests.get(
    BASE_URL + "artists/" + artistID + "/albums",
    headers=headers,
    params={"include_groups": "album", "limit": 50},
)
d = r.json()

data = []  # will hold all track info
albums = []  # to keep track of duplicates

# loop over albums and get all tracks
for album in d["items"]:
    album_name = album["name"]

    # here's a hacky way to skip over albums we've already grabbed
    trim_name = album_name.split("(")[0].strip()
    if trim_name.upper() in albums:  # or int(album['release_date'][:4]) > 1960:
        continue
    albums.append(trim_name.upper())  # use upper() to standardize

    # this takes a few seconds so let's keep track of progress
    print(albums)

    # pull all tracks from this album
    r = requests.get(BASE_URL + "albums/" + album["id"] + "/tracks", headers=headers)
    tracks = r.json()["items"]

    for track in tracks:
        # get audio features (key, liveness, danceability, ...)
        f = requests.get(BASE_URL + "audio-features/" + track["id"], headers=headers)
        f = f.json()

        # combine with album info
        f.update(
            {
                "track_name": track["name"],
                "album_name": album_name,
                "short_album_name": trim_name,
                "release_date": album["release_date"],
                "album_id": album["id"],
            }
        )

        data.append(f)

# Organize and clean as df
df = pd.DataFrame(data)

# convert release_date to an actual date, and sort by it
df["release_date"] = pd.to_datetime(df["release_date"])
df = df.sort_values(by="release_date")
