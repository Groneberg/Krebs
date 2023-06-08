import os
import config

from dotenv import load_dotenv
from pathlib import Path

from src import labelbox_annotations
from src import video_frame_thinning


def prepare_labelbox_dataset_for_yolo() -> int:
	print('Preparing labelbox dataset for YOLO...')
	dotenv_path = Path('../.env.local')
	load_dotenv(dotenv_path=dotenv_path)

	if not os.getenv('LABELBOX_API_KEY'):
		print('LABELBOX_API_KEY not set. Create a .env.local file in the root directory and set the key there.')
		return 1

	# Download labelbox annotations
	if not os.path.exists(config.DIR_CURRENT_DATASET):
		os.makedirs(config.DIR_CURRENT_DATASET)

	labelbox_annotations.download_project_json(
		os.getenv('LABELBOX_API_KEY'),
		config.LABELBOX_PROJECT_ID,
		config.LABELBOX_EXPORT_PARAMETERS
	)

	# Convert labelbox annotations to YOLO format
	if not os.path.exists(config.DIR_TRAINING):
		os.makedirs(config.DIR_TRAINING)
	labelbox_annotations.convert_to_yolo(
		input_json_path=config.LABELBOX_ANNOTATIONS_EXPORT_PATH,
		output_directory=config.DIR_TRAINING
	)

	# Download videos
	if not os.path.exists(config.DIR_VIDEOS):
		os.makedirs(config.DIR_VIDEOS)
	labelbox_annotations.download_project_videos(
		json_file_path=config.LABELBOX_ANNOTATIONS_EXPORT_PATH,
		output_dir=config.DIR_VIDEOS
	)

	# todo: extract frames from videos

	# Reduce the number of frames in the dataset by keeping only every nth frame
	if not os.path.exists(config.DIR_DISCARD):
		os.makedirs(config.DIR_DISCARD)
	video_frame_thinning.keep_nth_frame(
		source_dir=config.DIR_TRAINING,
		discard_dir=config.DIR_DISCARD,
		keep_nth_frame=config.THINNING_KEEP_NTH_FRAME
	)

	# todo: validate annotations

	# todo: scale video frames

	# todo: split dataset into train, test, (validation)

	# todo: augment dataset


def train_yolo():
	pass


def predict_yolo():
	pass


if __name__ == '__main__':
	prepare_labelbox_dataset_for_yolo()
