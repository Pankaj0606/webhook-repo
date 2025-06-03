from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timezone
from db import events

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.before_app_request
def log_every_request():
    print(f"🧭 Incoming request: {request.method} {request.path}")

@webhook_bp.route('/')
def home():
    return render_template('index.html')

@webhook_bp.route('/webhook', methods=['POST'])
def github_webhook():
    print("Headers:", dict(request.headers))
    print("Raw Data:", request.data)

    try:
        payload = request.get_json(force=True)
    except Exception as e:
        print("❌ Failed to parse JSON:", e)
        return jsonify({"error": "Bad JSON"}), 400

    if not payload:
        return jsonify({"error": "Empty payload"}), 400

    print("✅ Parsed payload:", payload)

    action_type = None
    author = None
    from_branch = None
    to_branch = None
    timestamp = datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC")
    request_id = None

    if 'commits' in payload:
        action_type = "PUSH"
        author = payload['pusher']['name']
        to_branch = payload['ref'].split('/')[-1]
        request_id = f"{payload['head_commit']['id']}_{action_type}"
    elif 'pull_request' in payload and payload.get('action') == 'closed' and payload['pull_request']['merged']:
        print("🎯 Detected MERGE event!")
        action_type = "MERGE"
        author = payload['pull_request']['user']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        request_id = f"{payload['pull_request']['id']}_{action_type}"
        print(f"Merge by {author} from {from_branch} to {to_branch} at {timestamp}")
    elif 'pull_request' in payload and payload.get('action') == 'opened':
        action_type = "PULL_REQUEST"
        author = payload['pull_request']['user']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        request_id = f"{payload['pull_request']['id']}_{action_type}"

    if action_type:
        if events.find_one({"request_id": request_id}):
            return jsonify({"status": "duplicate"}), 200

        doc = {
            "request_id": request_id,
            "author": author,
            "action": action_type,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
        events.insert_one(doc)
        print(f"Inserted event: {doc}")
        return jsonify({"status": "stored"}), 201

    return jsonify({"status": "ignored"}), 200

@webhook_bp.route('/events', methods=['GET'])
def get_events():
    recent_events = list(events.find().sort("timestamp", -1).limit(20))
    for e in recent_events:
        e['_id'] = str(e['_id'])
    return jsonify(recent_events)
