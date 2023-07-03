from mastodon import Mastodon
import json
from datetime import datetime
import os

# Define the URL you want to check for in the messages
target_url = 'map.decarbnow.space'

# Define the path for the data folder
data_folder = "data"

# Create an instance of Mastodon
mastodon = Mastodon(access_token='backend_mastodon_usercred.secret')

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

# Search for messages containing the target URL
search_results = mastodon.search(target_url)
print(search_results)

# Check each search result for the target URL
for status in search_results['statuses']:
    # Generate a unique filename using ID
    message_id = status['id']
    filename = f'{message_id}.json'
    filepath = os.path.join(data_folder, filename)

    # Save the relevant information to a JSON file
    with open(filepath, 'w') as output_file:
        json.dump(status, output_file, cls=DateTimeEncoder)

    print(f'Message with ID {message_id} saved to {filepath}')