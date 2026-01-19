# -*- coding: utf-8 -*-
TOKEN = "5465975914:AAECix-Ani6-klO37Ru-0OzcU5EyepSkAB8"

# Sözlər siyahısı
with open('words.txt', 'r', encoding='utf-8') as file:
    words_list = file.read().splitlines()

# İnsan adları siyahısı
with open('adlar.txt', 'r', encoding='utf-8') as file:
    names_list = file.read().splitlines()

# Default (geriye uygunluk üçün)
word_list = words_list

# API Server Configuration
API_PORT = 5001
