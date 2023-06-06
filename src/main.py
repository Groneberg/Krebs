import os
import config

from dotenv import load_dotenv
from pathlib import Path



if __name__ == '__main__':
	dotenv_path = Path('../.env.local')
	load_dotenv(dotenv_path=dotenv_path)

	if not os.getenv('LABELBOX_API_KEY'):
		print('LABELBOX_API_KEY not set. Create a .env.local file in the root directory and set the key there.')
		exit(1)

	print(config.DIR_DATA)
