# -*- coding: utf-8 -*-
"""
Track My Chat Member Handler
Bot qruplara əlavə olunanda/çıxarılanda izləmək üçün
"""

async def track_my_chat_member(update, context):
    """Bot qruplara əlavə/çıxarış izləmə"""
    import groups
    
    result = update.my_chat_member
    chat = result.chat
    
    # Yalnız qrup və supergroupları izlə
    if chat.type not in ["group", "supergroup"]:
        return
    
    new_member = result.new_chat_member
    old_member = result.old_chat_member
    
    # Bot qrupa əlavə olundu
    if old_member.status in ["left", "kicked"] and new_member.status in ["member", "administrator"]:
        print(f"✅ Bot qrupa əlavə olundu: {chat.title} ({chat.id})")
        groups.save_group(chat.id, chat.title)
    
    # Bot qrupdan çıxarıldı
    elif old_member.status in ["member", "administrator"] and new_member.status in ["left", "kicked"]:
        print(f"⚠️ Bot qrupdan çıxarıldı: {chat.title} ({chat.id})")
        groups.remove_group(chat.id)
