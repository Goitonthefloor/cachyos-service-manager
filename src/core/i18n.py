"""Internationalization (i18n) support for CachyOS Service Manager."""

import gettext
import locale
import os
from pathlib import Path
from typing import Optional

# Default language
DEFAULT_LANG = 'en'
SUPPORTED_LANGUAGES = ['en', 'de']

# Translation cache
_translations = {}
_current_lang = DEFAULT_LANG


def get_locale_dir() -> Path:
    """Get the locale directory path."""
    # Look in package directory first
    package_locale = Path(__file__).parent / 'locale'
    if package_locale.exists():
        return package_locale
    
    # Fallback to system locale
    return Path('/usr/share/locale')


def get_language() -> str:
    """Get current language."""
    return _current_lang


def set_language(lang: str) -> bool:
    """Set the current language.
    
    Args:
        lang: Language code (e.g., 'en', 'de')
        
    Returns:
        True if language was set successfully
    """
    global _current_lang
    
    if lang not in SUPPORTED_LANGUAGES:
        return False
    
    _current_lang = lang
    
    # Load translation
    try:
        locale_dir = get_locale_dir()
        translation = gettext.translation(
            'cachyos-service-manager',
            localedir=locale_dir,
            languages=[lang],
            fallback=True
        )
        _translations[lang] = translation
        translation.install()
        return True
    except Exception:
        # Fallback to null translation
        _translations[lang] = gettext.NullTranslations()
        return False


def get_translation(lang: Optional[str] = None):
    """Get translation object for a language."""
    lang = lang or _current_lang
    return _translations.get(lang, gettext.NullTranslations())


def _(message: str) -> str:
    """Translate a message using current language."""
    return get_translation().gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Translate a pluralized message."""
    return get_translation().ngettext(singular, plural, n)


def init_i18n() -> str:
    """Initialize i18n based on system locale.
    
    Returns:
        The language code that was set
    """
    # Try to get language from environment
    for env_var in ['LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG']:
        env_lang = os.environ.get(env_var, '')
        if env_lang:
            # Extract language code (e.g., 'de_DE.UTF-8' -> 'de')
            lang_code = env_lang.split('_')[0].split('.')[0].lower()
            if lang_code in SUPPORTED_LANGUAGES:
                set_language(lang_code)
                return lang_code
    
    # Try system locale
    try:
        sys_lang = locale.getdefaultlocale()[0]
        if sys_lang:
            lang_code = sys_lang.split('_')[0].lower()
            if lang_code in SUPPORTED_LANGUAGES:
                set_language(lang_code)
                return lang_code
    except Exception:
        pass
    
    # Default to English
    set_language(DEFAULT_LANG)
    return DEFAULT_LANG


class I18nMixin:
    """Mixin class to add i18n support to classes."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lang = get_language()
    
    def tr(self, message: str) -> str:
        """Translate a message."""
        return get_translation(self._lang).gettext(message)
    
    def trn(self, singular: str, plural: str, n: int) -> str:
        """Translate a pluralized message."""
        return get_translation(self._lang).ngettext(singular, plural, n)


# Initialize on import
init_i18n()