from mastodon import StreamListener, Mastodon
import time
import json
from datetime import datetime
import os
import shutil
import re

# Define the path for the data folder
data_folder = "data"
archive_folder = os.path.join(data_folder, "archive")
html_file = "templates/status_list.html"

# Ensure the data and archive folders exist
os.makedirs(data_folder, exist_ok=True)
os.makedirs(archive_folder, exist_ok=True)

# Regular expression pattern to match coordinates
coord_pattern = r'(\-?\d+\.\d+),\s*(\-?\d+\.\d+)'

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

# Custom listener class
class MyListener(StreamListener):
    def __init__(self):
        super().__init__()
        self.status_list = []
        self.update_status_list()
        self.update_html_file()

    def on_update(self, status):
        # Check if the content matches the coordinates pattern
        content = status['content']
        if re.search(coord_pattern, content):
            coordinates = re.findall(coord_pattern, content)
            # Perform further processing or actions with the matched coordinates
            print("Coordinates found:", coordinates, "in message", status['url'])

            status['coordinates'] = {'latitude': coordinates[0][0], 'longitude': coordinates[0][1]}

            message_id = status['id']
            filename = f'{message_id}.json'
            filepath = os.path.join(data_folder, filename)

            # Save the relevant information to a JSON file
            with open(filepath, 'a') as output_file:
                json.dump(status, output_file, cls=DateTimeEncoder)
                output_file.write('\n')

            # Move the file to the archive folder
            #archive_filepath = os.path.join(archive_folder, filename)
            #shutil.move(filepath, archive_filepath)
            #print(f"Moved file {filename} to archive folder")

            # Update the status list
            self.update_status_list()

            # Update the HTML file
            self.update_html_file()

    def update_status_list(self):
        self.status_list = []
        # Get a list of JSON files in the data folder
        json_files = [filename for filename in os.listdir(data_folder) if filename.endswith(".json")]
        for filename in json_files:
            file_path = os.path.join(data_folder, filename)
            # Read the JSON file
            with open(file_path, 'r') as file:
                status = json.load(file)
                self.status_list.append(status)

    def update_html_file(self):
        # Generate the HTML content
        html_content = """
        <html>
        <head>
            <title>Status List</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
            <script src="{{ url_for('static', filename='script.js') }}"></script>
        </head>
        <body>
            <h1>Status List</h1>
            <form id="status-form">
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Content</th>
                        <th>Google Maps Link</th>
                        <th>Latitude</th>
                        <th>Longitude</th>
                        <th>Keep</th>
                    </tr>
        """

        for status in self.status_list:
            # Extract status information
            status_id = status['id']
            status_content = status['content']
            status_username = status['account']['username']
            latitude = status['coordinates'].get('latitude', '')
            longitude = status['coordinates'].get('longitude', '')

            # Create the Google Maps link
            if latitude and longitude:
                map_link = f"https://www.google.com/maps/place/{latitude},{longitude}/@{latitude},{longitude},1500m/data=!3m1!1e3"
                map_link_html = f"<a href='{map_link}' target='_blank'>LINK</a>"
            else:
                map_link_html = ""

            # Create the Mastodon URL link
            mastodon_url_html = f"<a href='{status['url']}' target='_blank'>{status_id}</a>"

            # Create the check mark column with checkboxes
            check_mark_html = f"<input type='checkbox' name='status-checkbox' value='{status_id}'>"

            # Add the row to the HTML content
            html_content += f"""
            <tr>
                <td>{mastodon_url_html}</td>
                <td>{status_content}</td>
                <td>{map_link_html}</td>
                <td><input type='text' value='{latitude}'></td>
                <td><input type='text' value='{longitude}'></td>
                <td>{check_mark_html}</td>
            </tr>
            """

        html_content += """
                </table>
                <br>
                <button type='button' onclick='updateJsons()'>OK</button>
            </form>
            <script src="{{ url_for('static', filename='script.js') }}"></script>
        </body>
        </html>
        """

        # Save the HTML content to the HTML file
        with open(html_file, 'w') as file:
            file.write(html_content)


    def on_streaming_error(self, error):
        print(f"Streaming error occurred: {error}")


# Create an instance of Mastodon
mastodon = Mastodon(access_token='../backend_mastodon_usercred.secret')

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
