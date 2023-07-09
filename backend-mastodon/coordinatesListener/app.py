from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import traceback
import json
import threading
from runListener import MyListener, start_listener, HtmlUpdater

app = Flask(__name__)
CORS(app)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Define the path for the data folder
data_folder = "data"
archive_folder = os.path.join(data_folder, "archive")
templates_folder = "templates"
html_file = os.path.join(templates_folder, "status_list.html")

# Ensure the data and archive folders exist
os.makedirs(data_folder, exist_ok=True)
os.makedirs(archive_folder, exist_ok=True)
os.makedirs(templates_folder, exist_ok=True)

# Start the listener in a separate thread
listener = MyListener()
listener_thread = threading.Thread(target=start_listener, args=(listener,))
listener_thread.start()

# Create an instance of the HtmlUpdater class
html_updater = HtmlUpdater(listener.status_list, html_file)

# Route to update JSON file
@app.route('/data/<file_name>', methods=['PUT'])
def update_json(file_name):
    json_data = request.get_json()
    file_path = os.path.join(data_folder, file_name)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                data['coordinates']['latitude'] = json_data['latitude']
                data['coordinates']['longitude'] = json_data['longitude']
            with open(file_path, 'w') as file:
                json.dump(data, file)
            return jsonify({'message': f'Updated {file_name} successfully.'})
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': f'An error occurred while updating {file_name}.'}), 500
    else:
        return jsonify({'error': f'File {file_name} does not exist.'}), 404

# Route to archive JSON file
@app.route('/data/<file_name>', methods=['DELETE'])
def archive_json(file_name):
    file_path = os.path.join(data_folder, file_name)
    archive_path = os.path.join(archive_folder, file_name)
    if os.path.exists(file_path):
        os.rename(file_path, archive_path)
        return jsonify({'message': f'Archived {file_name} successfully.'})
    else:
        return jsonify({'error': f'File {file_name} does not exist.'}), 404

@app.route('/update-html', methods=['POST'])
def update_html():
    # Update the status list
    html_updater.update_status_list()

    # Update the HTML file
    html_updater.update_html_file()

    print("Status List updated.")

# Route to update JSON files from the status list page
@app.route('/update-jsons', methods=['POST'])
def update_jsons():
    updated_data = request.get_json()

    for update in updated_data:
        file_name = f"{update['id']}.json"
        file_path = os.path.join(data_folder, file_name)

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    data['coordinates']['latitude'] = update['latitude']
                    data['coordinates']['longitude'] = update['longitude']
                with open(file_path, 'w') as file:
                    json.dump(data, file)
            except Exception as e:
                traceback.print_exc()
                return jsonify({'error': f'An error occurred while updating {file_name}.'}), 500
        else:
            return jsonify({'error': f'File {file_name} does not exist.'}), 404

    return jsonify({'message': 'JSON files updated successfully.'})

# Route to serve the status list page
@app.route('/')
def status_list():
    return render_template('status_list.html')

if __name__ == '__main__':
    app.run()
