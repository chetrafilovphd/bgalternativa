# ============================================================
# BGАлтернатива - Публикуване в WordPress
# ============================================================

import requests
import base64
import mimetypes
import os
from urllib.parse import urlparse, unquote
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


def article_exists(title: str) -> bool:
    headers = get_auth_header()
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/posts",
        params={"search": title[:50], "per_page": 5},
        headers=headers
    )
    posts = r.json()
    for post in posts:
        if post["title"]["rendered"].lower().strip() == title.lower().strip():
            return True
    return False


def upload_media_from_url(image_url: str) -> int:
    """Сваля изображение от URL и го качва в WordPress Media Library."""
    if not image_url:
        return 0
    try:
        img_resp = requests.get(image_url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0"
        })
        if img_resp.status_code != 200 or len(img_resp.content) < 1000:
            return 0

        # Определи име на файла и mime
        path = urlparse(image_url).path
        filename = unquote(os.path.basename(path)) or "image.jpg"
        # Подсигури валидно разширение
        mime = img_resp.headers.get("Content-Type", "").split(";")[0].strip()
        if not mime or "image" not in mime:
            mime = mimetypes.guess_type(filename)[0] or "image/jpeg"
        ext_map = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}
        if not any(filename.lower().endswith(e) for e in [".jpg", ".jpeg", ".png", ".webp", ".gif"]):
            filename += ext_map.get(mime, ".jpg")

        upload_headers = get_auth_header()
        upload_headers["Content-Type"] = mime
        upload_headers["Content-Disposition"] = f'attachment; filename="{filename}"'

        r = requests.post(
            f"{WP_URL}/wp-json/wp/v2/media",
            data=img_resp.content,
            headers=upload_headers,
            timeout=30,
        )
        if r.status_code in (200, 201):
            return r.json().get("id", 0)
    except Exception as e:
        print(f"    ⚠ Грешка при качване на снимка: {e}")
    return 0


def post_article(article: dict) -> bool:
    headers = get_auth_header()
    headers["Content-Type"] = "application/json"

    if article_exists(article["title"]):
        print(f"  → Пропусната (дублат): {article['title'][:60]}")
        return False

    category_id = get_or_create_category(article["category"])

    # Взимаме featured image от Unsplash/Pexels (безопасно за копирайт)
    from unsplash_helper import get_image_for_article, unsplash_credit_html
    media_id = 0
    photo_credit = ""
    photo, _ = get_image_for_article(article["title"], article["category"])
    if photo and photo.get("url"):
        media_id = upload_media_from_url(photo["url"])
        if media_id:
            print(f"    ✓ Снимка от {photo.get('_source', 'Unsplash')} (ID: {media_id})")
            photo_credit = unsplash_credit_html(photo)

    source_note = f'<p><small>Източник: <a href="{article["original_url"]}" target="_blank" rel="nofollow">{article["source"]}</a></small></p>'

    # Статии с чувствителни имена → DRAFT за ръчен преглед
    status = article.get("status", "publish")
    sensitive_note = ""
    if article.get("sensitive_names"):
        names = ", ".join(article["sensitive_names"])
        sensitive_note = f'<!-- AUTO-FLAGGED: {names} -->'

    data = {
        "title": article["title"],
        "content": sensitive_note + article["content"] + source_note + photo_credit,
        "status": status,
        "categories": [category_id],
        "format": "standard",
    }
    if media_id:
        data["featured_media"] = media_id
    # SEO excerpt (Yoast/Rank Math използват този)
    if article.get("excerpt"):
        data["excerpt"] = article["excerpt"]
    # Rank Math SEO title + description
    meta_data = {}
    if article.get("meta_description"):
        meta_data["rank_math_description"] = article["meta_description"]
        meta_data["_yoast_wpseo_metadesc"] = article["meta_description"]
    if article.get("seo_title"):
        meta_data["rank_math_title"] = article["seo_title"]
    if meta_data:
        data["meta"] = meta_data

    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        json=data,
        headers=headers
    )

    if r.status_code == 201:
        status_label = "📝 ЧЕРНОВА" if status == "draft" else "✓ Публикувана"
        print(f"  {status_label}: {article['title'][:60]}")
        return True
    else:
        print(f"  ✗ Грешка: {r.status_code} - {r.text[:100]}")
        return False


def setup_categories(categories: list):
    print("Създавам категории...")
    for name in categories:
        cat_id = get_or_create_category(name)
        print(f"  ✓ {name} (ID: {cat_id})")
