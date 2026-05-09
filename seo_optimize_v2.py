"""
SEO оптимизация v2 — обработва само постове БЕЗ rank_math_title.
По-стабилен JSON parser + retry на грешки.
"""
import requests, base64, json, re, time, sys, os
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from groq import Groq

WP_USERNAME = os.environ.get('WP_USERNAME', 'bgalternativanews7')
WP_APP_PASSWORD = os.environ.get('WP_APP_PASSWORD', '')
auth = base64.b64encode(f'{WP_USERNAME}:{WP_APP_PASSWORD}'.encode()).decode()
H = {'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'}
BASE = 'https://bgalternativanews.eu'
GROQ_KEY = os.environ.get('GROQ_API_KEY', '')
client = Groq(api_key=GROQ_KEY)

# По-кратък + по-стриктен prompt
SYS = """Ти си SEO специалист. Връщаш САМО валиден JSON, никакъв друг текст.
Формат: {"t":"SEO заглавие 50-60 символа","d":"meta описание 140-155 символа"}
Заглавието трябва да започва с ключова дума. Описанието да е информативно, без AI клишета.
БЕЗ markdown, БЕЗ обяснения, САМО JSON."""


def strip_html(html):
    return re.sub(r'<[^>]+>', '', html or '').strip()


def extract_json(text):
    """Извлича JSON от текста дори при странни префикси."""
    text = text.strip()
    # Maх. опит: намери първото { ... }
    m = re.search(r'\{[^{}]*"t"\s*:\s*"[^"]*"\s*,\s*"d"\s*:\s*"[^"]*"\s*\}', text, re.DOTALL)
    if m:
        return m.group(0)
    # Fallback: { до първото }
    s = text.find('{')
    e = text.rfind('}')
    if s >= 0 and e > s:
        return text[s:e+1]
    return None


def generate_seo(title: str, content_text: str, retries=2):
    user = f"Заглавие: {title}\n\nСъдържание:\n{content_text[:1200]}"
    for attempt in range(retries + 1):
        try:
            r = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYS},
                    {"role": "user", "content": user},
                ],
                max_tokens=200,
                temperature=0.3,
                response_format={"type": "json_object"},  # Force JSON
            )
            text = r.choices[0].message.content
            data = json.loads(text)
            t = data.get("t", "")[:60]
            d = data.get("d", "")[:155]
            if t and d:
                return t, d
        except Exception as e:
            if attempt < retries:
                time.sleep(3)
                continue
            print(f"    Error after {retries+1} tries: {str(e)[:100]}")
    return None, None


def update_post(post_id: int, t: str, d: str):
    r = requests.post(f"{BASE}/wp-json/wp/v2/posts/{post_id}", headers=H, json={
        "meta": {"rank_math_title": t, "rank_math_description": d}
    })
    return r.status_code == 200


def get_pending_posts():
    """Връща списък с post IDs, които НЯМАТ rank_math_title."""
    pending = []
    page = 1
    while True:
        r = requests.get(
            f"{BASE}/wp-json/wp/v2/posts?per_page=100&page={page}&context=edit&_fields=id,title,content,meta",
            headers=H,
        )
        if r.status_code != 200:
            break
        posts = r.json()
        if not isinstance(posts, list) or not posts:
            break
        for p in posts:
            if not p.get("meta", {}).get("rank_math_title"):
                pending.append(p)
        if len(posts) < 100:
            break
        page += 1
    return pending


def main():
    print("Намирам пропуснати постове...")
    pending = get_pending_posts()
    print(f"Намерени {len(pending)} постове без SEO meta\n")

    success = 0
    failed = 0
    for i, p in enumerate(pending, 1):
        title = strip_html(p["title"]["rendered"])
        content = strip_html(p["content"]["rendered"])

        t, d = generate_seo(title, content)
        if not t or not d:
            failed += 1
            print(f"[{i}/{len(pending)}] ✗ {p['id']}: Groq фейлна")
            continue

        if update_post(p["id"], t, d):
            success += 1
            if i % 10 == 0:
                print(f"[{i}/{len(pending)}] ✓ {success} обновени")
        else:
            failed += 1

        time.sleep(2.2)

    print(f"\n=== РЕЗУЛТАТ ===")
    print(f"Обновени: {success} | Неуспешни: {failed}")
    requests.get(f"{BASE}/?rocket_clean=1")


if __name__ == "__main__":
    main()
