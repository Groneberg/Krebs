import labelbox
import json
import config
from pathlib import Path
from src.progress_bar import progress_bar, end_replaceable_progress_bar


def download_project_json(labelbox_api_key: str, project_id: str, export_parameters: dict) -> None:
	print('Exporting labelbox annotations...')

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


def convert_to_yolo(input_json_path: str, output_directory: str):
	print("Converting labels to YOLO format...")
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

		project_data = item['projects']
		if config.LABELBOX_PROJECT_ID not in project_data:
			skipped_videos.append(video_id)
			continue
		converted_videos.append(video_id)

		crayfish_project = project_data[config.LABELBOX_PROJECT_ID]
		frame_annotations = crayfish_project['labels'][0]['annotations']['frames']
		# Iterate over the frames inside the video folder
		for frame_index, frame_data in progress_bar(frame_annotations.items(), desc=f'Converting frames in {video_id}', replace_line=True):
			for object_id, object_data in frame_data['objects'].items():
				normalized_coords = yolo_normalize_bounding_box(media_height, media_width, object_data)

				# Get the detected object class name
				cls = object_data['name']
				if cls not in class_names:
					class_names.append(cls)

				# Create a line in YOLO format (class_index, xywh)
				line = class_names.index(cls), *normalized_coords

				true_frame_index = int(frame_index) - 1  # Convert the frame index to 0-based indexing
				label_path = output_directory / f'{video_id}-{true_frame_index}.txt'

				write_to_label_file(label_path, line)

	end_replaceable_progress_bar(f'Converted videos: {len(converted_videos)} | Skipped due to missing annotations: {len(skipped_videos)}')


def yolo_normalize_bounding_box(media_height, media_width, object_data):
	bounding_box = object_data['bounding_box']
	top, left, width, height = bounding_box['top'], bounding_box['left'], bounding_box['width'], bounding_box['height']

	normalized_coords = [
		(left + width / 2) / media_width,
		(top + height / 2) / media_height,
		width / media_width,
		height / media_height
	]
	return normalized_coords


def write_to_label_file(label_path, line):
	with open(label_path, 'a') as file:
		file.write(('%g ' * len(line)).rstrip() % line + '\n')

