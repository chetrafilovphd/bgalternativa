# ============================================================
# BGАлтернатива - Преработване на статии с Groq API (безплатен)
# ============================================================

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
import json
import re

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Ти си редактор на информационна платформа за българска аудитория.

ВАЖНИ правила за писане:
- Пиши на ЧИСТ БЪЛГАРСКИ ЕЗИК — както говори средностатистическият образован българин
- Не използвай транслитерирани чужди думи като: инбокс (→ поща), канава (→ платно), дедлайн (→ срок), фийдбек (→ обратна връзка), ъпдейт (→ обновяване), челендж (→ предизвикателство)
- Не започвай с клишета: "В заключение", "В крайна сметка", "В днешния бързо развиващ се свят", "Важно е да се отбележи", "Струва си да"
- Избягвай помпозни AI фрази: "постоянно развиващ се", "динамичен пейзаж", "безпрецедентен", "съществено значение"
- Използвай кратки, ясни изречения — български новинарски стил
- Тон: неутрален, фактологичен, без дидактика
- Запази фактите, използвай свои думи
- Дължина: 180-300 думи
- Ако е анализ — спокоен, без емоционална реторика

Отговори САМО с JSON без никакъв друг текст:
{"title": "заглавието", "content": "<p>параграф 1</p><p>параграф 2</p>", "seo_title": "50-60 символа SEO заглавие за Google търсачката (различно от title - по-кратко, с ключови думи)", "meta_description": "кратко 140-155 символа SEO описание за Google", "excerpt": "едно изречение кратко резюме"}"""


# Списък с чувствителни имена — ако се срещне, статията отива в "Draft" за ръчен преглед
SENSITIVE_NAMES = [
    # Български политици (настоящи и бивши)
    "Бойко Борисов", "Борисов",
    "Кирил Петков",
    "Асен Василев",
    "Делян Пеевски", "Пеевски",
    "Корнелия Нинова",
    "Костадин Костадинов", "Копейкин",
    "Волен Сидеров",
    "Слави Трифонов",
    "Росен Плевнелиев",
    "Румен Радев",
    "Стефан Янев",
    "Николай Денков",
    "Мария Габриел",
    "Атанас Атанасов",
    "Христо Иванов",
    "Деница Сачева",
    "Тошко Йорданов",
    "Васил Божков",
    # Бизнес
    "Иво Прокопиев",
    "Цветелина Бориславова",
    "Гриша Ганчев",
    "Васил Божков",
    # Съд / институции
    "Иван Гешев",
    "Сотир Цацаров",
    "Борислав Сарафов",
]


def contains_sensitive(text: str) -> list:
    """Връща списък с открити чувствителни имена."""
    found = []
    text_lower = text.lower()
    for name in SENSITIVE_NAMES:
        if name.lower() in text_lower:
            found.append(name)
    return list(set(found))


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


def _extract_meta(content_html: str) -> str:
    """Fallback: ако липсва meta_description, извлича първите 155 символа от съдържанието."""
    text = re.sub(r"<[^>]+>", "", content_html or "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 155:
        return text[:152].rsplit(" ", 1)[0] + "..."
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

        # Чувствителни имена → маркираме като draft за ръчен преглед
        combined_text = result.get("title", "") + " " + result.get("content", "")
        flagged = contains_sensitive(combined_text)
        if flagged:
            result["status"] = "draft"
            result["sensitive_names"] = flagged
            print(f"    ⚠ Чувствителни имена: {flagged} → DRAFT")

        # Гарантираме meta_description
        if not result.get("meta_description"):
            result["meta_description"] = _extract_meta(result.get("content", ""))
        result["meta_description"] = result["meta_description"][:155]

        # SEO title — fallback към article title ако липсва
        if not result.get("seo_title"):
            result["seo_title"] = result.get("title", "")[:60]
        result["seo_title"] = result["seo_title"][:60]

        result["original_url"] = article["url"]
        result["source"] = article["source"]
        result["category"] = article["category"]
        result["image_url"] = article.get("image_url", "")
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

Отговори САМО с JSON: {{"title": "...", "content": "<p>...</p>", "seo_title": "50-60 символа SEO заглавие", "meta_description": "140-155 символа SEO описание", "excerpt": "едно изречение резюме"}}"""

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

        combined_text = result.get("title", "") + " " + result.get("content", "")
        flagged = contains_sensitive(combined_text)
        if flagged:
            result["status"] = "draft"
            result["sensitive_names"] = flagged
            print(f"    ⚠ Чувствителни имена (анализ): {flagged} → DRAFT")

        if not result.get("meta_description"):
            result["meta_description"] = _extract_meta(result.get("content", ""))
        result["meta_description"] = result["meta_description"][:155]

        if not result.get("seo_title"):
            result["seo_title"] = result.get("title", "")[:60]
        result["seo_title"] = result["seo_title"][:60]

        result["original_url"] = article["url"]
        result["source"] = article["source"]
        result["category"] = "Анализи"
        result["image_url"] = article.get("image_url", "")
        return result

    except Exception as e:
        print(f"    Грешка при анализ: {e}")
        return None
