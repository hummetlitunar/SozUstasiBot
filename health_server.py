# -*- coding: utf-8 -*-
"""
Health Check Server - Render üçün tətbiqi oyaq saxlamaq üçün
UptimeRobot və ya oxşar xidmətlər üçün /healthz endpoint-i təmin edir
"""

from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "SözUstası Bot işləyir! 🐿️"

@app.route('/healthz')
def health_check():
    """UptimeRobot və ya oxşar xidmətlər üçün health check endpoint"""
    return {"status": "healthy", "message": "Bot is running"}, 200

@app.route('/ping')
def ping():
    return "pong", 200

def run_health_server():
    """Flask serverini ayrı thread-də işlət"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def start_health_server_thread():
    """Health server-i background thread-də başlat"""
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()
    print(f"✅ Health server işə düşdü - Port: {os.environ.get('PORT', 10000)}")
    return server_thread
