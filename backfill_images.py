# ============================================================
# BGАлтернатива - Backfill на featured images за съществуващи статии
# ============================================================

import re
import requests
from config import WP_URL
from wordpress_poster import get_auth_header, upload_media_from_url


def extract_source_url(content: str) -> str:
    """Извлича оригиналния URL от 'Източник:' линка в статията."""
    match = re.search(r'Източник:\s*<a\s+href="([^"]+)"', content)
    return match.group(1) if match else ""


def extract_og_image(url: str) -> str:
    """Взима og:image от оригиналната статия."""
    try:
        r = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; BGAlternativa/1.0)"
        })
        if r.status_code != 200:
            return ""
        html = r.text
        # og:image
        m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if m:
            return m.group(1)
        m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html, re.I)
        if m:
            return m.group(1)
        # twitter:image
        m = re.search(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if m:
            return m.group(1)
        # Първо <img> в <article>
        m = re.search(r'<article[^>]*>.*?<img[^>]+src=["\']([^"\']+)["\']', html, re.I | re.S)
        if m:
            return m.group(1)
    except Exception as e:
        print(f"    ⚠ Грешка при fetch: {e}")
    return ""


def backfill():
    headers = get_auth_header()
    # Взимаме всички постове без featured image (до 100)
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/posts",
        params={"per_page": 100, "_fields": "id,title,content,featured_media"},
        headers=headers
    )
    posts = r.json()
    print(f"Намерени {len(posts)} публикации.\n")

    updated = 0
    skipped = 0
    failed = 0

    for i, post in enumerate(posts, 1):
        title = post["title"]["rendered"][:60]
        if post.get("featured_media", 0) > 0:
            skipped += 1
            continue

        content = post["content"]["rendered"]
        source_url = extract_source_url(content)
        if not source_url:
            print(f"[{i}/{len(posts)}] ✗ Няма източник: {title}")
            failed += 1
            continue

        print(f"[{i}/{len(posts)}] → {title}")
        print(f"    Fetching: {source_url[:80]}")

        image_url = extract_og_image(source_url)
        if not image_url:
            print(f"    ✗ Няма og:image")
            failed += 1
            continue

        print(f"    Image: {image_url[:80]}")
        media_id = upload_media_from_url(image_url)
        if not media_id:
            print(f"    ✗ Не се качи")
            failed += 1
            continue

        # Обнови публикацията
        headers_json = get_auth_header()
        headers_json["Content-Type"] = "application/json"
        update = requests.post(
            f"{WP_URL}/wp-json/wp/v2/posts/{post['id']}",
            json={"featured_media": media_id},
            headers=headers_json
        )
        if update.status_code == 200:
            print(f"    ✓ Обновена (media ID: {media_id})")
            updated += 1
        else:
            print(f"    ✗ Грешка: {update.status_code}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Обновени: {updated}")
    print(f"Пропуснати (вече имат снимка): {skipped}")
    print(f"Неуспешни: {failed}")


if __name__ == "__main__":
    backfill()
