from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock data for users and RSVPs
users = {}
rsvps = {}

# Create a new user profile
@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.json
    users[user_data['id']] = user_data
    return jsonify({"message": "User created successfully"}), 201

# RSVP to an event
@app.route('/rsvp', methods=['POST'])
def rsvp_event():
    rsvp_data = request.json
    rsvps[rsvp_data['userId']] = rsvp_data
    return jsonify({"message": "RSVP recorded"}), 201

# Get user RSVPs
@app.route('/rsvp/user/<user_id>', methods=['GET'])
def get_user_rsvps(user_id):
    if user_id in rsvps:
        return jsonify(rsvps[user_id]), 200
    return jsonify({"message": "No RSVPs found for this user"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)