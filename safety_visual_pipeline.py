import os
import asyncio
from playwright.async_api import async_playwright
import requests

class VisualSafetyPipeline:
    def __init__(self, output_dir="./vault_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    async def render_preview_screenshot(self, html_content, filename="ui_preview.png"):
        sandbox_path = os.path.join(self.output_dir, "sandbox.html")
        with open(sandbox_path, "w", encoding="utf-8") as sf:
            sf.write(html_content)

        screenshot_path = os.path.join(self.output_dir, filename)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_viewport_size({"width": 375, "height": 812})
            await page.goto(f"file://{os.path.abspath(sandbox_path)}")
            await page.screenshot(path=screenshot_path, full_page=True)
            await browser.close()

        return screenshot_path

    def send_approval_request_to_telegram(self, image_path, description="New UI Proposal"):
        token = os.getenv("TELEGRAM_BOT_TOKEN") or "7507914035:AAHQv7F6w..." # Yahan apna bot token hai
        chat_id = os.getenv("TELEGRAM_CHAT_ID") or "YOUR_CHAT_ID"

        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        with open(image_path, "rb") as img:
            response = requests.post(
                url,
                data={
                    "chat_id": chat_id, 
                    "caption": f"🛡️ R.I.A.N. UI PROPOSAL REVIEW\n\n{description}\n\nReply 'APPROVE' to deploy or 'REJECT' to discard."
                },
                files={"photo": img}
            )
        
        if response.status_code == 200:
            os.remove(image_path)
            return True
        return False

print('VisualSafetyPipeline module ready!')
