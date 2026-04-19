"""Заменя всички featured images с Unsplash снимки + добавя credit."""
import re
import requests
import time
from config import WP_URL
from wordpress_poster import get_auth_header, upload_media_from_url
from unsplash_helper import get_image_for_article, unsplash_credit_html


def get_category_name(cat_id: int, cache: dict) -> str:
    if cat_id in cache:
        return cache[cat_id]
    r = requests.get(f"{WP_URL}/wp-json/wp/v2/categories/{cat_id}", headers=get_auth_header())
    if r.status_code == 200:
        name = r.json()["name"]
        cache[cat_id] = name
        return name
    return ""


def has_unsplash_credit(content: str) -> bool:
    return "Unsplash" in content and "utm_source=bgalternativa" in content


def run():
    cat_cache = {}
    old_media_ids = []

    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/posts",
        params={"per_page": 100, "_fields": "id,title,content,categories,featured_media"},
        headers=get_auth_header(),
    )
    posts = r.json()
    print(f"Намерени {len(posts)} публикации.\n")

    updated = 0
    skipped = 0
    failed = 0

    for i, post in enumerate(posts, 1):
        pid = post["id"]
        title = re.sub(r"&[^;]+;", "", post["title"]["rendered"])[:65]
        content = post["content"]["rendered"]

        if has_unsplash_credit(content):
            skipped += 1
            continue

        cats = post.get("categories", [])
        category_name = get_category_name(cats[0], cat_cache) if cats else "Свят"

        print(f"[{i}/{len(posts)}] {title}")

        photo, query = get_image_for_article(post["title"]["rendered"], category_name)
        if photo and photo.get("_rate_limited"):
            print(f"\n⏸ Rate limit достигнат на статия {i}/{len(posts)}. Спирам.")
            print(f"Пусни отново backfill_unsplash.py след 1 час.")
            break
        if not photo:
            print(f"    ✗ No Unsplash match")
            failed += 1
            continue

        print(f"    → query: {query}")

        media_id = upload_media_from_url(photo["url"])
        if not media_id:
            print(f"    ✗ Upload failed")
            failed += 1
            continue

        # Премахваме съществуващия credit (ако има такъв от старите файлове)
        new_content = content
        # Запазваме стария featured_media ID за изтриване
        old_fm = post.get("featured_media", 0)
        if old_fm and old_fm != media_id:
            old_media_ids.append(old_fm)

        # Добавяме Unsplash credit
        credit = unsplash_credit_html(photo)
        new_content = new_content + credit

        headers = get_auth_header()
        headers["Content-Type"] = "application/json"
        upd = requests.post(
            f"{WP_URL}/wp-json/wp/v2/posts/{pid}",
            json={"featured_media": media_id, "content": new_content},
            headers=headers,
        )
        if upd.status_code == 200:
            print(f"    ✓ Обновена (media {media_id})")
            updated += 1
        else:
            print(f"    ✗ Update {upd.status_code}")
            failed += 1

        # Пауза за rate limit (Unsplash 50/час = ~72 сек между заявки в demo mode)
        # Но при 100 статии нямаме проблем ако минем под лимита
        time.sleep(1.5)

    # Записваме ID-тата на старите медия файлове за изтриване
    with open("old_media_to_delete.txt", "w") as f:
        for mid in old_media_ids:
            f.write(f"{mid}\n")

    print("\n" + "=" * 60)
    print(f"Обновени: {updated}")
    print(f"Пропуснати (вече с Unsplash): {skipped}")
    print(f"Неуспешни: {failed}")
    print(f"Стари медия ID-та записани в old_media_to_delete.txt: {len(old_media_ids)}")


if __name__ == "__main__":
    run()
