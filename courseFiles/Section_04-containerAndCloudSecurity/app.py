from flask import Flask, send_from_directory, request, abort
import os
import logging
app = Flask(__name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'sensitive_data')
API_KEY = os.environ.get('API_KEY', '')
handler = logging.FileHandler('/tmp/secure_server_access.log')
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
@app.route('/<path:filename>')
def get_file(filename):
    api_key = request.headers.get('X-API-KEY', '')
    if not API_KEY or api_key != API_KEY:
        app.logger.info(f"DENY {request.remote_addr} {filename} headers={dict(request.headers)}")
        abort(403)
    app.logger.info(f"ALLOW {request.remote_addr} {filename}")
    return send_from_directory(os.path.abspath(DATA_DIR), filename, as_attachment=False)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))