#!/usr/bin/env python3
"""TradingView screenshot - WebGL/shader destekli headless Chromium."""
import os, base64
from playwright.sync_api import sync_playwright

URL = "https://tr.tradingview.com/chart/WfKlLjel/"
BASE = r"C:\Users\cagda\OneDrive\Masaüstü\open code mode"

with sync_playwright() as p:
    # WebGL destekli Chromium
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--use-gl=angle",
            "--use-angle=swiftshader",  # software WebGL
            "--enable-webgl",
            "--ignore-gpu-blocklist",
            "--disable-gpu-sandbox",
            "--enable-unsafe-swiftshader",
        ]
    )
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        device_scale_factor=1,
        locale="tr-TR",
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    )
    page = context.new_page()
    
    page.goto(URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(15000)
    
    # WebGL destegi var mi kontrol et
    webgl_info = page.evaluate("""() => {
        const c = document.createElement('canvas');
        const gl = c.getContext('webgl2') || c.getContext('webgl');
        if (!gl) return 'NO_WEBGL';
        return {
            renderer: gl.getParameter(gl.RENDERER),
            vendor: gl.getParameter(gl.VENDOR),
            version: gl.getParameter(gl.VERSION)
        };
    }""")
    print(f"[*] WebGL: {webgl_info}")
    
    # Canvas'dan pixel data oku
    canvas_data = page.evaluate("""() => {
        const canvases = document.querySelectorAll('canvas');
        const results = [];
        canvases.forEach((c, i) => {
            const rect = c.getBoundingClientRect();
            if (rect.width > 50 && rect.height > 50) {
                try {
                    const ctx = c.getContext('2d');
                    if (ctx) {
                        const imgData = ctx.getImageData(0, 0, Math.min(rect.width, 200), Math.min(rect.height, 200));
                        let nonBlack = 0;
                        let total = imgData.data.length / 4;
                        for (let j = 0; j < imgData.data.length; j += 16) {
                            if (imgData.data[j] > 30 || imgData.data[j+1] > 30 || imgData.data[j+2] > 30) nonBlack++;
                        }
                        results.push({idx: i, w: Math.round(rect.width), h: Math.round(rect.height), nonBlackPixels: nonBlack, totalPixels: total});
                    } else {
                        results.push({idx: i, w: Math.round(rect.width), h: Math.round(rect.height), context: 'webgl_canvas'});
                    }
                } catch(e) {
                    results.push({idx: i, error: e.message});
                }
            }
        });
        return results;
    }""")
    print(f"[*] Canvas analizi:")
    for c in canvas_data:
        print(f"    Canvas {c['idx']}: {c['w']}x{c['h']} - non-black: {c.get('nonBlackPixels', '?')}/{c.get('totalPixels', '?')}")
    
    # Screenshot
    page.screenshot(path=os.path.join(BASE, "tv_webgl.png"), full_page=False)
    size = os.path.getsize(os.path.join(BASE, "tv_webgl.png"))
    print(f"[*] Screenshot: {size} bytes")
    
    browser.close()
