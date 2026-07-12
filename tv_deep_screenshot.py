#!/usr/bin/env python3
"""TradingView chart deep screenshot - tries to interact with page to load indicators."""

import os, sys, time, json
from playwright.sync_api import sync_playwright

URL = "https://tr.tradingview.com/chart/WfKlLjel/"
BASE = r"C:\Users\cagda\OneDrive\Masaüstü\open code mode"

def try_screenshot():
    print("[*] Playwright baslatiliyor...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="tr-TR",
            timezone_id="Europe/Istanbul",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        
        print("[*] Sayfa yukleniyor...")
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        print(f"[*] Sayfa basligi: {page.title()}")
        
        # Bekle - TradingView yavas yuklenir
        page.wait_for_timeout(15000)
        
        # Scroll down to see indicator panel
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)
        
        # Screenshot 1: full page
        page.screenshot(path=os.path.join(BASE, "tv_full.png"), full_page=True)
        print(f"[*] Tam sayfa screenshot alindi")
        
        # Screenshot 2: viewport (görünen alan)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(2000)
        page.screenshot(path=os.path.join(BASE, "tv_viewport.png"), full_page=False)
        print(f"[*] Viewport screenshot alindi")
        
        # Sayfadaki tüm metinleri al
        text = page.evaluate("document.body.innerText")
        with open(os.path.join(BASE, "tv_page_text.txt"), "w", encoding="utf-8") as f:
            f.write(text[:10000])
        print(f"[*] Sayfa metni kaydedildi ({len(text)} chars)")
        
        # TradingView indicator panelini ara
        indicators = page.evaluate("""() => {
            const all = [];
            document.querySelectorAll('*').forEach(el => {
                const style = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                if (rect.width > 50 && rect.height > 50 && style.backgroundColor && style.backgroundColor !== 'rgba(0, 0, 0, 0)') {
                    const text = el.textContent?.trim().substring(0, 50);
                    if (text && text.length > 0) {
                        all.push({tag: el.tagName, text: text, cls: el.className?.substring(0,60), w: Math.round(rect.width), h: Math.round(rect.height)});
                    }
                }
            });
            return JSON.stringify(all.slice(0, 100));
        }""")
        with open(os.path.join(BASE, "tv_elements.json"), "w", encoding="utf-8") as f:
            f.write(indicators)
        print(f"[*] Element bilgileri kaydedildi")
        
        browser.close()
        print("[*] Tamamlandi")
        
        # Dosya boyutlari
        for f in ["tv_full.png", "tv_viewport.png", "tv_page_text.txt", "tv_elements.json"]:
            path = os.path.join(BASE, f)
            if os.path.exists(path):
                print(f"  {f}: {os.path.getsize(path)} bytes")

if __name__ == "__main__":
    try_screenshot()
