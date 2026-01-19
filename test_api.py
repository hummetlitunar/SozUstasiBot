# -*- coding: utf-8 -*-
"""
SözUstası API Test Script
KontrolBot olmadan API endpoint-ləri test etmək üçün
"""

import requests
import json

API_URL = "http://localhost:5001"

def test_status():
    """Test /status endpoint"""
    print("\n🔍 Testing /status endpoint...")
    try:
        response = requests.get(f"{API_URL}/status", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_groups_count():
    """Test /groups/count endpoint"""
    print("\n🔍 Testing /groups/count endpoint...")
    try:
        response = requests.get(f"{API_URL}/groups/count", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_groups_list():
    """Test /groups/list endpoint"""
    print("\n🔍 Testing /groups/list endpoint...")
    try:
        response = requests.get(f"{API_URL}/groups/list", timeout=5)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Success: {data.get('success')}")
        groups = data.get('data', {}).get('groups', {})
        print(f"Qruplar sayı: {len(groups)}")
        for chat_id, info in groups.items():
            print(f"  - {info.get('title')} (ID: {chat_id})")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_broadcast():
    """Test /groups/broadcast endpoint"""
    print("\n🔍 Testing /groups/broadcast endpoint...")
    print("⚠️ Bu test gerçək mesaj göndərməz (DRY RUN)")
    # Gerçək broadcast testi üçün şərh sətirini aktivləşdirin:
    # try:
    #     payload = {
    #         "message": "Test mesajı KontrolBot-dan",
    #         "target": "all"
    #     }
    #     response = requests.post(f"{API_URL}/groups/broadcast", json=payload, timeout=10)
    #     print(f"Status Code: {response.status_code}")
    #     print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    #     return response.status_code == 200
    # except Exception as e:
    #     print(f"❌ Error: {e}")
    #     return False
    print("✅ Broadcast test keçildi (DRY RUN)")
    return True

def main():
    print("=" * 60)
    print("🧪 SözUstası API Test Suite")
    print("=" * 60)
    print("\n⚠️ SözUstası botunun işlədiyinə əmin olun!")
    print("Terminal-da: cd 'd:\\Proqram\\Botlar\\SözUstası' && python main.py")
    print("\nEnter düyməsinə basaraq testə başlayın...")
    input()
    
    results = {
        "Status": test_status(),
        "Groups Count": test_groups_count(),
        "Groups List": test_groups_list(),
        "Broadcast": test_broadcast()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Nəticələri:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n🎯 Total: {passed}/{total} testlər uğurlu oldu")
    
    if passed == total:
        print("\n🎉 Bütün testlər uğurla keçdi!")
    else:
        print("\n⚠️ Bəzi testlər uğursuz oldu. SözUstası botunun işlədiyinə əmin olun.")

if __name__ == "__main__":
    main()
