import os
import labelbox
import json
import config


def download_json(labelbox_api_key: str) -> None:
	print('Exporting labelbox annotations...')

	client = labelbox.Client(api_key=labelbox_api_key)
	project = client.get_project(config.LABELBOX_PROJECT_ID)
	labels_process = project.export_v2(params=config.LABELBOX_EXPORT_PARAMETERS)

	labels_process.wait_till_done()
	if labels_process.errors:
		print(labels_process.errors)
		return

	export_json = labels_process.result

	# save to file
	with open(config.LABELBOX_ANNOTATIONS_EXPORT_PATH, 'w') as file:
		json.dump(export_json, file)
		print(f'Exported labelbox annotations to {config.LABELBOX_ANNOTATIONS_EXPORT_PATH}')
