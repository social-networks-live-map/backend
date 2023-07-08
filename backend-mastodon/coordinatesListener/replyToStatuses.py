import os
import json
from mastodon import Mastodon
import shutil

# Define the path for the data folder
data_folder = "data"
archive_folder = os.path.join(data_folder, "archive")

# Create an instance of Mastodon
mastodon = Mastodon(access_token='../backend_mastodon_usercred.secret')

# Ensure the archive folder exists
os.makedirs(archive_folder, exist_ok=True)

# Iterate over the JSON files in the data folder
for filename in os.listdir(data_folder):
    if filename.endswith(".json"):
        filepath = os.path.join(data_folder, filename)

        # Read the JSON file
        with open(filepath, 'r') as file:
            status = json.load(file)

        # Extract the latitude and longitude from the coordinates field
        coordinates = status['coordinates']
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']

        # Check if the status still exists
        try:
            mastodon.status(status['id'])
        except:
            # Move the file to the archive folder
            archive_filepath = os.path.join(archive_folder, filename)
            shutil.move(filepath, archive_filepath)
            print(f"Status with ID {status['id']} doesn't exist. Moved file {filename} to archive folder.")
            continue

        # Create the Google Maps link
        if latitude and longitude:
            map_link = f"https://www.google.com/maps/place/{latitude},{longitude}/@{latitude},{longitude},1500m/data=!3m1!1e3"

            # Create the reply content
            reply_content = f"Here's the Google Maps link for the coordinates: {map_link}"

            # Reply to the status
            mastodon.status_post(reply_content, in_reply_to_id=status['id'])

            # Print or perform further actions with the reply
            print("Replied to status ID:", status['id'])

        # Move the file to the archive folder
        archive_filepath = os.path.join(archive_folder, filename)
        shutil.move(filepath, archive_filepath)
        print(f"Moved file {filename} to archive folder")
