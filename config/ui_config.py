# ui_config.py
from config.settings import UI_DIR

# UI Theme
THEME = "Soft"

# Logo and images
LOGO_PATH = UI_DIR / "images/icon_app.png"
COVER_PATH = UI_DIR / "images/landscape_cover.jpg"
ICON_PATH = UI_DIR / "images/landscape_icon.jpg"

# UI Texts
APP_TITLE = "Landscape Cafe & Eatery Chatbot"
WELCOME_TITLE = "☕ Landscape Cafe & Eatery Assistant 🌿"
WELCOME_MESSAGE = "Welcome to our cozy cafe! I'm here to help you with menu, promotions, and reservations."

# Example questions
EXAMPLES = [
    "Location and parking lots?",
    "เวลาเปิดปิดร้าน",
    "โปรโมชั่นประจำเดือน",
    "ขอรายการสินค้าที่มีพร้อมราคา",
    "Sales this month",
    "ตรวจสอบโต๊ะว่างขณะนี้และช่องทางติดต่อ"
] 