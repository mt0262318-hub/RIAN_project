# Safe CSS and UI Injector for Glassmorphism Input Bar
import os

print("Injecting glassmorphism modern input bar safely...")
# Yeh script bina purana code udaye sirf UI styling inject karegi

# Adding Streamlit Component for Glassmorphism Input Bar with Plus and Mic
import streamlit.components.v1 as components

modern_input_html = """
<div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); width: 85%; max-width: 800px; background: rgba(15, 25, 35, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(0, 240, 255, 0.4); border-radius: 30px; padding: 10px 20px; display: flex; align-items: center; box-shadow: 0 0 20px rgba(0, 240, 255, 0.2); z-index: 9999;">
    <button style="background: none; border: none; color: #00f0ff; font-size: 22px; cursor: pointer; margin-right: 12px;" title="Upload Image">+</button>
    <input type="text" placeholder="Ask R.I.A.N. or type command..." style="background: transparent; border: none; outline: none; color: #fff; font-size: 16px; flex-grow: 1; padding: 5px;">
    <button style="background: none; border: none; color: #00f0ff; font-size: 18px; cursor: pointer; margin: 0 10px;" title="Voice Dictation">🎙️</button>
    <button style="background: #00f0ff; border: none; color: #000; font-weight: bold; padding: 8px 18px; border-radius: 20px; cursor: pointer;">Send</button>
</div>
"""
print("Modern glass input component prepared safely.")
