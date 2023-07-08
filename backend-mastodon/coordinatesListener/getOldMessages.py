from mastodon import Mastodon
import json
from datetime import datetime
import os
import shutil
import re

# Define the regular expression pattern to match coordinates
coord_pattern = r'(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)'

# Define the path for the data folder and archive subfolder
data_folder = "data"
archive_folder = os.path.join(data_folder, "archive")

# Ensure the data and archive folders exist
os.makedirs(data_folder, exist_ok=True)
os.makedirs(archive_folder, exist_ok=True)

# Get a list of existing message IDs in the data folder
existing_ids = [filename.split(".")[0] for filename in os.listdir(data_folder) if filename.endswith(".json")]

# Create an instance of Mastodon
mastodon = Mastodon(access_token='../backend_mastodon_usercred.secret')

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

# Search for messages containing coordinates
search_results = mastodon.timeline_local()

# Check each search result for coordinates
for status in search_results:
    content = status['content']

    # Check if the content matches the coordinates pattern
    if re.search(coord_pattern, content):
        # Generate a unique filename using ID
        message_id = str(status['id'])
        filename = f'{message_id}.json'
        filepath = os.path.join(data_folder, filename)

        # Save the relevant information to a JSON file
        with open(filepath, 'w') as output_file:
            json.dump(status, output_file, cls=DateTimeEncoder)

        print(f'Message with ID {message_id} saved to {filepath}')

        # Remove the ID from the existing IDs list if found
        if message_id in existing_ids:
            existing_ids.remove(message_id)

# Move any remaining files in the data folder to the archive folder
for message_id in existing_ids:
    filename = f'{message_id}.json'
    filepath = os.path.join(data_folder, filename)
    archive_filepath = os.path.join(archive_folder, filename)
    shutil.move(filepath, archive_filepath)
    print(f'Message with ID {message_id} moved to archive folder')
