# -*- coding: utf-8 -*-

import random
import time
from datetime import datetime, timedelta

import settings


# -------------------------------------------------
# USER
# -------------------------------------------------

class User:
    def __init__(self, user_id, username):
        self.user_id: int = user_id
        self.username: str = username
        self.rating = 0

    def update_rating(self):
        self.rating += 1

    def get_rating(self):
        return self.rating

    def get_rating_str(self):
        return self.username + ": " + str(self.rating) + "\n"


# -------------------------------------------------
# GAME
# -------------------------------------------------

class Game:
    def __init__(self):
        self._master_user_id = 0
        self._word_list = []
        self._current_word = ''
        self._game_started = False
        self._users = {}
        self.winner = 0
        self._master_start_time: datetime = datetime.now()
        self.timedelta = 60

        # 🔒 Kelime değiştirme limiti
        self.max_word_changes = 3
        self.word_change_count = 0
        self._last_activity_time = datetime.now()

    def update_activity(self):
        self._last_activity_time = datetime.now()

    def is_inactive(self, minutes=15):
        if not self._game_started:
            return False
        return (datetime.now() - self._last_activity_time) > timedelta(seconds=minutes*60)

    def stop(self):
        self._game_started = False

    # -------------------------------------------------
    # GAME FLOW
    # -------------------------------------------------

    def start(self, word_type='words'):
        """
        Oyunu başlat
        word_type: 'words' (sözlər) və ya 'names' (insan adları)
        """
        if word_type == 'names':
            self._word_list = settings.names_list.copy()
        else:
            self._word_list = settings.words_list.copy()
        
        self._word_type = word_type
        self._master_user_id = 0
        self._game_started = True
        self._users = {}
        self.winner = 0
        self._current_word = ''
        self._master_start_time = datetime.now()
        self.word_change_count = 0
        self._last_activity_time = datetime.now()

    def is_game_started(self):
        return self._game_started

    # -------------------------------------------------
    # MASTER TIME
    # -------------------------------------------------

    def get_master_time_left(self) -> int:
        return self.timedelta - (datetime.now() - self._master_start_time).seconds

    def is_master_time_left(self):
        return (datetime.now() - self._master_start_time).seconds >= self.timedelta

    # -------------------------------------------------
    # MASTER
    # -------------------------------------------------

    def set_master(self, user_id):
        self._create_word()
        self._master_user_id = user_id
        self._master_start_time = datetime.now()
        self.update_activity()

        # 🔄 Yeni master → haklar sıfırlanır
        self.word_change_count = 0

    def is_master(self, user_id: int):
        return user_id == self._master_user_id

    # -------------------------------------------------
    # WORD
    # -------------------------------------------------

    def _create_word(self):
        if not self._word_list:
            # Siyahı bitibsə yenidən doldur
            if hasattr(self, '_word_type') and self._word_type == 'names':
                self._word_list = settings.names_list.copy()
            else:
                self._word_list = settings.words_list.copy()

        self._current_word = random.choice(self._word_list)
        del self._word_list[self._word_list.index(self._current_word)]

    def get_word(self, user_id: int):
        if self.is_master(user_id):
            self.update_activity()
            return self._current_word
        else:
            return ''

    def change_word(self, user_id: int):
        if not self.is_master(user_id):
            return ''

        # 🔒 3 hak sınırı
        if self.word_change_count >= self.max_word_changes:
            return ''

        self.word_change_count += 1
        self._create_word()
        self.update_activity()
        return self._current_word

    def get_word_change_left(self):
        return self.max_word_changes - self.word_change_count

    def get_current_word(self):
        return self._current_word

    # -------------------------------------------------
    # ANSWER
    # -------------------------------------------------

    def is_word_answered(self, user_id, text):
        if not self.is_master(user_id):
            if text.lower() == self._current_word.lower():
                self._master_user_id = user_id
                self.winner = user_id
                self.update_activity()
                return True
        else:
            # Səhv cavab da aktivlik sayılır
            self.update_activity()
        return False

    # -------------------------------------------------
    # RATING
    # -------------------------------------------------

    def update_rating(self, user_id, username):
        if user_id not in self._users:
            self._users[user_id] = User(user_id, username)

        self._users[user_id].update_rating()

    def get_str_rating(self):
        rating_str = ''
        for user_id in self._users:
            rating_str += self._users[user_id].get_rating_str()

        return rating_str
