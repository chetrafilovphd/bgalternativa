# ============================================================
# BGАлтернатива - RSS Скрейпър
# ============================================================

import feedparser
import hashlib
import json
import os
from datetime import datetime, timedelta
from config import RSS_SOURCES

SEEN_FILE = "seen_articles.json"


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen[-500:], f)  # Пазим само последните 500


def article_id(url):
    return hashlib.md5(url.encode()).hexdigest()


def fetch_articles(category, limit=10):
    seen = load_seen()
    sources = RSS_SOURCES.get(category, [])
    articles = []

    for source in sources:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:5]:
                uid = article_id(entry.get("link", ""))
                if uid in seen:
                    continue

                # Вземи текста
                content = ""
                if hasattr(entry, "summary"):
                    content = entry.summary
                elif hasattr(entry, "content"):
                    content = entry.content[0].value

                import re

                # Извлечи изображение ПРЕДИ да изчистиш HTML
                image_url = ""
                # 1. media:thumbnail / media:content
                if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                    image_url = entry.media_thumbnail[0].get("url", "")
                elif hasattr(entry, "media_content") and entry.media_content:
                    image_url = entry.media_content[0].get("url", "")
                # 2. enclosures (RSS 2.0)
                elif hasattr(entry, "enclosures") and entry.enclosures:
                    for enc in entry.enclosures:
                        if "image" in enc.get("type", ""):
                            image_url = enc.get("href", "") or enc.get("url", "")
                            break
                # 3. Първо <img> в съдържанието
                if not image_url:
                    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
                    if img_match:
                        image_url = img_match.group(1)

                # Почисти HTML тагове
                content = re.sub(r"<[^>]+>", "", content).strip()

                if len(content) < 100:
                    continue

                articles.append({
                    "uid": uid,
                    "title": entry.get("title", ""),
                    "content": content,
                    "url": entry.get("link", ""),
                    "source": source["name"],
                    "lang": source["lang"],
                    "category": category,
                    "published": entry.get("published", str(datetime.now())),
                    "image_url": image_url,
                })

                if len(articles) >= limit:
                    break

        except Exception as e:
            print(f"Грешка при {source['name']}: {e}")

        if len(articles) >= limit:
            break

    # Маркирай като видени
    new_seen = seen + [a["uid"] for a in articles]
    save_seen(new_seen)

    return articles


def fetch_all(limits: dict) -> dict:
    result = {}
    for category, limit in limits.items():
        print(f"Скрейпвам {category}...")
        result[category] = fetch_articles(category, limit)
        print(f"  → {len(result[category])} нови статии")
    return result
