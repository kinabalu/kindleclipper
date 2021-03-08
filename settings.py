import os
import platform

from dotenv import load_dotenv
load_dotenv()

system_platform = platform.system()

platform_clippings_path = './My\ Clippings.txt'

if system_platform == 'Darwin':
    platform_clippings_path = "/Volumes/Kindle/documents/My Clippings.txt"
elif system_platform == 'Windows':
    platform_clippings_path = "C:\Kindle\documents\My Clippings.txt"
elif system_platform == 'Linux':
    platform_clippings_path = "/media/Kindle/documents/My Clippings.txt"

MY_CLIPPINGS_PATH = platform_clippings_path
AMAZON_USERNAME = os.getenv("AMAZON_USERNAME", "")
AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD", "")
AMAZON_COOKIE = os.getenv("AMAZON_COOKIE", "")
