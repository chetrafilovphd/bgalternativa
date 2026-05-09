# ============================================================
# BGАлтернатива - Автоматични анкети в Telegram
# - 18:00 дневна анкета (тема на деня)
# - 19:00 неделя седмична анкета (общ въпрос)
# - Tечни poll-ове базирани на новини
# ============================================================

import os
import re
import json
import html
import random
import requests
import sys
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from groq import Groq

WP_URL = "https://bgalternativanews.eu"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "")
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
groq = Groq(api_key=GROQ_KEY)

POLL_TYPE = os.environ.get("POLL_TYPE", "daily")  # daily | weekly | breaking


def fetch_recent_posts(limit=20):
    """Взима последните публикации."""
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/posts",
        params={"per_page": limit, "_embed": "true", "orderby": "date", "order": "desc"},
        timeout=20,
    )
    return r.json() if r.status_code == 200 else []


def filter_today(posts):
    """Само днешните публикации."""
    today = datetime.now(timezone.utc).date()
    return [
        p for p in posts
        if datetime.fromisoformat(p["date_gmt"].replace("Z", "+00:00")).date() == today
    ]


def filter_this_week(posts):
    week_start = datetime.now(timezone.utc) - timedelta(days=7)
    return [
        p for p in posts
        if datetime.fromisoformat(p["date_gmt"].replace("Z", "+00:00")) >= week_start
    ]


def pick_main_story(posts):
    """Избира най-важната статия — приоритет: Анализи, после Геополитика, после най-новата."""
    if not posts:
        return None
    # Приоритет: Анализи
    for p in posts:
        cats = []
        for tax in p.get("_embedded", {}).get("wp:term", []):
            for t in tax:
                if t.get("taxonomy") == "category":
                    cats.append(t.get("name", ""))
        if "Анализи" in cats or "Геополитика" in cats:
            return p
    # Иначе най-новата
    return posts[0]


def strip_html(html_str):
    return re.sub(r"<[^>]+>", "", html_str or "").strip()


def generate_poll(title: str, content: str, poll_type: str = "daily"):
    """Groq генерира въпрос + 4 опции на български."""
    if poll_type == "weekly":
        instruction = "седмичен анализ — въпрос за обобщение на седмицата"
    else:
        instruction = "дневен въпрос — какво мислят хората за тази тема"

    prompt = f"""Ти си модератор на новинарска платформа. Генерирай Telegram анкета на български език.

ЗАДАЧА: {instruction}

Заглавие: {title}
Съдържание: {content[:1000]}

ИЗИСКВАНИЯ:
- Въпросът: до 250 символа, неутрален, провокира мислене (НЕ "Какво мислите?")
- Опциите: 3-4 на брой, всяка до 90 символа
- Опциите трябва да са взаимноизключващи
- БЕЗ AI клишета, БЕЗ "Какво мислите?"
- Тон: разговорен, конкретен

Отговори САМО с JSON:
{{"question":"въпросът","options":["опция 1","опция 2","опция 3","опция 4"]}}"""

    try:
        r = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.6,
            response_format={"type": "json_object"},
        )
        data = json.loads(r.choices[0].message.content)
        question = data.get("question", "")[:250]
        options = [opt[:90] for opt in data.get("options", [])][:10]
        if question and len(options) >= 2:
            return question, options
    except Exception as e:
        print(f"Groq error: {e}")
    return None, None


def send_poll(question: str, options: list, intro: str = ""):
    """Изпраща Telegram poll. Незадължителен intro текст ПРЕДИ poll-а."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL:
        print("Липсва токен/канал")
        return False

    base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    # Intro съобщение (ако има)
    if intro:
        r = requests.post(
            f"{base}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHANNEL,
                "text": intro,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=20,
        )
        if r.status_code != 200:
            print(f"Intro грешка: {r.text[:200]}")

    # Самата анкета
    r = requests.post(
        f"{base}/sendPoll",
        json={
            "chat_id": TELEGRAM_CHANNEL,
            "question": question,
            "options": options,
            "is_anonymous": True,  # Telegram канали изискват анонимни
            "allows_multiple_answers": False,
        },
        timeout=20,
    )
    if r.status_code == 200:
        print(f"✓ Анкета изпратена: {question[:60]}")
        return True
    print(f"✗ Poll грешка: {r.status_code} - {r.text[:200]}")
    return False


def daily_poll():
    """Дневна анкета — взима тема на деня и пита."""
    posts = fetch_recent_posts(20)
    today_posts = filter_today(posts)
    if not today_posts:
        today_posts = posts[:5]  # fallback към последни 5
    main = pick_main_story(today_posts)
    if not main:
        print("Няма статия за анкета")
        return

    title = strip_html(main["title"]["rendered"])
    content = strip_html(main["content"]["rendered"])
    link = main["link"]

    question, options = generate_poll(title, content, "daily")
    if not question:
        return

    intro = f'<b>📊 Тема на деня</b>\n\n{title}\n\n🔗 <a href="{link}">Прочети статията</a>\n\n👇 Гласувайте:'
    send_poll(question, options, intro)


def weekly_poll():
    """Седмична анкета — обобщителен въпрос за седмицата."""
    posts = fetch_recent_posts(50)
    week_posts = filter_this_week(posts)
    if not week_posts:
        return

    # Обобщение на топ темите
    titles = [strip_html(p["title"]["rendered"]) for p in week_posts[:10]]
    summary_text = "\n".join(f"- {t}" for t in titles)

    question, options = generate_poll(
        "Обобщение на седмицата",
        f"Топ теми тази седмица:\n{summary_text}",
        "weekly",
    )
    if not question:
        return

    intro = "<b>📊 Анкета на седмицата</b>\n\nКое беше най-важното събитие тази седмица? 👇"
    send_poll(question, options, intro)


def main():
    if POLL_TYPE == "weekly":
        print("Седмична анкета...")
        weekly_poll()
    else:
        print("Дневна анкета...")
        daily_poll()


if __name__ == "__main__":
    main()
