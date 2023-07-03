from mastodon import StreamListener, Mastodon
import time
import json
from datetime import datetime
import os
import shutil

# Define the URL you want to check for in the messages
target_url = 'https://map.decarbnow.space'

# Define the path for the data folder and archive subfolder
data_folder = "data"
archive_folder = os.path.join(data_folder, "archive")

# Ensure the data and archive folders exist
os.makedirs(data_folder, exist_ok=True)
os.makedirs(archive_folder, exist_ok=True)

# Get a list of existing message IDs in the data folder
existing_ids = [filename.split(".")[0] for filename in os.listdir(data_folder) if filename.endswith(".json")]

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

# Custom listener class that inherits from StreamListener
class MyListener(StreamListener):
    def on_update(self, status):
        if target_url in status['content']:
            # Generate a unique filename using ID
            message_id = status['id']
            filename = f'{message_id}.json'
            filepath = os.path.join(data_folder, filename)

            # Save the relevant information to a JSON file
            with open(filepath, 'a') as output_file:
                json.dump(status, output_file, cls=DateTimeEncoder)
                output_file.write('\n')
                print('Output file written')

            # Update the existing_ids list
            existing_ids.append(str(message_id))

    def on_delete(self, status_id):
        if str(status_id) in existing_ids:
            # Move the corresponding file to the archive subfolder
            filename = f'{status_id}.json'
            filepath = os.path.join(data_folder, filename)
            archive_filepath = os.path.join(archive_folder, filename)
            shutil.move(filepath, archive_filepath)
            print('Message deleted, file moved to archive folder')

            # Update the existing_ids list
            existing_ids.remove(str(status_id))

    def on_streaming_error(self, error):
        print(f"Streaming error occurred: {error}")

# Create an instance of Mastodon
mastodon = Mastodon(access_token='backend_mastodon_usercred.secret')

# Create an instance of the custom listener
listener = MyListener()

# Retry the connection with exponential backoff
retry_delay = 5  # Initial delay in seconds
max_retries = 10  # Maximum number of retries
retry_count = 0  # Counter for tracking retries

while retry_count < max_retries:
    try:
        mastodon.stream_public(listener)
    except Exception as e:
        print(f"Connection error occurred: {e}")
        retry_count += 1
        print(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
        retry_delay *= 2  # Exponential backoff
