import string
import random

CHARACTERS = string.ascii_letters + string.digits

def generate_short_code(length: int = 6) -> str:
    """Generate a random 6-character short code."""
    return "".join(random.choices(CHARACTERS, k=length))

def parse_user_agent(user_agent: str) -> dict:
    """Parse device type and browser from User-Agent string."""
    ua = user_agent.lower() if user_agent else ""

    # Device type
    if any(x in ua for x in ["mobile", "android", "iphone"]):
        device_type = "Mobile"
    elif "tablet" in ua or "ipad" in ua:
        device_type = "Tablet"
    else:
        device_type = "Desktop"

    # Browser
    if "chrome" in ua and "edg" not in ua:
        browser = "Chrome"
    elif "firefox" in ua:
        browser = "Firefox"
    elif "safari" in ua and "chrome" not in ua:
        browser = "Safari"
    elif "edg" in ua:
        browser = "Edge"
    else:
        browser = "Other"

    return {"device_type": device_type, "browser": browser}
