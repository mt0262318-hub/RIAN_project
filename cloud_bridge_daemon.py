
import time
import threading

def cloud_background_worker():
    print("[CLOUD WORKER] Non-blocking execution thread active on server...")
    while True:
        # Background task handling without freezing
        time.sleep(2)

if __name__ == "__main__":
    t = threading.Thread(target=cloud_background_worker, daemon=True)
    t.start()
    while True:
        time.sleep(10)
