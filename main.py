from flask import Flask, request, send_from_directory, jsonify, render_template
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dictionary to track the state for each device
device_states = {}

firmware_filename = None

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global firmware_filename, device_states
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        firmware_filename = file.filename
        # Reset the state for all devices
        for mac in device_states:
            device_states[mac] = {'download': True, 'update': False}
        return jsonify({'success': True, 'file_path': file.filename, 'message': 'Firmware uploaded successfully'})

@app.route('/download/firmware.bin', methods=['GET'])
def download_firmware():
    if firmware_filename:
        return send_from_directory(app.config['UPLOAD_FOLDER'], firmware_filename)
    return 'Firmware file not found', 404

@app.route('/trigger_download_firmware', methods=['POST'])
def trigger_download_firmware():
    global device_states
    for mac in device_states:
        device_states[mac]['download'] = True
    return jsonify({"success": True})

@app.route('/trigger_ota_update', methods=['POST'])
def trigger_ota_update():
    global device_states
    for mac in device_states:
        device_states[mac]['update'] = True
    return jsonify({"success": True})

@app.route('/check_flags', methods=['GET'])
def check_flags():
    mac = request.args.get('mac')
    if mac:
        if mac not in device_states:
            device_states[mac] = {'download': False, 'update': False}
        state = device_states[mac]
        response = {
            "download": state['download'],
            "update": state['update']
        }
        # Reset flags after they are checked for this specific device
        device_states[mac] = {'download': False, 'update': False}
        return jsonify(response)
    return jsonify({"download": False, "update": False})

@app.route('/check_update', methods=['GET'])
def check_update():
    global firmware_filename
    if firmware_filename:
        return jsonify({"update": True})
    return jsonify({"update": False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
