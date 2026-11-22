import os
import subprocess
import click
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

def handle_load_more(page, max_clicks=50):
    """بيدور على زرار Load More ويدوس عليه لحد ما يختفي"""
    for _ in range(max_clicks):
        btn = page.locator("button:has-text('Load more'), button:has-text('عرض المزيد')")
        if btn.count() > 0 and btn.first.is_visible():
            btn.first.click()
            page.wait_for_timeout(1500)
        else:
            break

def scroll_to_bottom(page):
    """بديل لو الموقع بيستخدم infinite scroll"""
    last_height = page.evaluate("document.body.scrollHeight")
    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

@click.command()
@click.argument('url')
@click.option('--video', is_flag=True, help='حمّل فيديو باستخدام yt-dlp')
@click.option('--cookies-from-browser', default=None, help='مرر كوكيز من المتصفح لو الموقع محتاج تسجيل دخول')
def main(url, video, cookies_from_browser):
    if video:
        # تحميل فيديو
        cmd = ["yt-dlp", url]
        if cookies_from_browser:
            cmd += ["--cookies-from-browser", cookies_from_browser]
        subprocess.run(cmd)
    else:
        # تحميل صور: نفتح الصفحة بـ Playwright الأول عشان نحل مشكلة Load More
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=os.getenv("CHROMIUM_PATH"),
                headless=True,
                args=['--no-sandbox', '--disable-gpu']
            )
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            
            handle_load_more(page)
            scroll_to_bottom(page)
            
            # بعد ما كل حاجة ظهرت، ناخد الـ HTML النهائي
            html = page.content()
            browser.close()
        
        # نحفظ الـ HTML مؤقتاً ونسلمه لـ gallery-dl
        temp_html = "/tmp/page_loaded.html"
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html)
        
        subprocess.run(["gallery-dl", "--input-file", temp_html, "-d", "./downloads"])

if __name__ == '__main__':
    main()
