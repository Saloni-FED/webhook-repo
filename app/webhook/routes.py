from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import datetime
import os
import hmac
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MongoDB client
MONGODB_URI = os.getenv('MONGODB_URI')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')


client = MongoClient(MONGODB_URI)
db = client['github-webhook']
collection = db['events']

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

def verify_signature(payload_body, signature_header):
    """Verify that the webhook is from GitHub"""
    if not signature_header:
        return False
    
    expected_signature = hmac.new(
        key=WEBHOOK_SECRET.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature_header)

@webhook.route('/receiver', methods=["POST"])
def receiver():
    try:
        # Verify GitHub webhook signature
        signature = request.headers.get('X-Hub-Signature-256')
        if not verify_signature(request.get_data(), signature):
            return jsonify({'error': 'Invalid signature'}), 401

        # Get the GitHub webhook payload
        if request.content_type == 'application/x-www-form-urlencoded':
            payload = request.form.to_dict()
            if 'payload' in payload:
                import json
                payload = json.loads(payload['payload'])
        else:
            payload = request.get_json()
        
        # Initialize event data
        event_data = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'type': '',
            'message': ''
        }

        # Handle different types of events
        if 'pusher' in payload:
            branch = payload['ref'].split('/')[-1]
            event_data.update({
                'type': 'PUSH',
                'message': f"{payload['pusher']['name']} pushed to \"{branch}\" on {datetime.datetime.utcnow().strftime('%d %B %Y - %H:%M %Z UTC')}"
            })
            
        elif 'pull_request' in payload:
            pr = payload['pull_request']
            event_data.update({
                'type': 'PULL_REQUEST',
                'message': f"{payload['sender']['login']} submitted a pull request from \"{pr['head']['ref']}\" to \"{pr['base']['ref']}\" on {datetime.datetime.utcnow().strftime('%d %B %Y - %H:%M %Z UTC')}"
            })
            
        elif all(key in payload for key in ['ref', 'before', 'after']):
            branch = payload['ref'].split('/')[-1]
            event_data.update({
                'type': 'MERGE',
                'message': f"{payload['sender']['login']} merged branch \"{branch}\" on {datetime.datetime.utcnow().strftime('%d %B %Y - %H:%M %Z UTC')}"
            })

        # Store in MongoDB
        if event_data['type']:
            collection.insert_one(event_data)

        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

@webhook.route('/events', methods=["GET"])
def get_events():
    try:
        events = list(collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(10))
        print(events)
        return jsonify(events), 200
    except Exception as e:
        print(f"Error fetching events: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500