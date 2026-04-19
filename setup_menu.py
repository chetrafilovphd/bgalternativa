"""Създава главното меню с правилния ред и заглавия."""
import requests, base64, sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

auth = base64.b64encode(b'bgalternativanews7:TjkH u9vY dnYv GQWU 5wLo 5jJf').decode()
H = {'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'}
BASE = 'https://bgalternativanews.eu'
MENU_ID = 9

# Взимаме категориите
cats = requests.get(f'{BASE}/wp-json/wp/v2/categories?per_page=20', headers=H).json()
cat_map = {c['name']: c['id'] for c in cats}
print('Categories:', cat_map)

# Взимаме страниците
pages = requests.get(f'{BASE}/wp-json/wp/v2/pages?per_page=20', headers=H).json()
page_map = {p['slug']: p['id'] for p in pages}
print('Pages:', page_map)

# Изтриваме всички съществуващи menu items в нашето меню (ако има)
existing = requests.get(f'{BASE}/wp-json/wp/v2/menu-items?menus={MENU_ID}&per_page=50', headers=H).json()
for it in existing:
    requests.delete(f'{BASE}/wp-json/wp/v2/menu-items/{it["id"]}?force=true', headers=H)

# Дефинираме реда на елементите
items = [
    {'title': 'НАЧАЛО',      'type': 'custom', 'url': BASE + '/'},
    {'title': 'БЪЛГАРИЯ',    'type': 'taxonomy', 'object': 'category', 'object_id': cat_map.get('България')},
    {'title': 'СВЯТ',        'type': 'taxonomy', 'object': 'category', 'object_id': cat_map.get('Свят')},
    {'title': 'ГЕОПОЛИТИКА', 'type': 'taxonomy', 'object': 'category', 'object_id': cat_map.get('Геополитика')},
    {'title': 'АНАЛИЗИ',     'type': 'taxonomy', 'object': 'category', 'object_id': cat_map.get('Анализи')},
    {'title': 'ЗА НАС',      'type': 'post_type', 'object': 'page', 'object_id': page_map.get('za-nas')},
]

for i, item in enumerate(items, 1):
    payload = {
        'title': item['title'],
        'menus': MENU_ID,
        'menu_order': i,
        'status': 'publish',
        'type': item['type'],
    }
    if item['type'] == 'custom':
        payload['url'] = item['url']
    else:
        payload['object'] = item['object']
        payload['object_id'] = item['object_id']

    r = requests.post(f'{BASE}/wp-json/wp/v2/menu-items', headers=H, json=payload)
    if r.status_code == 201:
        print(f'  ✓ {item["title"]}')
    else:
        print(f'  ✗ {item["title"]}: {r.status_code} - {r.text[:200]}')

# Потвърждаваме че менюто е в primary-menu location
update = requests.post(f'{BASE}/wp-json/wp/v2/menus/{MENU_ID}', headers=H, json={'locations':['primary-menu']})
print('Location assignment:', update.status_code)

# Показваме текущото меню
final = requests.get(f'{BASE}/wp-json/wp/v2/menu-items?menus={MENU_ID}&per_page=20&orderby=menu_order&order=asc', headers=H).json()
print('\nFinal menu:')
for it in final:
    print(f'  {it["menu_order"]}. {it["title"]["rendered"]}')
