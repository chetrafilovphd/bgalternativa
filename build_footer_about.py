"""Попълва footer widgets + пише "За нас" страница."""
import requests, base64

auth = base64.b64encode(b'bgalternativanews7:TjkH u9vY dnYv GQWU 5wLo 5jJf').decode()
H = {'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'}
BASE = 'https://bgalternativanews.eu'

# ==========================================================
# FOOTER WIDGETS (sidebar-2 = footer area)
# ==========================================================

# 1. Колона "За BGАлтернатива"
about_widget = '''<!-- wp:group -->
<div class="wp-block-group"><h3>ЗА BGАЛТЕРНАТИВА</h3>
<!-- wp:paragraph -->
<p>Независим медиен канал за политически и геополитически новини, анализи и коментари. Даваме глас на темите, които другите медии избягват.</p>
<!-- /wp:paragraph -->
<!-- wp:paragraph -->
<p><a href="https://www.youtube.com/@bgalternativa" target="_blank" rel="noopener">📺 YouTube канал</a></p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->'''

# 2. Колона "Рубрики"
categories_widget = '''<!-- wp:group -->
<div class="wp-block-group"><h3>РУБРИКИ</h3>
<!-- wp:html -->
<ul class="footer-links">
<li><a href="/category/bulgaria/">България</a></li>
<li><a href="/category/svyat/">Свят</a></li>
<li><a href="/category/geopolitika/">Геополитика</a></li>
<li><a href="/category/analizi/">Анализи</a></li>
</ul>
<!-- /wp:html -->
</div>
<!-- /wp:group -->'''

# 3. Колона "Навигация"
nav_widget = '''<!-- wp:group -->
<div class="wp-block-group"><h3>НАВИГАЦИЯ</h3>
<!-- wp:html -->
<ul class="footer-links">
<li><a href="/">Начало</a></li>
<li><a href="/za-nas/">За нас</a></li>
<li><a href="https://www.youtube.com/@bgalternativa" target="_blank">YouTube канал</a></li>
</ul>
<!-- /wp:html -->
</div>
<!-- /wp:group -->'''

# 4. Колона "Следвайте ни"
follow_widget = '''<!-- wp:group -->
<div class="wp-block-group"><h3>СЛЕДВАЙТЕ НИ</h3>
<!-- wp:html -->
<div class="footer-follow">
<a href="https://www.youtube.com/@bgalternativa?sub_confirmation=1" target="_blank" rel="noopener" class="follow-btn yt-btn">▶ АБОНИРАЙ СЕ</a>
<p style="margin-top:15px;color:#9a9a9a;font-size:13px;">Получавайте най-новите анализи и коментари директно във вашия инбокс.</p>
</div>
<!-- /wp:html -->
</div>
<!-- /wp:group -->'''

for widget_content in [about_widget, categories_widget, nav_widget, follow_widget]:
    r = requests.post(f'{BASE}/wp-json/wp/v2/widgets', headers=H, json={
        'sidebar': 'sidebar-2',
        'id_base': 'block',
        'instance': {'raw': {'content': widget_content}}
    })
    print(f'Footer widget: {r.status_code}')

# ==========================================================
# ЗА НАС страница
# ==========================================================

ABOUT_CONTENT = """<!-- wp:paragraph -->
<p><strong>BGАлтернатива</strong> е независим медиен канал, създаден с ясна цел — да даде глас на темите, които големите медии избягват или разглеждат повърхностно. В свят на бърза информация, ние се фокусираме върху задълбочен анализ, критично мислене и перспективи, които не намирате в мейнстрийм медиите.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Нашата мисия</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Живеем в епоха, в която достъпът до информация никога не е бил по-лесен — но умението да различим истината от пропагандата, фактите от спина и реалния анализ от повторените тези — никога не е било по-трудно. <strong>BGАлтернатива</strong> се стреми да бъде убежище от шума. Място, където сложните политически и геополитически теми се разбиват на ясни и разбираеми части, без патернализъм, без скрити интереси.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>За какво пишем</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
<li><strong>България</strong> — политика, общество, икономика, събитията зад кулисите</li>
<li><strong>Свят</strong> — актуални международни новини с фокус върху това как те засягат региона и България</li>
<li><strong>Геополитика</strong> — задълбочени разбори на конфликти, съюзи и стратегически интереси</li>
<li><strong>Анализи</strong> — коментари и мнения, които провокират мислене, не продават идеология</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>Нашият подход</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Редакционната ни работа се води от три принципа:</p>
<!-- /wp:paragraph -->

<!-- wp:list {"ordered":true} -->
<ol>
<li><strong>Независимост</strong> — не служим на партия, олигарх или чужда сила. Само на читателите и зрителите си.</li>
<li><strong>Прозрачност</strong> — когато използваме чужди източници, ги посочваме. Когато правим анализ, обясняваме рамката си.</li>
<li><strong>Критичност</strong> — задаваме неудобните въпроси. Към всички, включително към себе си.</li>
</ol>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>YouTube каналът</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Сърцето на проекта е <strong>YouTube каналът BGАлтернатива</strong>, където публикуваме редовни видео-анализи, коментари и дискусии. Този сайт допълва каната с писмени публикации и агрегирана новинарска хроника, за да имате винаги под ръка пълната картина.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p style="text-align:center;margin-top:30px;"><a href="https://www.youtube.com/@bgalternativa?sub_confirmation=1" target="_blank" rel="noopener" style="display:inline-block;background:#c0152a;color:#fff;padding:14px 32px;border-radius:4px;font-weight:900;letter-spacing:2px;text-transform:uppercase;text-decoration:none;font-size:14px;">▶ АБОНИРАЙ СЕ ЗА КАНАЛА</a></p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Редакционни стандарти</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Част от съдържанието ни се формира чрез агрегиране и преработване на публично достъпни новини от авторитетни източници като Dnevnik, 24 Часа, DW, Al Jazeera и др. Винаги посочваме оригиналния източник и използваме изображения от легални стокови фото бази (Unsplash, Pexels) с правилното приписване. При коментарните ни материали мнението е на автора и не ангажира цялата редакция.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Контакт</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Имате предложение за тема? Забелязахте фактологическа грешка? Искате да сътрудничите? Пишете ни на YouTube канала или очаквайте скоро да отворим и директна форма за контакт.</p>
<!-- /wp:paragraph -->"""

# Find or update "За нас" page
r = requests.get(f'{BASE}/wp-json/wp/v2/pages?slug=za-nas', headers=H).json()
if r:
    about_id = r[0]['id']
    resp = requests.post(f'{BASE}/wp-json/wp/v2/pages/{about_id}', headers=H, json={
        'content': ABOUT_CONTENT,
        'title': 'За нас',
    })
    print(f'Update За нас ({about_id}): {resp.status_code}')

# Purge cache
requests.get(f'{BASE}/?rocket_clean=1')
print('Done')
