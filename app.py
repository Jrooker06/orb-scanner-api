from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Load API keys from environment variables
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# =============================================================================
# MARKET DATA ENDPOINTS
# =============================================================================

@app.route('/api/gainers', methods=['GET'])
def get_gainers():
    """Get top gaining stocks"""
    try:
        url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/gainers?apiKey={POLYGON_API_KEY}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"Polygon API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/losers', methods=['GET'])
def get_losers():
    """Get top losing stocks"""
    try:
        url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/losers?apiKey={POLYGON_API_KEY}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"Polygon API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/volume/<symbol>', methods=['GET'])
def get_volume(symbol):
    """Get volume data for a stock"""
    try:
        # Get data from the last 5 days to ensure we have data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)
        
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}?adjusted=true&sort=desc&limit=5&apiKey={POLYGON_API_KEY}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                # Get the most recent data
                latest = data['results'][0]
                return jsonify({
                    "symbol": symbol, 
                    "volume": latest.get('v', 0),
                    "price": latest.get('c', 0),
                    "high": latest.get('h', 0),
                    "low": latest.get('l', 0),
                    "open": latest.get('o', 0),
                    "date": datetime.fromtimestamp(latest.get('t', 0)/1000).strftime('%Y-%m-%d')
                })
            else:
                return jsonify({"error": "No data found for this symbol"}), 404
        else:
            return jsonify({"error": f"Polygon API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/float/<symbol>', methods=['GET'])
def get_float(symbol):
    """Get float data from Polygon"""
    try:
        # Use Polygon's ticker details endpoint to get float information
        url = f"https://api.polygon.io/v3/reference/tickers/{symbol}?apiKey={POLYGON_API_KEY}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('results', {})
            
            # Extract float information
            float_info = {
                "symbol": symbol,
                "float": result.get('share_class_shares_outstanding', 0),
                "market_cap": result.get('market_cap', 0),
                "shares_outstanding": result.get('share_class_shares_outstanding', 0),
                "company_name": result.get('name', ''),
                "primary_exchange": result.get('primary_exchange', ''),
                "currency": result.get('currency_name', 'USD')
            }
            
            return jsonify(float_info)
        else:
            return jsonify({"error": f"Polygon API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sector/<symbol>', methods=['GET'])
def get_sector(symbol):
    """Get sector information for a stock"""
    try:
        # Use Polygon's ticker details endpoint to get sector information
        url = f"https://api.polygon.io/v3/reference/tickers/{symbol}?apiKey={POLYGON_API_KEY}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('results', {})
            
            # Extract sector information
            sector_info = {
                "symbol": symbol,
                "sector": result.get('sic_description', 'Unknown'),
                "industry": result.get('sic_description', 'Unknown'),
                "company_name": result.get('name', ''),
                "primary_exchange": result.get('primary_exchange', ''),
                "market_cap": result.get('market_cap', 0)
            }
            
            return jsonify(sector_info)
        else:
            return jsonify({"error": f"Polygon API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# HISTORICAL DATA ENDPOINTS
# =============================================================================

@app.route('/api/historical/<symbol>', methods=['GET'])
def get_historical(symbol):
    """Get historical price data"""
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
            return jsonify({"error": f"Polygon API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# TECHNICAL ANALYSIS ENDPOINTS
# =============================================================================

@app.route('/api/rsi/<symbol>', methods=['GET'])
def get_rsi(symbol):
    """Calculate RSI indicator"""
    try:
        days_back = request.args.get('days_back', 14)
        period = request.args.get('period', 14)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(days_back))
        
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}?adjusted=true&sort=asc&limit=1000&apiKey={POLYGON_API_KEY}"
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                # Simple RSI calculation
                prices = [result['c'] for result in data['results']]
                rsi = calculate_rsi(prices, int(period))
                return jsonify({"symbol": symbol, "rsi": rsi, "period": period})
            else:
                return jsonify({"error": "No data found"}), 404
        else:
            return jsonify({"error": f"Polygon API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/macd/<symbol>', methods=['GET'])
def get_macd(symbol):
    """Calculate MACD indicator"""
    try:
        days_back = request.args.get('days_back', 30)
        fast = request.args.get('fast', 12)
        slow = request.args.get('slow', 26)
        signal = request.args.get('signal', 9)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(days_back))
        
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}?adjusted=true&sort=asc&limit=1000&apiKey={POLYGON_API_KEY}"
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                prices = [result['c'] for result in data['results']]
                macd_line, signal_line, histogram = calculate_macd(prices, int(fast), int(slow), int(signal))
                return jsonify({
                    "symbol": symbol, 
                    "macd_line": macd_line, 
                    "signal_line": signal_line, 
                    "histogram": histogram,
                    "fast": fast,
                    "slow": slow,
                    "signal": signal
                })
            else:
                return jsonify({"error": "No data found"}), 404
        else:
            return jsonify({"error": f"Polygon API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vwap/<symbol>', methods=['GET'])
def get_vwap(symbol):
    """Calculate VWAP"""
    try:
        days_back = request.args.get('days_back', 1)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(days_back))
        
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}?adjusted=true&sort=asc&limit=1000&apiKey={POLYGON_API_KEY}"
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                vwap = calculate_vwap(data['results'])
                return jsonify({"symbol": symbol, "vwap": vwap})
            else:
                return jsonify({"error": "No data found"}), 404
        else:
            return jsonify({"error": f"Polygon API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# NEWS & SENTIMENT ENDPOINTS
# =============================================================================

@app.route('/api/news/<symbol>', methods=['GET'])
def get_news(symbol):
    """Get news for a stock"""
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from=2024-01-01&to=2024-12-31&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"Finnhub API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sentiment/<symbol>', methods=['GET'])
def get_sentiment(symbol):
    """Get social sentiment"""
    try:
        url = f"https://finnhub.io/api/v1/stock/sentiment?symbol={symbol}&from=2024-01-01&to=2024-12-31&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"Finnhub API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    if len(prices) < period + 1:
        return None
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD indicator"""
    if len(prices) < slow:
        return None, None, None
    
    # Calculate EMAs
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    # Calculate MACD line
    macd_line = ema_fast - ema_slow
    
    # For signal line, we need to calculate MACD for each day
    # This is a simplified version - in practice you'd need the full MACD history
    if len(prices) >= slow + signal:
        # Calculate MACD values for signal line
        macd_values = []
        for i in range(slow, len(prices)):
            ema_fast_i = calculate_ema(prices[:i+1], fast)
            ema_slow_i = calculate_ema(prices[:i+1], slow)
            macd_values.append(ema_fast_i - ema_slow_i)
        
        if len(macd_values) >= signal:
            signal_line = calculate_ema(macd_values, signal)
            histogram = macd_line - signal_line
            return round(macd_line, 2), round(signal_line, 2), round(histogram, 2)
    
    # Fallback: simple calculation
    signal_line = macd_line * 0.8  # Simplified signal line
    histogram = macd_line - signal_line
    return round(macd_line, 2), round(signal_line, 2), round(histogram, 2)

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return prices[-1] if prices else 0
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    
    for price in prices[period:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema

def calculate_vwap(data):
    """Calculate Volume Weighted Average Price"""
    total_volume = 0
    volume_price_sum = 0
    
    for bar in data:
        volume = bar.get('v', 0)
        price = bar.get('c', 0)  # Close price
        total_volume += volume
        volume_price_sum += volume * price
    
    if total_volume == 0:
        return 0
    
    vwap = volume_price_sum / total_volume
    return round(vwap, 2)

# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_keys_configured": bool(POLYGON_API_KEY and FINNHUB_API_KEY)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
