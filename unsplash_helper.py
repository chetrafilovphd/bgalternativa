# ============================================================
# BGАлтернатива - Unsplash API интеграция за featured images
# ============================================================

import os
import re
import requests
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

_groq_client = None


def _get_groq():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


# Фолбек keyword map — ако Groq не е наличен
CATEGORY_FALLBACK = {
    "България": "Bulgaria Sofia politics",
    "Свят": "world news global",
    "Политика": "politics parliament government",
    "Геополитика": "geopolitics diplomacy flags",
    "Анализи": "analysis politics discussion",
    "Видео": "television broadcast studio",
}


def extract_english_keywords(title: str, category: str) -> str:
    """Използва Groq да извлече 3-4 английски ключови думи за Unsplash."""
    try:
        client = _get_groq()
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Extract 3-4 English keywords for Unsplash image search from the news headline. Reply with ONLY the keywords separated by spaces, no punctuation, no quotes. Prefer concrete nouns (country names, objects, people types, events). Avoid abstract words."
                },
                {
                    "role": "user",
                    "content": f"Headline: {title}\nCategory: {category}"
                }
            ],
            max_tokens=30,
            temperature=0.3,
        )
        kw = resp.choices[0].message.content.strip()
        kw = re.sub(r'[^\w\s]', '', kw)
        if kw and len(kw.split()) >= 2:
            return kw
    except Exception as e:
        print(f"    ⚠ Groq keyword error: {e}")
    return CATEGORY_FALLBACK.get(category, "news journalism")


def search_unsplash(query: str):
    """Търси снимка в Unsplash. Връща dict или None."""
    if not UNSPLASH_ACCESS_KEY:
        return None
    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": query,
                "per_page": 3,
                "orientation": "landscape",
                "content_filter": "high",
            },
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            timeout=15,
        )
        if r.status_code == 403:
            # Rate limit hit
            remaining = r.headers.get("X-Ratelimit-Remaining", "?")
            print(f"    ⚠ Unsplash rate limit (remaining: {remaining})")
            return {"_rate_limited": True}
        if r.status_code != 200:
            print(f"    ⚠ Unsplash status {r.status_code}: {r.text[:150]}")
            return None
        data = r.json()
        results = data.get("results", [])
        if not results:
            return None
        # Вземи първата
        photo = results[0]
        # Отбележи download (изискване на Unsplash API guidelines)
        download_loc = photo.get("links", {}).get("download_location")
        if download_loc:
            try:
                requests.get(
                    download_loc,
                    headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
                    timeout=10,
                )
            except Exception:
                pass
        return {
            "url": photo["urls"]["regular"],  # ~1080px широко
            "download_url": photo["urls"]["full"],
            "author_name": photo["user"]["name"],
            "author_link": photo["user"]["links"]["html"] + "?utm_source=bgalternativa&utm_medium=referral",
            "unsplash_link": photo["links"]["html"] + "?utm_source=bgalternativa&utm_medium=referral",
            "description": photo.get("description") or photo.get("alt_description") or "",
        }
    except Exception as e:
        print(f"    ⚠ Unsplash error: {e}")
        return None


def search_pexels(query: str):
    """Търси снимка в Pexels. Връща dict или None."""
    if not PEXELS_API_KEY:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            headers={"Authorization": PEXELS_API_KEY},
            timeout=15,
        )
        if r.status_code == 429:
            print(f"    ⚠ Pexels rate limit")
            return {"_rate_limited": True}
        if r.status_code != 200:
            print(f"    ⚠ Pexels status {r.status_code}: {r.text[:150]}")
            return None
        data = r.json()
        photos = data.get("photos", [])
        if not photos:
            return None
        photo = photos[0]
        return {
            "url": photo["src"]["large"],
            "download_url": photo["src"]["original"],
            "author_name": photo["photographer"],
            "author_link": photo["photographer_url"],
            "unsplash_link": photo["url"],  # reusing key name for compatibility
            "description": photo.get("alt") or "",
            "_source": "Pexels",
        }
    except Exception as e:
        print(f"    ⚠ Pexels error: {e}")
        return None


def get_image_for_article(title: str, category: str):
    """High-level: извлича keywords и търси снимка в Unsplash, fallback към Pexels."""
    query = extract_english_keywords(title, category)
    photo = search_unsplash(query)

    # Ако Unsplash има rate limit или няма резултат → Pexels
    if not photo or photo.get("_rate_limited") or not photo.get("url"):
        pexels_photo = search_pexels(query)
        if pexels_photo and not pexels_photo.get("_rate_limited"):
            return pexels_photo, query
        # И Pexels е изчерпан - пробвай fallback query
        if photo and photo.get("_rate_limited"):
            return photo, query  # връщаме rate_limited маркер

    if not photo:
        # Фолбек към категорийните ключови думи
        photo = search_unsplash(CATEGORY_FALLBACK.get(category, "news"))
        if not photo or not photo.get("url"):
            photo = search_pexels(CATEGORY_FALLBACK.get(category, "news"))
    return photo, query


def unsplash_credit_html(photo: dict) -> str:
    """Attribution линк за Unsplash/Pexels."""
    source = photo.get("_source", "Unsplash")
    return (
        f'<p><small>Снимка: <a href="{photo["author_link"]}" target="_blank" rel="nofollow">'
        f'{photo["author_name"]}</a> / <a href="{photo["unsplash_link"]}" target="_blank" rel="nofollow">{source}</a></small></p>'
    )


if __name__ == "__main__":
    # Тест
    import sys
    sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
    test_title = "Пеевски гласува в родопско село за държавата на хората"
    test_category = "България"
    photo, query = get_image_for_article(test_title, test_category)
    if photo:
        print(f"Query: {query}")
        print(f"URL: {photo['url']}")
        print(f"Author: {photo['author_name']}")
        print(f"Description: {photo['description'][:100]}")
    else:
        print("No image found")
