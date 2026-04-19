"""Обновява homepage с новото съдържание."""
import requests, base64

auth = base64.b64encode(b'bgalternativanews7:TjkH u9vY dnYv GQWU 5wLo 5jJf').decode()
H = {'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'}
BASE = 'https://bgalternativanews.eu'

with open('homepage_content.txt', encoding='utf-8') as f:
    content = f.read()

r = requests.post(f'{BASE}/wp-json/wp/v2/pages/556', headers=H, json={
    'content': content,
    'meta': {'_et_pb_use_builder': 'on', '_et_pb_page_layout': 'et_no_sidebar'},
})
print('Update:', r.status_code)

# Also set page meta for "no title"
# Purge cache
requests.get(f'{BASE}/?rocket_clean=1', headers={'Authorization': f'Basic {auth}'})
print('Cache purged')
