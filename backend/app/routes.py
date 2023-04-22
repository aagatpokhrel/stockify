from app import app
from flask import jsonify, request, Response

@app.route('/subscribe', methods=['GET'])
def subscribe():
    return jsonify({'message': 'Subscribed'})
