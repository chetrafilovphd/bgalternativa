"""Създава професионална newsroom homepage с Divi Builder."""
import requests, base64, sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

auth = base64.b64encode(b'bgalternativanews7:TjkH u9vY dnYv GQWU 5wLo 5jJf').decode()
H = {'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'}
BASE = 'https://bgalternativanews.eu'

# Divi section CSS accents
DIVI_CONTENT = """[et_pb_section fb_built="1" fullwidth="on" disabled_on="off|off|off" _builder_version="4.27.6" background_color="#0f0f0f" custom_padding="0px||0px||false|false" global_colors_info="{}"][et_pb_fullwidth_post_title meta="off" featured_image="off" text_color="light" _builder_version="4.27.6" title_font="Roboto Condensed|900|||||||" title_text_color="#ffffff" title_font_size="42px" background_color="#c0152a" custom_padding="20px|0|20px|0|false|false" global_colors_info="{}"][/et_pb_fullwidth_post_title][/et_pb_section]

[et_pb_section fb_built="1" _builder_version="4.27.6" background_color="#0f0f0f" custom_padding="40px||20px||false|false" global_colors_info="{}"][et_pb_row _builder_version="4.27.6" global_colors_info="{}"][et_pb_column type="4_4" _builder_version="4.27.6" global_colors_info="{}"][et_pb_text _builder_version="4.27.6" text_font="||||||||" text_text_color="#c0152a" header_font="Roboto Condensed|900|||||||" header_font_size="28px" header_text_color="#ffffff" custom_padding="0|0|15px|0|false|false" global_colors_info="{}"]

<h2 style="border-left:5px solid #c0152a;padding-left:15px;margin:0;">ГЛАВНИ НОВИНИ</h2>

[/et_pb_text][et_pb_blog fullwidth="off" posts_number="1" include_categories="2,3,5" show_thumbnail="on" show_content="off" show_author="off" show_date="on" show_categories="on" show_comments="off" show_pagination="off" show_more="on" _builder_version="4.27.6" header_font="Roboto Condensed|900|||||||" header_text_color="#ffffff" header_font_size="32px" meta_text_color="#9a9a9a" body_text_color="#f2f2f2" read_more_text_color="#c0152a" background_color="#1a1a1a" custom_padding="0|0|30px|0|false|false" global_colors_info="{}"][/et_pb_blog][/et_pb_column][/et_pb_row]

[et_pb_row column_structure="1_3,1_3,1_3" _builder_version="4.27.6" global_colors_info="{}"][et_pb_column type="1_3" _builder_version="4.27.6" global_colors_info="{}"][et_pb_text _builder_version="4.27.6" header_2_font="Roboto Condensed|900|||||||" header_2_text_color="#ffffff" header_2_font_size="22px" custom_padding="0|0|10px|0|false|false" global_colors_info="{}"]

<h2 style="border-bottom:3px solid #c0152a;padding-bottom:8px;margin:0;">БЪЛГАРИЯ</h2>

[/et_pb_text][et_pb_blog posts_number="4" include_categories="2" show_thumbnail="on" show_content="off" show_excerpt_length="off" show_author="off" show_date="on" show_categories="off" show_comments="off" show_more="off" show_pagination="off" _builder_version="4.27.6" header_font="Roboto Condensed|700|||||||" header_text_color="#ffffff" header_font_size="16px" meta_font_size="11px" meta_text_color="#9a9a9a" background_color="transparent" custom_padding="0|0|0|0|false|false" global_colors_info="{}"][/et_pb_blog][/et_pb_column]

[et_pb_column type="1_3" _builder_version="4.27.6" global_colors_info="{}"][et_pb_text _builder_version="4.27.6" header_2_font="Roboto Condensed|900|||||||" header_2_text_color="#ffffff" header_2_font_size="22px" custom_padding="0|0|10px|0|false|false" global_colors_info="{}"]

<h2 style="border-bottom:3px solid #c0152a;padding-bottom:8px;margin:0;">СВЯТ</h2>

[/et_pb_text][et_pb_blog posts_number="4" include_categories="3" show_thumbnail="on" show_content="off" show_author="off" show_date="on" show_categories="off" show_comments="off" show_more="off" show_pagination="off" _builder_version="4.27.6" header_font="Roboto Condensed|700|||||||" header_text_color="#ffffff" header_font_size="16px" meta_font_size="11px" meta_text_color="#9a9a9a" background_color="transparent" global_colors_info="{}"][/et_pb_blog][/et_pb_column]

[et_pb_column type="1_3" _builder_version="4.27.6" global_colors_info="{}"][et_pb_text _builder_version="4.27.6" header_2_font="Roboto Condensed|900|||||||" header_2_text_color="#ffffff" header_2_font_size="22px" custom_padding="0|0|10px|0|false|false" global_colors_info="{}"]

<h2 style="border-bottom:3px solid #c0152a;padding-bottom:8px;margin:0;">ГЕОПОЛИТИКА</h2>

[/et_pb_text][et_pb_blog posts_number="4" include_categories="5" show_thumbnail="on" show_content="off" show_author="off" show_date="on" show_categories="off" show_comments="off" show_more="off" show_pagination="off" _builder_version="4.27.6" header_font="Roboto Condensed|700|||||||" header_text_color="#ffffff" header_font_size="16px" meta_font_size="11px" meta_text_color="#9a9a9a" background_color="transparent" global_colors_info="{}"][/et_pb_blog][/et_pb_column][/et_pb_row][/et_pb_section]

[et_pb_section fb_built="1" _builder_version="4.27.6" background_color="#1a1a1a" custom_padding="50px||50px||false|false" global_colors_info="{}"][et_pb_row _builder_version="4.27.6" global_colors_info="{}"][et_pb_column type="4_4" _builder_version="4.27.6" global_colors_info="{}"][et_pb_text _builder_version="4.27.6" header_2_font="Roboto Condensed|900|||||||" header_2_text_color="#c0152a" header_2_font_size="32px" header_2_line_height="1em" global_colors_info="{}"]

<h2 style="text-align:center;letter-spacing:3px;">АНАЛИЗИ & МНЕНИЯ</h2>
<p style="text-align:center;color:#9a9a9a;max-width:600px;margin:10px auto 30px auto;">Задълбочени коментари и анализи по актуалните теми от България и света</p>

[/et_pb_text][et_pb_blog posts_number="3" include_categories="6" show_thumbnail="on" show_content="off" show_author="off" show_date="on" show_categories="off" show_comments="off" show_more="on" show_pagination="off" fullwidth="off" use_overlay="on" hover_overlay_color="rgba(192,21,42,0.6)" _builder_version="4.27.6" header_font="Roboto Condensed|900|||||||" header_text_color="#ffffff" header_font_size="22px" meta_text_color="#9a9a9a" body_text_color="#f2f2f2" read_more_text_color="#c0152a" background_color="#0f0f0f" global_colors_info="{}"][/et_pb_blog][/et_pb_column][/et_pb_row][/et_pb_section]

[et_pb_section fb_built="1" _builder_version="4.27.6" background_color="#000000" custom_padding="60px||60px||false|false" global_colors_info="{}"][et_pb_row column_structure="1_2,1_2" _builder_version="4.27.6" global_colors_info="{}"][et_pb_column type="1_2" _builder_version="4.27.6" global_colors_info="{}"][et_pb_text _builder_version="4.27.6" text_text_color="#ffffff" text_font_size="16px" header_2_font="Roboto Condensed|900|||||||" header_2_text_color="#ffffff" header_2_font_size="36px" header_2_line_height="1.1em" global_colors_info="{}"]

<h2 style="color:#fff;">ГЛЕДАЙТЕ НИ И В<br><span style="color:#c0152a;">YOUTUBE</span></h2>
<p style="color:#d0d0d0;font-size:16px;line-height:1.7;margin:20px 0;">Присъединете се към хилядите, които следват BG<span style="color:#c0152a;font-weight:900;">Алтернатива</span> за остри политически анализи, геополитически разбори и дискусии, които другите медии избягват.</p>
<p><a href="https://www.youtube.com/@bgalternativa?sub_confirmation=1" target="_blank" rel="noopener" style="display:inline-block;background:#c0152a;color:#fff;padding:14px 32px;border-radius:4px;font-weight:900;letter-spacing:2px;text-transform:uppercase;text-decoration:none;font-size:14px;">▶ АБОНИРАЙ СЕ</a></p>

[/et_pb_text][/et_pb_column][et_pb_column type="1_2" _builder_version="4.27.6" global_colors_info="{}"][et_pb_code _builder_version="4.27.6" global_colors_info="{}"]

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:8px;border:2px solid #c0152a;"><iframe style="position:absolute;top:0;left:0;width:100%;height:100%;" src="https://www.youtube.com/embed/videoseries?list=UU0pRhrzNkBkoNcWNXVUnTAw" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>

[/et_pb_code][/et_pb_column][/et_pb_row][/et_pb_section]

[et_pb_section fb_built="1" _builder_version="4.27.6" background_color="#0f0f0f" custom_padding="40px||40px||false|false" global_colors_info="{}"][et_pb_row _builder_version="4.27.6" global_colors_info="{}"][et_pb_column type="4_4" _builder_version="4.27.6" global_colors_info="{}"][et_pb_text _builder_version="4.27.6" header_2_font="Roboto Condensed|900|||||||" header_2_text_color="#ffffff" header_2_font_size="28px" custom_padding="0|0|20px|0|false|false" global_colors_info="{}"]

<h2 style="border-left:5px solid #c0152a;padding-left:15px;margin:0;">ВСИЧКИ НОВИНИ</h2>

[/et_pb_text][et_pb_blog fullwidth="off" posts_number="9" include_categories="all" show_thumbnail="on" show_content="off" show_author="off" show_date="on" show_categories="on" show_comments="off" show_more="on" show_pagination="on" _builder_version="4.27.6" header_font="Roboto Condensed|900|||||||" header_text_color="#ffffff" header_font_size="20px" meta_text_color="#9a9a9a" body_text_color="#f2f2f2" read_more_text_color="#c0152a" background_color="#1a1a1a" global_colors_info="{}"][/et_pb_blog][/et_pb_column][/et_pb_row][/et_pb_section]"""

