"""Сканира публикуваните статии за AI-изми и ги заменя с нормален български."""
import requests, base64, re, sys, html
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

auth = base64.b64encode(b'bgalternativanews7:TjkH u9vY dnYv GQWU 5wLo 5jJf').decode()
H = {'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'}
BASE = 'https://bgalternativanews.eu'

# Речник: AI-изми / неестествени изрази → нормален български
# Използваме \b за цели думи, за да не засегнем съставни думи
REPLACEMENTS = [
    # Чужди думи транслитерирани
    (r'\bинбокс\b', 'пощенска кутия'),
    (r'\bИнбокс\b', 'Пощенска кутия'),
    (r'\bканава\b', 'платно'),
    (r'\bКанава\b', 'Платно'),
    (r'\bканавата\b', 'платното'),
    (r'\bдедлайн\w*\b', 'краен срок'),
    (r'\bДедлайн\w*\b', 'Краен срок'),
    (r'\bдийлър\w*\b', 'търговец'),
    (r'\bгеймър\w*\b', 'геймър'),  # оставяме, вече е в речника
    (r'\bтраш\b', 'боклук'),
    (r'\bинстантно\b', 'незабавно'),
    (r'\bинстантен\b', 'моментален'),
    (r'\bфийдбек\b', 'обратна връзка'),
    (r'\bФийдбек\b', 'Обратна връзка'),
    (r'\bлиддер\w*\b', 'водач'),
    (r'\bсетъп\b', 'настройка'),
    (r'\bъпдейт\w*\b', 'обновяване'),
    (r'\bъпгрейд\w*\b', 'надграждане'),
    (r'\bЪпдейт\w*\b', 'Обновяване'),
    (r'\bкол ?център\b', 'кол център', ),  # OK
    (r'\bиншурънс\b', 'застраховка'),
    (r'\bчелендж\w*\b', 'предизвикателство'),
    (r'\bЧелендж\w*\b', 'Предизвикателство'),
    (r'\bритейл\w*\b', 'търговия на дребно'),
    (r'\bбрейк\b', 'пауза'),
    (r'\bбрейкинг\b', 'извънредно'),
    (r'\bСкрийншот\w*\b', 'Екранна снимка'),
    (r'\bскрийншот\w*\b', 'екранна снимка'),
    (r'\bлинк\w*\b', 'линк'),  # оставяме, вече се използва
    (r'\bпроектирано\b', 'разработено'),

    # AI фрази (типични шаблонни изрази)
    (r'В заключение,?\s+', ''),
    (r'В крайна сметка,?\s+', ''),
    (r'Важно е да се отбележи, че', 'Отбелязваме, че'),
    (r'Важно е да отбележим, че', 'Отбелязваме, че'),
    (r'Струва си да се отбележи', 'Отбелязваме'),
    (r'От съществено значение е', 'Важно е'),
    (r'В днешния бързо развиващ се свят', 'В съвременността'),
    (r'значимостта на (?:това|тези|тази) не може да бъде подценена', 'това е от значение'),
    (r'навлизайки в (?:този|тази) тема', 'по темата'),
    (r'постоянно развиващ\w* се', 'променящ се'),
    (r'В епохата на\b', 'В модерното време'),
]


def clean_text(content):
    changed = False
    for pattern, replacement in REPLACEMENTS:
        if isinstance(replacement, str):
            new, n = re.subn(pattern, replacement, content)
            if n > 0:
                content = new
                changed = True
    return content, changed


def scan_all():
    total = 0
    changed_count = 0
    flagged = []
    page = 1
    while True:
        r = requests.get(f'{BASE}/wp-json/wp/v2/posts?per_page=50&page={page}&_fields=id,title,content', headers=H)
        posts = r.json()
        if not isinstance(posts, list) or not posts:
            break
        for p in posts:
            total += 1
            content = p['content']['rendered']
            title = p['title']['rendered']
            new_content, changed = clean_text(content)
            new_title, title_changed = clean_text(title)
            if changed or title_changed:
                changed_count += 1
                payload = {}
                if changed:
                    payload['content'] = new_content
                if title_changed:
                    payload['title'] = new_title
                upd = requests.post(f'{BASE}/wp-json/wp/v2/posts/{p["id"]}',
                                    headers=H, json=payload)
                if upd.status_code == 200:
                    print(f'  ✓ {p["id"]}: {title[:60]}')
                else:
                    print(f'  ✗ {p["id"]}: {upd.status_code}')
                flagged.append(p['id'])
        if len(posts) < 50:
            break
        page += 1

    print(f'\nТотал статии прегледани: {total}')
    print(f'Променени: {changed_count}')
    return flagged


if __name__ == '__main__':
    flagged = scan_all()
    # Purge cache
    requests.get(f'{BASE}/?rocket_clean=1')
    print('Cache cleared')
