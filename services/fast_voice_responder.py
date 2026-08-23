import asyncio

def get_quick_response(prompt: str) -> str:
    prompt_lower = prompt.lower()
    if "joke" in prompt_lower:
        return "Teacher: Batao sabse purana ped kaunsa hai? Student: Khajoor ka, kyunki woh sabse uncha hai!"
    if "online" in prompt_lower or "hello" in prompt_lower:
        return "Haan Manish, main fully online hoon. Kya task karna hai?"
    return f"Main aapka command '{prompt}' process kar raha hoon."

if __name__ == "__main__":
    print("[✓] Fast Voice Responder Ready")
