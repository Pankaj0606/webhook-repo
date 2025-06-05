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
    print("➡️ Webhook endpoint hit!")
    print("Headers:", dict(request.headers))
    print("Raw Data:", request.data)

    try:
        payload = request.get_json(force=True)
        print("✅ JSON payload parsed successfully.")
    except Exception as e:
        print("❌ Failed to parse JSON:", e)
        return jsonify({"error": "Bad JSON"}), 400

    if not payload:
        print("⚠️ Received empty payload.")
        return jsonify({"error": "Empty payload"}), 400

    print("✅ Payload content:", payload)

    action_type = None
    author = None
    from_branch = None
    to_branch = None
    timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()  # UTC ISO string
    request_id = None

    if 'commits' in payload:
        action_type = "PUSH"
        author = payload.get('pusher', {}).get('name')
        to_branch = payload.get('ref', '').split('/')[-1]
        request_id = f"{payload.get('head_commit', {}).get('id', 'unknown')}_{action_type}"
        print(f"Detected PUSH event by {author} to {to_branch} at {timestamp}")
    elif 'pull_request' in payload and payload.get('action') == 'closed' and payload['pull_request'].get('merged'):
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
        print(f"Pull request opened by {author} from {from_branch} to {to_branch} at {timestamp}")

    if action_type:
        # Check duplicates
        if events.find_one({"request_id": request_id}):
            print(f"⚠️ Duplicate event detected: {request_id}, ignoring.")
            return jsonify({"status": "duplicate"}), 200

        doc = {
            "request_id": request_id,
            "author": author,
            "action": action_type,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }

        try:
            events.insert_one(doc)
            print(f"✅ Inserted event: {doc}")
        except Exception as e:
            print(f"❌ MongoDB insert error: {e}")
            return jsonify({"error": "Database error"}), 500

        return jsonify({"status": "stored"}), 201

    print("ℹ️ Event ignored: no matching action_type.")
    return jsonify({"status": "ignored"}), 200


@webhook_bp.route('/events', methods=['GET'])
def get_events():
    recent_events = list(events.find().sort("timestamp", -1).limit(20))
    for e in recent_events:
        e['_id'] = str(e['_id'])
    return jsonify(recent_events)
