from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import os
import traceback
import json  # Add this line to import the json module

app = Flask(__name__)
CORS(app)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/data/<file_name>', methods=['PUT'])
def update_json(file_name):
    json_data = request.get_json()
    file_path = os.path.join('data', file_name)
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


@app.route('/data/<file_name>', methods=['DELETE'])
def archive_json(file_name):
    file_path = os.path.join('data', file_name)
    archive_path = os.path.join('data', 'archive', file_name)
    if os.path.exists(file_path):
        os.rename(file_path, archive_path)
        return jsonify({'message': f'Archived {file_name} successfully.'})
    else:
        return jsonify({'error': f'File {file_name} does not exist.'}), 404

@app.route('/update-jsons', methods=['POST'])
def update_jsons():
    updated_data = request.get_json()

    for update in updated_data:
        file_name = f"{update['id']}.json"
        file_path = os.path.join('data', file_name)

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


@app.route('/')
def status_list():
    return render_template('status_list.html')

if __name__ == '__main__':
    app.run()