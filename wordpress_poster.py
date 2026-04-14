# ============================================================
# BGАлтернатива - Публикуване в WordPress
# ============================================================

import requests
import base64
from config import WP_URL, WP_USERNAME, WP_APP_PASSWORD

def get_auth_header():
    token = base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def get_or_create_category(name: str) -> int:
    headers = get_auth_header()
    # Търси съществуваща
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/categories",
        params={"search": name, "per_page": 5},
        headers=headers
    )
    cats = r.json()
    for cat in cats:
        if cat["name"].lower() == name.lower():
            return cat["id"]

    # Създай нова
    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/categories",
        json={"name": name, "slug": name.lower().replace(" ", "-")},
        headers=headers
    )
    return r.json()["id"]


def post_article(article: dict) -> bool:
    headers = get_auth_header()
    headers["Content-Type"] = "application/json"

    category_id = get_or_create_category(article["category"])

    source_note = f'<p><small>Източник: <a href="{article["original_url"]}" target="_blank" rel="nofollow">{article["source"]}</a></small></p>'

    data = {
        "title": article["title"],
        "content": article["content"] + source_note,
        "status": "publish",
        "categories": [category_id],
        "format": "standard",
    }

    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        json=data,
        headers=headers
    )

    if r.status_code == 201:
        print(f"  ✓ Публикувана: {article['title'][:60]}")
        return True
    else:
        print(f"  ✗ Грешка: {r.status_code} - {r.text[:100]}")
        return False


def setup_categories(categories: list):
    print("Създавам категории...")
    for name in categories:
        cat_id = get_or_create_category(name)
        print(f"  ✓ {name} (ID: {cat_id})")
