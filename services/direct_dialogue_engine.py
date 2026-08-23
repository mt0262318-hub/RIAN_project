import json

def get_dialogue_reply(prompt: str) -> str:
    p = prompt.strip().lower()
    if "joke" in p:
        return "Pappu ne dost se pucha: Zindagi me kitna aage badhna chahiye? Dost bola: Itna ki peeche mudkar dekhna na pade, bas wiper chalate raho!"
    elif "who are you" in p or "kaun ho" in p:
        return "Main RIAN hoon, aapka autonomous AI neural assistant."
    elif "kya kar sakte ho" in p or "what can you do" in p:
        return "Main apps open kar sakta hoon, background automation run kar sakta hoon aur aapse real time baatchit kar sakta hoon."
    elif "hello" in p or "hi" in p or "online" in p:
        return "Haan Manish, main bilkul online hoon aur aapki aawaz sun raha hoon."
    else:
        return f"Aapka request '{prompt}' process ho gaya hai."

