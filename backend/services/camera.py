from dotenv import load_dotenv

try:
    from openocd import _ssh
except:
    from backend.services.openocd import _ssh

load_dotenv()