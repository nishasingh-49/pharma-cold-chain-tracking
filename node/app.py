# node/app.py
import os
from flask import Flask, jsonify

# Create the Flask app instance
app = Flask(__name__)

# Get the Node ID from an environment variable, default to "node-unknown"
NODE_ID = os.environ.get('NODE_ID', 'node-unknown')

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to confirm the node is running.
    """
    response = {
        'ok': True,
        'nodeId': NODE_ID
    }
    return jsonify(response), 200

if __name__ == '__main__':
    # Run the app on port 8000, accessible from any IP address within the Docker network
    app.run(host='0.0.0.0', port=8000)