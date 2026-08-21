import os
import asyncio
from safety_visual_pipeline import VisualSafetyPipeline

class RianUIBridge:
    def __init__(self):
        self.visualizer = VisualSafetyPipeline()

    async def propose_ui_update(self, html_code, description):
        print("[1/3] Rendering UI Sandbox...")
        screenshot_path = await self.visualizer.render_preview_screenshot(html_code)
        
        print(f"[2/3] Sending UI Preview to Telegram Vault for Approval: {screenshot_path}")
        self.visualizer.send_approval_request_to_telegram(screenshot_path, description)
        
        print("[3/3] UI Proposal Queued for User Approval. No changes made to live site.")

if __name__ == '__main__':
    bridge = RianUIBridge()
    sample_html = "<html><body style='background:black; color:white; font-family:sans-serif; padding:20px;'><h1>R.I.A.N. UI Preview Ready</h1><p>Status: Sandbox Secure & Zero-Risk</p></body></html>"
    asyncio.run(bridge.propose_ui_update(sample_html, "Initial Dashboard Dark Mode Layout"))
    print("UI Approval Bridge Test Executed Successfully!")
