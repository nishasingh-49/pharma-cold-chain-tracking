# node/app.py
import os
import sys
from flask import Flask, jsonify

# This line adds the 'src' directory to Python's path
# so we can import modules from it.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from api.wallet import wallet_bp, crypto_bp

def create_app():
    """Application factory function"""
    app = Flask(__name__)

    # Get the Node ID from an environment variable
    app.config['NODE_ID'] = os.environ.get('NODE_ID', 'node-unknown')
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'ok': True,
            'nodeId': app.config['NODE_ID']
        }), 200

    # Register our blueprints
    app.register_blueprint(wallet_bp, url_prefix='/wallet')
    app.register_blueprint(crypto_bp, url_prefix='/crypto')
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)