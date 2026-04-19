"""Създава FAQ страница с FAQPage Schema markup."""
import requests, base64, sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

auth = base64.b64encode(b'bgalternativanews7:TjkH u9vY dnYv GQWU 5wLo 5jJf').decode()
H = {'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'}
BASE = 'https://bgalternativanews.eu'

# FAQ въпроси и отговори
FAQ_ITEMS = [
    {
        "q": "Какво представлява BGАлтернатива?",
        "a": "BGАлтернатива е независима информационна платформа, която обобщава актуални новини и анализи по политически, геополитически и обществени теми. Сайтът допълва едноименния YouTube канал."
    },
    {
        "q": "Как се създава съдържанието на сайта?",
        "a": "Новинарските материали представляват кратки обобщения и преразкази на публично достъпна информация. Използваме технологии за автоматизация, за да покрием широк спектър от теми ежедневно. Всяка публикация се преглежда от редакцията преди да стане публична при чувствителни теми."
    },
    {
        "q": "Защо използвате изображения от банки за стокови снимки?",
        "a": "За да избегнем копирайт конфликти с други медии, за всяка публикация подбираме безплатни лицензирани изображения от Unsplash и Pexels, с надлежно приписване на фотографа и източника."
    },
    {
        "q": "Мога ли да препубликувам материал от сайта?",
        "a": "Кратко цитиране с ясно обозначен източник и активен линк към оригинала е позволено. Пълно препубликуване изисква изрично писмено разрешение."
    },
    {
        "q": "Как мога да подам сигнал за грешка или неточност?",
        "a": "Ако забележите фактическа грешка или считате, че публикация се нуждае от корекция, можете да ни уведомите чрез нашия YouTube канал. Всеки такъв сигнал се разглежда в разумен срок."
    },
    {
        "q": "Как се финансира сайтът?",
        "a": "BGАлтернатива е независим и не получава финансиране от политически субекти, държавни институции или корпоративни спонсори. Поддръжката се осъществява чрез приходи от реклама и партньорски линкове, които винаги са ясно обозначени."
    },
    {
        "q": "Как да се абонирам за актуалните новини?",
        "a": "Най-добрият начин е да се абонирате за нашия YouTube канал - там публикуваме видео прегледи и коментари. Сайтът с писменото съдържание се обновява ежедневно и може да се посещава редовно."
    },
    {
        "q": "Ще станат ли моите лични данни достъпни за трети страни?",
        "a": "Не продаваме и не предоставяме лични данни на трети страни. Използваме само необходимите технически и аналитични бисквитки, и то само след Ваше съгласие. Подробности в Политиката за поверителност."
    },
    {
        "q": "Мога ли да коментирам под статиите?",
        "a": "Да, коментарите са отворени. Всеки коментар подлежи на модерация и може да отнеме време, преди да се появи. Забранени са обидни, дискриминационни или противоречащи на закона мнения."
    },
    {
        "q": "Как мога да се свържа с редакцията?",
        "a": "За общи въпроси, предложения или право на отговор, можете да ни пишете чрез нашия YouTube канал, който е основен комуникационен канал."
    },
]

# Schema.org/FAQPage JSON-LD
schema_items = []
for item in FAQ_ITEMS:
    schema_items.append({
        "@type": "Question",
        "name": item["q"],
        "acceptedAnswer": {
            "@type": "Answer",
            "text": item["a"]
        }
    })

schema_json = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": schema_items
}

import json
schema_script = json.dumps(schema_json, ensure_ascii=False, indent=2)

# Build FAQ HTML content
faq_html = '<!-- wp:paragraph -->\n<p>Отговори на най-честите въпроси за платформата BGАлтернатива.</p>\n<!-- /wp:paragraph -->\n\n'

for i, item in enumerate(FAQ_ITEMS, 1):
    faq_html += f'''<!-- wp:html -->
<details class="bg-faq-item">
<summary>{item["q"]}</summary>
<p>{item["a"]}</p>
</details>
<!-- /wp:html -->

'''

# Add Schema JSON-LD script (Rank Math will also add News/Article schema)
schema_start = '<scr' + 'ipt type="application/ld+json">'
schema_end = '<\/scr' + 'ipt>'
faq_html += f'''<!-- wp:html -->
{schema_start}
{schema_script}
{schema_end}
<!-- /wp:html -->
'''

# Check if FAQ exists, create or update
r = requests.get(f'{BASE}/wp-json/wp/v2/pages?slug=chesti-vaprosi', headers=H).json()
if r:
    pid = r[0]['id']
    resp = requests.post(f'{BASE}/wp-json/wp/v2/pages/{pid}', headers=H, json={
        'title': 'Често задавани въпроси',
        'content': faq_html,
    })
    print(f'Updated FAQ page {pid}: {resp.status_code}')
else:
    resp = requests.post(f'{BASE}/wp-json/wp/v2/pages', headers=H, json={
        'title': 'Често задавани въпроси',
        'slug': 'chesti-vaprosi',
        'content': faq_html,
        'status': 'publish',
    })
    pid = resp.json().get('id')
    print(f'Created FAQ page {pid}: {resp.status_code}')

# Add to footer navigation widget
nav_with_faq = '''<!-- wp:group -->
<div class="wp-block-group"><h3>НАВИГАЦИЯ</h3>
<!-- wp:html -->
<ul class="footer-links">
<li><a href="/">Начало</a></li>
<li><a href="/za-nas/">За нас</a></li>
<li><a href="/chesti-vaprosi/">Често задавани въпроси</a></li>
<li><a href="https://www.youtube.com/@bgalternativa" target="_blank" rel="noopener">YouTube канал</a></li>
<li><a href="/obshti-usloviya/">Общи условия</a></li>
<li><a href="/politika-za-poveritelnost/">Политика за поверителност</a></li>
<li><a href="/politika-za-biskvitkite/">Политика за бисквитките</a></li>
</ul>
<!-- /wp:html -->
</div>
<!-- /wp:group -->'''

r = requests.put(f'{BASE}/wp-json/wp/v2/widgets/block-11', headers=H, json={
    'instance': {'raw': {'content': nav_with_faq}}
})
print(f'Footer nav updated: {r.status_code}')

requests.get(f'{BASE}/?rocket_clean=1')
print(f'\nFAQ URL: {BASE}/chesti-vaprosi/')