# Check if Home page exists
r = requests.get(f'{BASE}/wp-json/wp/v2/pages?slug=nachalo', headers=H).json()
if r:
    home_id = r[0]['id']
    print(f'Existing Начало page: {home_id}')
    # Update
    payload = {
        'title': 'Начало',
        'content': DIVI_CONTENT,
        'status': 'publish',
        'meta': {'_et_pb_use_builder': 'on'},
    }
    resp = requests.put(f'{BASE}/wp-json/wp/v2/pages/{home_id}', headers=H, json=payload)
    print(f'Update: {resp.status_code}')
else:
    # Create
    resp = requests.post(f'{BASE}/wp-json/wp/v2/pages', headers=H, json={
        'title': 'Начало',
        'slug': 'nachalo',
        'content': DIVI_CONTENT,
        'status': 'publish',
        'meta': {'_et_pb_use_builder': 'on'},
    })
    home_id = resp.json().get('id')
    print(f'Created home page: {resp.status_code}, ID={home_id}')

# Assign as front page
r = requests.post(f'{BASE}/wp-json/wp/v2/settings', headers=H, json={
    'show_on_front': 'page',
    'page_on_front': home_id,
})
print(f'Assign as front page: {r.status_code}')

# Also set Divi builder meta
if home_id:
    # Need to set et_pb_use_builder meta — try via alternative REST
    resp2 = requests.post(f'{BASE}/wp-json/wp/v2/pages/{home_id}', headers=H, json={
        'meta': {'_et_pb_use_builder': 'on', '_et_pb_page_layout': 'et_full_width_page'}
    })
    print(f'Builder meta: {resp2.status_code}')

# Update menu НАЧАЛО to point to new page
menu_items = requests.get(f'{BASE}/wp-json/wp/v2/menu-items?menus=9&per_page=20', headers=H).json()
for it in menu_items:
    if it['title']['rendered'] == 'НАЧАЛО':
        requests.put(f'{BASE}/wp-json/wp/v2/menu-items/{it["id"]}', headers=H, json={
            'type': 'post_type',
            'object': 'page',
            'object_id': home_id,
            'url': '',
        })
        print(f'Menu item updated: {it["id"]}')
        break
