# Better Slack Notifications

Better slack notifications for sonarr and radarr.

## To install

git clone `https://github.com/Dec64/Better_slack_notifcations.git`

or download onto your server.

To make executable: `chomod +X slack.py`

`nano slack.py`

and edit the config section, see below for details.

on sonarr/radarr add the script under, `settings > connect > Customscript` Run on download and on upgrade. Point to slack.py and in arguments, set either `sonarr` or `radarr` respectively 

```
slack_user = "Notification Bot"  # User name to post under
slack_icon = ":satellite_antenna:" # Slack icon for user
slack_channel_tv = "#tv" # What channel to post TV notifcations
slack_channel_movie = "#movies" # What channel to post Movie notifcations
slack_url = "" #URL of your slack webhook

sonarr_url = "" # URL to your sonarr (public accessible URL) for link in notifcation only
radarr_url = "" # URL to your radarr (public accessible URL) for link in notifcation only
```
