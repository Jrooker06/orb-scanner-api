from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Load API keys from environment variables
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

@app.route('/api/gainers', methods=['GET'])
def get_gainers():
    try:
        url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/gainers?apiKey={POLYGON_API_KEY}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/historical/<symbol>', methods=['GET'])
def get_historical(symbol):
    try:
        days_back = request.args.get('days_back', 0)
        interval = request.args.get('interval', '1')
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(days_back))
        
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{interval}/minute/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}?adjusted=true&sort=asc&limit=1000&apiKey={POLYGON_API_KEY}"
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))