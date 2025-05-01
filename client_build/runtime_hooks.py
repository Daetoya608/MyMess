# runtime_hooks.py
import sys
import os

# Фикс для поиска ресурсов в собранном приложении
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    sys.path.insert(0, os.path.join(base_path, 'client'))
else:
    base_path = os.path.dirname(__file__)
