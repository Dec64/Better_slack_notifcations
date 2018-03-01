#!/usr/bin/env python3
import os
import requests
import logging
import sys
import json

#################### CONFIG ####################

slack_user = "Notification Bot"
slack_icon = ":satellite_antenna:"
slack_channel_tv = "#tv"
slack_channel_movie = "#movies"
slack_url = ""

sonarr_url = ""
radarr_url = ""

moviedb_key = ""
omdb_key = ""

############### DO NOT EDIT BELOW ###############

# Set up the log file
log_filename = os.path.join(os.path.dirname(sys.argv[0]), 'slack_notification.log')
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
log = logging.getLogger("Slack")

# Set up env variables

skyhook_url = "http://skyhook.sonarr.tv/v1/tvdb/shows/en/"
sonarr_icon = "https://raw.githubusercontent.com/Sonarr/Sonarr/develop/Logo/256.png"
radarr_icon = "https://raw.githubusercontent.com/Radarr/Radarr/develop/Logo/256.png"

slack_headers = {'content-type': 'application/json'}

if len(sys.argv) <= 1:
    log.error("You must send argument sonarr or radarr")
    sys.exit(0)

elif sys.argv[1].lower() == "sonarr":
    overview = "None"
    season = os.environ.get('sonarr_episodefile_seasonnumber')
    episode = os.environ.get('sonarr_episodefile_episodenumbers')
    tvdb_id = os.environ.get('sonarr_series_tvdbid')
    scene_name = os.environ.get("sonarr_episodefile_scenename")
    media_title = os.environ.get("sonarr_series_title")
    episode_title = os.environ.get("sonarr_episodefile_episodetitles")
    quality = os.environ.get("sonarr_episodefile_quality")
    is_upgrade = os.environ.get("sonarr_isupgrade")

    # Get raw show information
    request = requests.get(skyhook_url + str(tvdb_id))
    data = request.json()
    title_slug = data['slug']

    # Get images for show
    try:
        poster = data['seasons'][int(season)]['images'][0]['url']
    except:
        poster = data['images'][2]['url']

    try:
        banner = data['seasons'][int(season)]['images'][1]['url']
    except:
        banner = data['images'][1]['url']

    fanart = data['images'][0]['url']

    for line in data['episodes']:
        try:
            if int(line['seasonNumber']) == int(season) and int(line['episodeNumber']) == int(episode):
                if line['overview']:
                    overview = line['overview']
                if line['image']:
                    thumb = line['image']
                break
            else:
                continue
        except:
            pass

    if len(str(season)) == 1:
        season = "0{}".format(season)
    if len(str(episode)) == 1:
        episode = "0{}".format(episode)
    if len(str(overview)) == 0:
        overview = "None"

    message = {
        "text": "New episode downloaded - {}: {}".format(media_title, episode_title),
        "username": slack_user,
        "icon_emoji": slack_icon,
        "channel": slack_channel_tv,
        "attachments": [
            {"title": "{}: {}".format(media_title, episode_title),
             "color": "#3ae367",
             "title_link": "{}series/{}".format(sonarr_url, title_slug),
             "fields": [{"title": "Episode",
                         "value": "s{}e{}".format(season, episode),
                         "short": True},
                        {"title": "Quality",
                         "value": quality,
                         "short": True}],
             "author_name": "Sonarr",
             "author_link": sonarr_url,
             "author_icon": sonarr_icon,
             "image_url": banner, },
            {"title": "Overview",
             "color": "#3AA3E3",
             "text": overview,
             "footer": "{} - Is upgrade: {}".format(scene_name, is_upgrade)}
        ]
    }

elif sys.argv[1].lower() == "radarr":
    media_title = os.environ.get('radarr_movie_title')
    imdb_id = os.environ.get('radarr_movie_imdbid')
    quality = os.environ.get('radarr_moviefile_quality')
    scene_name = os.environ.get("radarr_moviefile_scenename")

    title_slug = media_title.replace(" ", "-")

    moviedb_url = "https://api.themoviedb.org/3/find/{}?api_key={}&external_source=imdb_id".format(imdb_id, moviedb_key)
    omdb_url = "https://www.omdbapi.com/?i={}&apikey={}".format(imdb_id, omdb_key)

    request = requests.get(moviedb_url)
    data = request.json()

    request_omdb = requests.get(omdb_url)
    data_omdb = request_omdb.json()

    overview = data['movie_results'][0]['overview']
    release = data['movie_results'][0]['release_date']
    poster_path = data['movie_results'][0]['poster_path']
    poster_path = "https://image.tmdb.org/t/p/w185" + poster_path
    imdburl = "https://www.imdb.com/title/" + imdb_id
    radarr_id = data['movie_results'][0]['id']
    imdbrating = data_omdb['imdbRating']
    year = data_omdb['Year']

    message = {
        "text": "New movie downloaded - {} ({}) IMDB: {}".format(media_title, year, imdbrating),
        "username": slack_user,
        "icon_emoji": slack_icon,
        "channel": slack_channel_movie,
        "attachments": [
            {"title": "{} ({})".format(media_title, year, imdbrating),
             "color": "#3ae367",
             "title_link": "{}movies/{}-{}".format(radarr_url, title_slug.lower(), radarr_id),
             "author_name": "Radarr",
             "author_link": radarr_url,
             "author_icon": radarr_icon,
             "image_url": poster_path, },
            {"title": "Overview",
             "color": "#3AA3E3",
             "text": overview,
             "footer": "{} - {} - Release Date: {}".format(quality, scene_name, release)},
	    {"title": "IMDB URL",
             "color": "#e3b53a",
             "text": imdburl}
        ]
    }


log.info(json.dumps(message, sort_keys=True, indent=4, separators=(',', ': ')))

# Send notification
r = requests.post(slack_url, headers=slack_headers, json=message)
