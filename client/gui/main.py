from ..config import load_url_info
import sys
import os


if __name__ == '__main__':
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    load_url_info()
    from .async_client import main
    main()
