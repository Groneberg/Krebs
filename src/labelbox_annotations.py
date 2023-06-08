import labelbox
import json
import config
from pathlib import Path
from src.progress_bar import progress_bar


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

	with open(input_json_path) as f:
		data = json.load(f)

	# Iterate over the JSON data to find the annotations for the current frame
	for item in data:
		video_id = item['data_row']['id']

		project_data = item['projects']
		if config.LABELBOX_PROJECT_ID not in project_data:
			# print(f'Warning: No crayfish project annotations found for video {video_id}')
			skipped_videos.append(video_id)
			continue

		converted_videos.append(video_id)

		crayfish_project = project_data[config.LABELBOX_PROJECT_ID]
		frame_annotations = crayfish_project['labels'][0]['annotations']['frames']
		# Iterate over the frames inside the video folder
		for frame_index in progress_bar(frame_annotations, desc=f'Converting frames in {video_id}', over_printable=True):

			media_height = item['media_attributes']['height']
			media_width = item['media_attributes']['width']

			# Process each frame image separately
			frame_data = frame_annotations[str(frame_index)]

			for object_id, object_data in frame_data['objects'].items():
				# Extract the bounding box coordinates
				top = object_data['bounding_box']['top']
				left = object_data['bounding_box']['left']
				height = object_data['bounding_box']['height']
				width = object_data['bounding_box']['width']

				# Normalize the bounding box coordinates
				normalized_coords = [
					(left + width / 2) / media_width,
					(top + height / 2) / media_height,
					width / media_width,
					height / media_height
				]

				# Get the class name
				cls = object_data['name']

				# Add the class name to the list of names if it's not already present
				if cls not in class_names:
					class_names.append(cls)

				# Create a line in YOLO format (class_index, xywh)
				line = class_names.index(cls), *normalized_coords

				true_frame_index = int(frame_index) - 1  # Convert the frame index to 0-based indexing
				label_path = output_directory / f'{video_id}-{true_frame_index}.txt'

				with open(label_path, 'a') as f:
					f.write(('%g ' * len(line)).rstrip() % line + '\n')  # Write the line to the label file

	print(f'\rConverted videos: {len(converted_videos)} | Skipped missing annotations: {len(skipped_videos)}')
	print()  # Cancel out the \r from the progress bar
