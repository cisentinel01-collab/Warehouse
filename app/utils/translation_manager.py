import json
import os
from typing import Dict
from app.config.settings import settings

class TranslationManager:
    _instance = None
    _translations: Dict[str, Dict[str, str]] = {}
    _current_lang = settings.DEFAULT_LANGUAGE

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranslationManager, cls).__new__(cls)
            cls._instance._load_translations()
        return cls._instance

    def _load_translations(self):
        trans_dir = "app/translations"
        for lang in ['ar', 'en']:
            path = os.path.join(trans_dir, f"{lang}.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self._translations[lang] = json.load(f)

    def set_language(self, lang: str):
        if lang in self._translations:
            self._current_lang = lang

    def get_text(self, key: str) -> str:
        return self._translations.get(self._current_lang, {}).get(key, key)

    @property
    def current_language(self):
        return self._current_lang

tr = TranslationManager()
