# ============================================================
# BGАлтернатива - Главен оркестратор
# Пуска се веднъж на ден (напр. с cron или Task Scheduler)
# ============================================================

import time
from datetime import datetime
from config import ARTICLES_SCHEDULE, WP_CATEGORIES
from news_scraper import fetch_all
from news_rewriter import rewrite_article, rewrite_analysis
from wordpress_poster import post_article, setup_categories


def run():
    print(f"\n{'='*50}")
    print(f"BGАлтернатива Автоматизация")
    print(f"Стартирано: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print(f"{'='*50}\n")

    # Стъпка 1: Създай категории ако не съществуват
    setup_categories(WP_CATEGORIES)

    # Стъпка 2: Вземи статии от RSS
    print("\nСкрейпвам новини...")
    raw_articles = fetch_all(ARTICLES_SCHEDULE)

    # Стъпка 3: Преработи и публикувай
    total_published = 0

    for category, articles in raw_articles.items():
        print(f"\n--- {category} ({len(articles)} статии) ---")

        for article in articles:
            print(f"  Преработвам: {article['title'][:50]}...")

            # Анализите се преработват по-задълбочено
            if category == "Анализи":
                rewritten = rewrite_analysis(article)
            else:
                rewritten = rewrite_article(article)

            if rewritten:
                success = post_article(rewritten)
                if success:
                    total_published += 1

            # Пауза между заявките (не претоварваме API-то)
            time.sleep(2)

    print(f"\n{'='*50}")
    print(f"Готово! Публикувани: {total_published} статии")
    print(f"Завършено: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run()
