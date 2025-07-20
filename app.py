from main import *

if __name__ == "__main__":
    # Optionally: sync database from CSVs on startup
    # csvs_to_sqlite()  # Uncomment if you want to auto-sync DB
    app = create_app(chat, clear_chat)
    app.launch(debug=settings.DEBUG) 