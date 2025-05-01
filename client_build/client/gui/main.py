from client.config import load_url_info
import sys
import os

sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')
load_url_info()
from client.gui.async_client import main
main()
