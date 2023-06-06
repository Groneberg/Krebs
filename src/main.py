import os
import config

from dotenv import load_dotenv
from pathlib import Path

import src.labelbox_annotations as labelbox_annotations


def prepare_labelbox_dataset_for_yolo() -> int:
	dotenv_path = Path('../.env.local')
	load_dotenv(dotenv_path=dotenv_path)

	if not os.getenv('LABELBOX_API_KEY'):
		print('LABELBOX_API_KEY not set. Create a .env.local file in the root directory and set the key there.')
		return 1

	if not os.path.exists(config.DIR_CURRENT_DATASET):
		os.makedirs(config.DIR_CURRENT_DATASET)

	labelbox_annotations.download_json(os.getenv('LABELBOX_API_KEY'))

	# todo: download videos from labelbox

	# todo: extract frames from videos

	# todo: thin out frames

	# todo: validate annotations

	# todo: split dataset into train, test, (validation)

	# todo: augment dataset


if __name__ == '__main__':
	prepare_labelbox_dataset_for_yolo()
