import os

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

DIR_DATA = os.path.join(PROJECT_PATH, 'data')
DIR_CURRENT_DATASET = os.path.join(DIR_DATA, 'crawfish_dataset_v1')

# dataset
DIR_TRAINING = os.path.join(DIR_CURRENT_DATASET, 'train')
DIR_VALIDATION = os.path.join(DIR_CURRENT_DATASET, 'validate')
DIR_TEST = os.path.join(DIR_CURRENT_DATASET, 'test')
DIR_DISCARD = os.path.join(DIR_CURRENT_DATASET, 'discard')

# dataset reduction
THINNING_KEEP_NTH_FRAME = 30


# labelbox
LABELBOX_PROJECT_ID = 'cliae24in02sz07yi2f7ves6h'
# see: https://docs.labelbox.com/reference/label-export
LABELBOX_EXPORT_PARAMETERS = {
	"data_row_details": False,
	"metadata": False,
	"attachments": False,
	"project_details": False,
	"performance_details": False,
	"label_details": False,
	"interpolated_frames": False
}
LABELBOX_ANNOTATIONS_EXPORT_PATH = os.path.join(DIR_CURRENT_DATASET, 'labelbox_export.json')

