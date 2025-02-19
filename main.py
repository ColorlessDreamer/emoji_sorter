import threading
from app import app
from bot import run_bot

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Run Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # Run the bot in the main thread
    run_bot()