# ============================================================
# BGАлтернатива - Преработване на статии с Groq API (безплатен)
# ============================================================

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
import json
import re

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Ти си редактор на BGАлтернатива - сайт за политически и геополитически новини.

Правила:
- Преработи статията на БЪЛГАРСКИ ЕЗИК
- Запази фактите, използвай свои думи
- Тон: информативен, критичен, аналитичен
- НЕ копирай директно от оригинала
- Дължина: 250-400 думи
- Отговори САМО с JSON без никакъв друг текст:
{"title": "заглавието", "content": "<p>параграф 1</p><p>параграф 2</p>"}"""


def clean_json(text):
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            if "{" in part:
                text = part
                if text.startswith("json"):
                    text = text[4:]
                break
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > 0:
        text = text[start:end]
    return text


def rewrite_article(article: dict) -> dict:
    lang_note = "Статията е на английски - преведи и преработи на български." if article.get("lang") == "en" else ""

    user_message = f"""Заглавие: {article['title']}
Източник: {article['source']}
Категория: {article['category']}
{lang_note}

Текст:
{article['content'][:2000]}"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1024,
            temperature=0.7,
        )

        text = response.choices[0].message.content
        text = clean_json(text)
        result = json.loads(text)
        result["original_url"] = article["url"]
        result["source"] = article["source"]
        result["category"] = article["category"]
        return result

    except Exception as e:
        print(f"    Грешка при преработване: {e}")
        return None


def rewrite_analysis(article: dict) -> dict:
    user_message = f"""Напиши задълбочен анализ на тази тема за BGАлтернатива.
Заглавие: {article['title']}

Текст:
{article['content'][:3000]}

Структура:
- Провокативно заглавие
- Контекст (150 думи)
- Анализ (200 думи)
- Значение за България/Европа (100 думи)

Отговори САМО с JSON: {{"title": "...", "content": "<p>...</p>"}}"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=1500,
            temperature=0.8,
        )

        text = response.choices[0].message.content
        text = clean_json(text)
        result = json.loads(text)
        result["original_url"] = article["url"]
        result["source"] = article["source"]
        result["category"] = "Анализи"
        return result

    except Exception as e:
        print(f"    Грешка при анализ: {e}")
        return None
