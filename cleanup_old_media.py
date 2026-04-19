"""Изтрива всички стари scraped снимки от WP Media Library."""
import requests, base64, sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

auth = base64.b64encode(b'bgalternativanews7:TjkH u9vY dnYv GQWU 5wLo 5jJf').decode()
H = {'Authorization': f'Basic {auth}'}
BASE = 'https://bgalternativanews.eu'

with open('old_media_to_delete.txt') as f:
    ids = [int(line.strip()) for line in f if line.strip()]

# Премахни дубликати
ids = list(set(ids))
print(f'Ще изтрием {len(ids)} стари медия файла...\n')

deleted = 0
failed = 0
for i, mid in enumerate(ids, 1):
    r = requests.delete(f'{BASE}/wp-json/wp/v2/media/{mid}?force=true', headers=H)
    if r.status_code in (200, 404):
        deleted += 1
        if i % 10 == 0:
            print(f'  {i}/{len(ids)} изтрити')
    else:
        failed += 1
        print(f'  ✗ {mid}: {r.status_code}')

print(f'\n✓ Изтрити: {deleted}')
print(f'✗ Неуспешни: {failed}')
