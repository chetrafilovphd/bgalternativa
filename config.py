# ============================================================
# BGАлтернатива - Конфигурация
# ============================================================

# Groq API (безплатен) - чете от environment variables
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"

# WordPress - чете от environment variables
WP_URL = "https://bgalternativanews.eu"
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")

# Брой статии на ден
ARTICLES_PER_DAY = 20
ARTICLES_SCHEDULE = {
    "България": 7,
    "Свят": 7,
    "Геополитика": 3,
    "Анализи": 3,
}

# RSS източници - тествани и работещи
RSS_SOURCES = {
    "България": [
        {"name": "24 Часа", "url": "https://www.24chasa.bg/rss", "lang": "bg"},
        {"name": "Дневник", "url": "https://www.dnevnik.bg/rss/?rubric=bulgaria", "lang": "bg"},
        {"name": "Монитор", "url": "https://www.monitor.bg/rss", "lang": "bg"},
    ],
    "Свят": [
        {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "lang": "en"},
        {"name": "DW World", "url": "https://rss.dw.com/rdf/rss-en-world", "lang": "en"},
        {"name": "Дневник Свят", "url": "https://www.dnevnik.bg/rss/", "lang": "bg"},
    ],
    "Геополитика": [
        {"name": "DW Europe", "url": "https://rss.dw.com/rdf/rss-en-eu", "lang": "en"},
        {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "lang": "en"},
        {"name": "24 Часа", "url": "https://www.24chasa.bg/rss", "lang": "bg"},
    ],
    "Анализи": [
        {"name": "Дневник", "url": "https://www.dnevnik.bg/rss/", "lang": "bg"},
        {"name": "DW World", "url": "https://rss.dw.com/rdf/rss-en-world", "lang": "en"},
    ],
}

# YouTube канал
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@bgalternativa"
YOUTUBE_CHANNEL_ID = "UC0pRhrzNkBkoNcWNXVUnTAw"

# WordPress категории (ще се създадат автоматично)
WP_CATEGORIES = [
    "България",
    "Свят",
    "Политика",
    "Геополитика",
    "Анализи",
    "Видео",
]
