from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import json

app = Flask(__name__)

@app.route('/api/instagram/user', methods=['GET'])
def get_instagram_user():
    username = request.args.get('username')
    
    if not username:
        return jsonify({
            "error": "Username parameter is required",
            "example": "/api/instagram/user?username=instagram"
        }), 400
    
    try:
        # Fetch Instagram profile page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(f'https://www.instagram.com/{username}/', headers=headers)
        
        if response.status_code != 200:
            return jsonify({
                "error": f"Account not found or unavailable (HTTP {response.status_code})",
                "username": username
            }), 404
        
        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find script tag with JSON data
        script_tags = soup.find_all('script', type='text/javascript')
        data_script = None
        
        for script in script_tags:
            if 'window._sharedData' in script.text:
                data_script = script.text
                break
        
        if not data_script:
            return jsonify({
                "error": "Could not extract data from Instagram page",
                "username": username
            }), 500
        
        # Extract JSON data
        json_data = json.loads(data_script.split('window._sharedData = ')[1].rstrip(';'))
        
        # Extract user data
        user_data = json_data['entry_data']['ProfilePage'][0]['graphql']['user']
        
        # Format response
        result = {
            "username": user_data['username'],
            "full_name": user_data['full_name'],
            "biography": user_data['biography'],
            "followers": user_data['edge_followed_by']['count'],
            "following": user_data['edge_follow']['count'],
            "posts": user_data['edge_owner_to_timeline_media']['count'],
            "profile_pic": user_data['profile_pic_url_hd'],
            "is_private": user_data['is_private'],
            "is_verified": user_data['is_verified'],
            "external_url": user_data['external_url'],
            "success": True,
            "credit": "Made with ❤️ by @DIWANI_xD"
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "username": username,
            "credit": "Made with ❤️ by @DIWANI_xD"
        }), 500

@app.route('/')
def home():
    return jsonify({
        "message": "Instagram Public Data API",
        "endpoints": {
            "get_user_info": "/api/instagram/user?username=USERNAME"
        },
        "credit": "Made with ❤️ by @DIWANI_xD"
    })

if __name__ == '__main__':
    app.run(debug=True)