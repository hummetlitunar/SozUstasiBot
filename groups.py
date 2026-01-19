# -*- coding: utf-8 -*-
import json
import os

GROUPS_FILE = "groups.json"

def load_groups():
    """Yaddaşdan qrupları yüklə"""
    if not os.path.exists(GROUPS_FILE):
        return {}
    
    try:
        with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Qruplar yüklənərkən xəta: {e}")
        return {}

def save_group(chat_id, title, member_count=None, link=None):
    """Qrupu yadda saxla"""
    groups = load_groups()
    
    # Əgər qrup artıq varsa və məlumat eynidirsə yazma
    str_chat_id = str(chat_id)
    existing = groups.get(str_chat_id, {})
    
    groups[str_chat_id] = {
        'title': title,
        'added_at': existing.get('added_at'),
        'member_count': member_count if member_count is not None else existing.get('member_count'),
        'link': link if link else existing.get('link')
    }
    
    try:
        with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
            json.dump(groups, f, ensure_ascii=False, indent=4)
            # print(f"✅ Qrup yadda saxlanıldı: {title}")  # Log spam-ı azaltmaq üçün disabled
    except Exception as e:
        print(f"Qrup saxlanılarkən xəta: {e}")

def remove_group(chat_id):
    """Qrupu yaddaşdan sil"""
    groups = load_groups()
    str_chat_id = str(chat_id)
    
    if str_chat_id in groups:
        title = groups[str_chat_id].get('title', 'Naməlum')
        del groups[str_chat_id]
        
        try:
            with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
                json.dump(groups, f, ensure_ascii=False, indent=4)
                print(f"⚠️ Qrup silindi: {title} ({chat_id})")
        except Exception as e:
            print(f"Qrup silinərkən xəta: {e}")
