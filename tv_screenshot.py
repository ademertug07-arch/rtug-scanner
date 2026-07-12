#!/usr/bin/env python3
"""Take a screenshot of a TradingView chart using Playwright (headless Chromium)."""

import sys
import os
from playwright.sync_api import sync_playwright, TimeoutError

URL = "https://tr.tradingview.com/chart/WfKlLjel/"
OUTPUT = r"C:\Users\cagda\OneDrive\Masaüstü\open code mode\tv_live.png"

def take_screenshot(url: str, output_path: str) -> bool:
    print(f"[*] Playwright ile {url} adresine gidiliyor...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()
            
            print("[*] Sayfa yukleniyor...")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            print("[*] Sayfa yuklendi, bekleniyor...")
            page.wait_for_timeout(8000)
            
            print(f"[*] Screenshot aliniyor: {output_path}")
            page.screenshot(path=output_path, full_page=False)
            
            size = os.path.getsize(output_path)
            print(f"[*] Screenshot kaydedildi: {size} bytes")
            
            browser.close()
            return size > 1000
    except TimeoutError:
        print("[!] Sayfa yukleme zaman asimi")
        return False
    except Exception as e:
        print(f"[!] Hata: {e}")
        return False

if __name__ == "__main__":
    success = take_screenshot(URL, OUTPUT)
    if success:
        print(f"[OK] Screenshot basarili: {OUTPUT}")
    else:
        print("[FAIL] Screenshot alinamadi")
