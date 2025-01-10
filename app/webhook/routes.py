from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import datetime

# Initialize MongoDB client
client = MongoClient('mongodb+srv://saloni15627:salonipandey014@cluster3.mgvianu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster3')
db = client['github-webhook']
collection = db['events']

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    try:
        # Get the GitHub webhook payload
        payload = request.get_json()
        
        # Initialize event data
        event_data = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'type': '',
            'message': ''
        }

        # Handle different types of events
        if 'pusher' in payload:
            # Push event
            branch = payload['ref'].split('/')[-1]
            event_data.update({
                'type': 'PUSH',
                'message': f"{payload['pusher']['name']} pushed to \"{branch}\" on {datetime.datetime.utcnow().strftime('%d %B %Y - %H:%M %Z UTC')}"
            })
            
        elif 'pull_request' in payload:
            # Pull request event
            pr = payload['pull_request']
            event_data.update({
                'type': 'PULL_REQUEST',
                'message': f"{payload['sender']['login']} submitted a pull request from \"{pr['head']['ref']}\" to \"{pr['base']['ref']}\" on {datetime.datetime.utcnow().strftime('%d %B %Y - %H:%M %Z UTC')}"
            })
            
        elif all(key in payload for key in ['ref', 'before', 'after']):
            # Merge event
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

# Optional: Add a route to get events
@webhook.route('/events', methods=["GET"])
def get_events():
    try:
        # Get the latest 10 events, sorted by timestamp
        events = list(collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(10))
        return jsonify(events), 200
    except Exception as e:
        print(f"Error fetching events: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500