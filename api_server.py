# -*- coding: utf-8 -*-
"""
SözUstası Bot API Server
KontrolBot ilə əlaqə üçün Flask API server
"""

from flask import Flask, jsonify, request
import threading
import logging
import random
import os

# Global bot application instance (main.py-dan set ediləcək)
bot_app = None

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Flask log-larını minimize et

# -------------------------------------------------
# API ENDPOINTS
# -------------------------------------------------

# Health check endpoints (Render üçün)
@app.route('/')
def home():
    return "SözUstası Bot işləyir! 🐿️"

@app.route('/healthz')
def healthz():
    """UptimeRobot və ya oxşar xidmətlər üçün health check endpoint"""
    return {"status": "healthy", "message": "SözUstası Bot is running"}, 200

@app.route('/ping')
def ping():
    return "pong", 200

# Bot API endpoints

@app.route('/status', methods=['GET'])
def get_status():
    """Bot statusunu qaytarır"""
    return jsonify({
        "success": True,
        "data": {
            "status": "active",
            "bot_name": "SözUstası"
        }
    })

@app.route('/groups/count', methods=['GET'])
def get_groups_count():
    """Qrup sayını qaytarır"""
    try:
        from groups import load_groups
        groups = load_groups()
        count = len(groups)
        
        return jsonify({
            "success": True,
            "data": {
                "count": count
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Xəta: {str(e)}"
        }), 500

@app.route('/groups/list', methods=['GET'])
def get_groups_list():
    """Qrupların siyahısını qaytarır (üzv sayı və linklə)"""
    import asyncio
    
    async def fetch_group_data():
        try:
            from groups import load_groups, save_group
            groups = load_groups()
            
            # Hər qrup üçün üzv sayını və linki yenilə
            if bot_app:
                for chat_id_str, group_data in groups.items():
                    try:
                        chat_id = int(chat_id_str)
                        
                        # Üzv sayını əldə et
                        member_count = await bot_app.bot.get_chat_member_count(chat_id)
                        
                        # Qrup linkini əldə et (əgər mümkündürsə)
                        try:
                            chat = await bot_app.bot.get_chat(chat_id)
                            link = chat.link if hasattr(chat, 'link') and chat.link else None
                            if not link and chat.username:
                                link = f"https://t.me/{chat.username}"
                        except:
                            link = None
                        
                        # Məlumatı yenilə
                        groups[chat_id_str]['member_count'] = member_count
                        if link:
                            groups[chat_id_str]['link'] = link
                        
                        # Qrupu yaddaşa yenidən yaz
                        save_group(chat_id, group_data['title'], member_count, link)
                        
                    except Exception as e:
                        logging.error(f"Qrup məlumatı yenilənmədi {chat_id_str}: {e}")
            
            return {
                "success": True,
                "data": {
                    "groups": groups
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Xəta: {str(e)}"
            }
    
    try:
        # Async funksiyaını sync context-də işlət
        result = asyncio.run(fetch_group_data())
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Xəta: {str(e)}"
        }), 500

@app.route('/groups/broadcast', methods=['POST'])
def broadcast_message():
    """Gruplara mesaj göndərir"""
    try:
        data = request.get_json()
        message = data.get('message')
        target = data.get('target', 'all')  # 'all', 'half', 'selected'
        group_ids = data.get('group_ids', [])
        
        if not message:
            return jsonify({
                "success": False,
                "message": "Mesaj göndərilməyib"
            }), 400
        
        from groups import load_groups
        groups = load_groups()
        
        if not groups:
            return jsonify({
                "success": False,
                "message": "Heç bir qrup yoxdur"
            }), 404
        
        # Target-a görə qrupları seç
        target_groups = []
        
        if target == 'all':
            target_groups = list(groups.keys())
        elif target == 'half':
            all_groups = list(groups.keys())
            half_size = len(all_groups) // 2
            target_groups = random.sample(all_groups, half_size)
        elif target == 'selected':
            target_groups = [str(gid) for gid in group_ids if str(gid) in groups]
        
        # Mesajları göndər
        sent_count = 0
        failed_count = 0
        
        if bot_app:
            import asyncio
            
            async def send_messages():
                nonlocal sent_count, failed_count
                for chat_id in target_groups:
                    try:
                        await bot_app.bot.send_message(
                            chat_id=int(chat_id),
                            text=message,
                            parse_mode='Markdown'
                        )
                        sent_count += 1
                    except Exception as e:
                        logging.error(f"Qrupa mesaj göndərilmədi {chat_id}: {e}")
                        failed_count += 1
            
            # Async loop-da işlət
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(send_messages())
            loop.close()
        
        return jsonify({
            "success": True,
            "data": {
                "sent_count": sent_count,
                "failed_count": failed_count,
                "total_targets": len(target_groups)
            },
            "message": "Broadcast tamamlandı"
        })
        
    except Exception as e:
        logging.error(f"Broadcast xətası: {e}")
        return jsonify({
            "success": False,
            "message": f"Xəta: {str(e)}"
        }), 500

# -------------------------------------------------
# SERVER BAŞLATMA
# -------------------------------------------------

def start_api_server(port=5001):
    """API server-i ayrı thread-də başlat"""
    def run():
        # Render üçün PORT environment variable istifadə et
        # Yerli development üçün default port
        api_port = int(os.environ.get('PORT', port))
        logging.info(f"🌐 API Server (health + API endpoints) başladılır: port {api_port}")
        app.run(host='0.0.0.0', port=api_port, debug=False, use_reloader=False)
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    logging.info(f"✅ API Server thread-i başladıldı")

def set_bot_application(application):
    """Bot application instance-ı set et (main.py-dan çağrılır)"""
    global bot_app
    bot_app = application
    logging.info("✅ Bot application API server-ə bağlandı")
