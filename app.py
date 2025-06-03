from flask import Flask, jsonify
from flask_cors import CORS
from routes.webhook_routes import webhook_bp
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Register routes
app.register_blueprint(webhook_bp)

@app.errorhandler(403)
def forbidden(e):
    print("❌ Flask is returning 403:", e)
    return jsonify(error="Forbidden"), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
