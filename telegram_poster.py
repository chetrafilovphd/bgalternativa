# ============================================================
# BGАлтернатива - Telegram автоматизация
# Публикува нови WP постове в Telegram канал с насърчаване на дискусия
# ============================================================

import os
import re
import json
import html
import time
import random
import requests
import sys

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

WP_URL = "https://bgalternativanews.eu"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "")  # @bgalternativa или -100xxx (ID)

SEEN_FILE = "seen_telegram.json"

# Емоджита за категории (визуална навигация)
CATEGORY_EMOJI = {
    "България": "🇧🇬",
    "Свят": "🌍",
    "Геополитика": "♟",
    "Анализи": "📊",
    "Политика": "🏛",
    "Видео": "📺",
}

# Хаштаг карта (български → латински за Telegram навигация)
CATEGORY_HASHTAG = {
    "България": "Bulgaria",
    "Свят": "World",
    "Геополитика": "Geopolitics",
    "Анализи": "Analysis",
    "Политика": "Politics",
    "Видео": "Video",
}

# Провокативни въпроси за насърчаване на дискусия
DISCUSSION_PROMPTS = [
    "💬 А вие какво мислите по темата? Споделете в коментарите.",
    "💬 Как ще се отрази това на България? Кажете мнението си.",
    "💬 Изненадан ли сте от тези събития? Дискутирайте с нас.",
    "💬 Какъв е вашият анализ? Очакваме коментарите ви.",
    "💬 Каква би била правилната реакция? Споделете гледната си точка.",
    "💬 Какво следва според вас? Дискусията е отворена.",
    "💬 Какво пропускат другите медии по темата? Споделете.",
]


def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen[-500:], f)


def fetch_new_posts(limit=10):
    """Взима последните постове от WP REST API."""
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/posts",
        params={
            "per_page": limit,
            "_embed": "true",
            "status": "publish",
            "orderby": "date",
            "order": "desc",
        },
        timeout=20,
    )
    return r.json() if r.status_code == 200 else []


def get_category_name(post):
    """Извлича името на първата категория от _embedded данни."""
    embedded = post.get("_embedded", {})
    terms = embedded.get("wp:term", [])
    for tax_terms in terms:
        for t in tax_terms:
            if t.get("taxonomy") == "category" and t.get("name"):
                return t["name"]
    return ""


def get_excerpt(post):
    """Извлича meta description или excerpt."""
    # Опит 1: rank_math_description
    meta = post.get("meta", {})
    if meta.get("rank_math_description"):
        return meta["rank_math_description"]
    # Опит 2: excerpt поле
    excerpt = post.get("excerpt", {}).get("rendered", "")
    excerpt = re.sub(r"<[^>]+>", "", excerpt).strip()
    excerpt = re.sub(r"\s+", " ", excerpt)
    if excerpt and len(excerpt) > 30:
        return excerpt[:200]
    # Опит 3: първите 200 символа от content
    content = post.get("content", {}).get("rendered", "")
    content = re.sub(r"<[^>]+>", "", content).strip()
    content = re.sub(r"\s+", " ", content)
    return content[:200] if content else ""


def get_featured_image(post):
    embedded = post.get("_embedded", {})
    media = embedded.get("wp:featuredmedia", [])
    if media and isinstance(media, list):
        return media[0].get("source_url", "")
    return ""


def format_message(post):
    """Форматира пост за Telegram."""
    title = html.unescape(post["title"]["rendered"])
    title = re.sub(r"<[^>]+>", "", title)

    excerpt = get_excerpt(post)
    excerpt = html.unescape(excerpt)
    excerpt = re.sub(r"<[^>]+>", "", excerpt)

    category = get_category_name(post)
    emoji = CATEGORY_EMOJI.get(category, "📰")
    hashtag = CATEGORY_HASHTAG.get(category, "News")

    link = post["link"]
    discussion = random.choice(DISCUSSION_PROMPTS)

    # Telegram HTML formatting
    msg = f"<b>{emoji} {title}</b>\n\n"
    if excerpt:
        # Подсигуряваме че excerpt не повтаря title
        if title.lower() not in excerpt.lower():
            msg += f"{excerpt}\n\n"
    msg += f"{discussion}\n\n"
    msg += f'🔗 <a href="{link}">Прочети повече</a>\n\n'
    msg += f"#BGАлтернатива #{hashtag}"

    return msg


def send_to_telegram(message: str, photo_url: str = ""):
    """Пуска съобщение в Telegram канал."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL:
        print("✗ Липсват TELEGRAM_BOT_TOKEN или TELEGRAM_CHANNEL")
        return False

    base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    if photo_url:
        # sendPhoto с caption (HTML)
        # Telegram caption лимит = 1024 символа
        caption = message[:1020] + "..." if len(message) > 1024 else message
        r = requests.post(
            f"{base}/sendPhoto",
            json={
                "chat_id": TELEGRAM_CHANNEL,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": "HTML",
            },
            timeout=30,
        )
    else:
        r = requests.post(
            f"{base}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHANNEL,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=30,
        )

    if r.status_code == 200:
        return True
    print(f"  ✗ Telegram грешка: {r.status_code} - {r.text[:200]}")
    return False


def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL:
        print("ГРЕШКА: Задайте TELEGRAM_BOT_TOKEN и TELEGRAM_CHANNEL env vars.")
        sys.exit(1)

    print(f"Канал: {TELEGRAM_CHANNEL}")
    seen = load_seen()
    posts = fetch_new_posts(limit=10)
    print(f"Последни постове: {len(posts)}")

    new_count = 0
    for post in reversed(posts):  # oldest first → запазва хронологията
        post_id = post["id"]
        if post_id in seen:
            continue

        title = re.sub(r"<[^>]+>", "", post["title"]["rendered"])[:60]
        print(f"  → Изпращам: {title}")

        msg = format_message(post)
        photo = get_featured_image(post)

        if send_to_telegram(msg, photo):
            print(f"  ✓ Изпратено")
            seen.append(post_id)
            new_count += 1
            time.sleep(2)  # Не претовареваме Telegram API
        else:
            print(f"  ✗ Неуспешно")

    save_seen(seen)
    print(f"\n=== ИЗПРАТЕНИ {new_count} нови ===")


if __name__ == "__main__":
    main()
