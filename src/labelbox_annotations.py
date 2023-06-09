import labelbox
import requests

import os
import json
import math
from pathlib import Path

import config
from src.progress_bar import progress_bar, end_replaceable_progress_bar


def download_project_json(labelbox_api_key: str, project_id: str, export_parameters: dict) -> None:
	print('Downloading labelbox annotations json...')

	client = labelbox.Client(api_key=labelbox_api_key)
	project = client.get_project(project_id)
	labels_process = project.export_v2(params=export_parameters)

	labels_process.wait_till_done()
	if labels_process.errors:
		print(labels_process.errors)
		return

	export_json = labels_process.result

	# save to file
	with open(config.LABELBOX_ANNOTATIONS_EXPORT_PATH, 'w') as file:
		json.dump(export_json, file)
		print(f'Exported labelbox annotations to {config.LABELBOX_ANNOTATIONS_EXPORT_PATH}')


def download_project_videos(input_json_path: str, output_dir: str) -> None:
	print('Downloading videos...')
	with open(input_json_path) as file:
		data = json.load(file)

	for item in data:
		video_url = item['data_row']['row_data']
		video_id = item['data_row']['id']
		file_name = video_id + '.mp4'
		print(f'\rDownloading video: {video_id}...', end='')

		# Skip videos that do not have the correct project ID
		project_data = item['projects']
		if config.LABELBOX_PROJECT_ID not in project_data:
			print(f'\rSkipping video {video_id} because it does not contain annotations for the current project')
			continue

		output_path = os.path.join(output_dir, file_name)
		temp_output_path = output_path + '.part'  # Temporary file path

		# Don't download the video if it already exists
		if os.path.exists(output_path):
			print(f'\rVideo {video_id} already exists, skipping')
			continue

		try:
			response = requests.get(video_url, stream=True)
			response.raise_for_status()

			total_size = int(response.headers.get('Content-Length', 0))
			chunk_size = 8192  # 8 KiB

			with open(temp_output_path, 'wb') as outfile:
				for chunk in progress_bar(
						response.iter_content(chunk_size=chunk_size),
						total_length=math.floor(total_size/chunk_size),
						desc=f'Downloading video: {video_id}...',
						replace_line=True
				):
					outfile.write(chunk)

			# Rename the temporary file to the final output path
			os.rename(temp_output_path, output_path)

			print(f'\rDownloaded video: {video_id}')

		except KeyboardInterrupt:
			# User interrupted the download
			end_replaceable_progress_bar(f'KeyboardInterrupt: Download of video {video_id} interrupted by the user.')
			# Remove the temporary file if it exists
			if os.path.exists(temp_output_path):
				os.remove(temp_output_path)
			break  # Exit the loop and stop downloading further videos

		except Exception as e:
			end_replaceable_progress_bar(f'Error downloading video {video_id}: {e}')
			# Delete the temporary file if an error occurs
			if os.path.exists(temp_output_path):
				os.remove(temp_output_path)
			break

	end_replaceable_progress_bar('Finished downloading videos')


def remove_invalid_videos_from_annotations(input_json_path: str) -> None:
	print('Removing invalid video annotations...')
	with open(input_json_path) as file:
		data = json.load(file)

	original_video_count = len(data)
	kept_video_count = 0

	updated_data = []
	for item in data:
		if _get_frame_annotations(item) is not None:
			updated_data.append(item)
			kept_video_count += 1

	with open(input_json_path, 'w') as file:
		json.dump(updated_data, file)

	print(f'Finished removing video annotations without project data, kept {kept_video_count} out of {original_video_count} videos')


def thin_out_frame_annotations(input_json_path: str, keep_nth_frame: int):
	print(f'Thinning out frame annotations, keeping every {keep_nth_frame}th frame...')
	original_frame_count = 0
	kept_frame_count = 0

	with open(input_json_path) as file:
		data = json.load(file)

	for item in data:
		frame_annotations = _get_frame_annotations(item)
		if frame_annotations is None:
			continue
		original_frame_count += len(frame_annotations)

		kept_frames = {}
		last_kept_frame_index = None

		for frame_index, frame_data in frame_annotations.items():
			current_frame_index = int(frame_index)
			keep = False

			if last_kept_frame_index is None or current_frame_index - last_kept_frame_index >= keep_nth_frame:
				last_kept_frame_index = current_frame_index
				keep = True

			if keep:
				kept_frames[frame_index] = frame_data

		kept_frame_count += len(kept_frames)
		_set_frame_annotations(item, kept_frames)

	with open(input_json_path, 'w') as file:
		json.dump(data, file, indent=4)

	print(f'Finished thinning out frame annotations, kept {kept_frame_count} out of {original_frame_count} frames')


def _get_frame_annotations(item):
	project_data = item['projects']
	if config.LABELBOX_PROJECT_ID not in project_data:
		return
	current_project = project_data[config.LABELBOX_PROJECT_ID]
	labels = current_project['labels']
	if not labels or len(labels) <= 0:
		return
	return labels[0]['annotations']['frames']


def _set_frame_annotations(item, frame_annotations):
	project_data = item['projects']
	if config.LABELBOX_PROJECT_ID not in project_data:
		return
	current_project = project_data[config.LABELBOX_PROJECT_ID]
	current_project['labels'][0]['annotations']['frames'] = frame_annotations


def convert_to_yolo(input_json_path: str, output_directory: str):
	print('Converting labels to YOLO format...')
	converted_videos = []
	skipped_videos = []
	class_names = []

	output_directory = Path(output_directory)  # Convert the output directory to a Path object

	with open(input_json_path) as file:
		data = json.load(file)

	# Iterate over the JSON data to find the annotations for the current frame
	for item in data:
		video_id = item['data_row']['id']
		media_height = item['media_attributes']['height']
		media_width = item['media_attributes']['width']

		frame_annotations = _get_frame_annotations(item)
		if frame_annotations is None:
			skipped_videos.append(video_id)
			continue
		converted_videos.append(video_id)

		# Iterate over the frames inside the video folder
		for frame_index, frame_data in progress_bar(frame_annotations.items(), desc=f'Converting frames in {video_id}', replace_line=True):
			for object_id, object_data in frame_data['objects'].items():
				normalized_coords = _yolo_normalize_bounding_box(media_height, media_width, object_data)

				# Get the detected object class name
				cls = object_data['name']
				if cls not in class_names:
					class_names.append(cls)

				# Create a line in YOLO format (class_index, xywh)
				line = class_names.index(cls), *normalized_coords

				true_frame_index = int(frame_index) - 1  # Convert the frame index to 0-based indexing
				label_path = output_directory / f'{video_id}-{true_frame_index}.txt'

				_write_to_label_file(label_path, line)

	end_replaceable_progress_bar(f'Converted videos: {len(converted_videos)} | Skipped due to missing annotations: {len(skipped_videos)}')


def _yolo_normalize_bounding_box(media_height, media_width, object_data):
	bounding_box = object_data['bounding_box']
	top, left, width, height = bounding_box['top'], bounding_box['left'], bounding_box['width'], bounding_box['height']

	normalized_coords = [
		(left + width / 2) / media_width,
		(top + height / 2) / media_height,
		width / media_width,
		height / media_height
	]
	return normalized_coords


def _write_to_label_file(label_path, line):
	with open(label_path, 'a') as file:
		file.write(('%g ' * len(line)).rstrip() % line + '\n')

