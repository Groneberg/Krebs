import os

from src.progress_bar import progress_bar


def id_and_frame_index_sorting_key(filename):
	# Extract the ID and index from the filename
	parts = filename.split('-')
	id_part = parts[0]
	index_part = int(parts[-1].split('.')[0])

	# Return a tuple with the ID and index as sorting keys
	return id_part, index_part


def get_frame_index(filename):
	return int(filename.split('-')[-1].split('.')[0])


def get_video_id(filename):
	return filename.split('-')[0]


def keep_nth_frame(source_dir, discard_dir, keep_nth_frame=30):
	print(f'Thinning dataset. Keeping every {keep_nth_frame}th frame...')
	last_video_id = None
	last_kept_frame_index = None

	files = sorted(os.listdir(source_dir), key=id_and_frame_index_sorting_key)
	for file in progress_bar(files, 'Thinning out frames', over_printable=True):
		# skip non-txt files
		if not file.endswith('.txt'):
			continue

		# reset if new video
		current_video_id = get_video_id(file)
		if not current_video_id == last_video_id:
			last_video_id = current_video_id
			last_kept_frame_index = None

		current_frame_index = get_frame_index(file)
		keep = False

		# keep every nth frame of the same video
		if last_kept_frame_index is None or current_frame_index - last_kept_frame_index >= keep_nth_frame:
			last_kept_frame_index = current_frame_index
			keep = True

		# move to discard dir if not kept
		if not keep:
			os.rename(os.path.join(source_dir, file), os.path.join(discard_dir, file))

			# if there is a jpg file, move that too
			jpeg_file = file.replace('.txt', '.jpg')
			if os.path.exists(os.path.join(source_dir, jpeg_file)):
				os.rename(os.path.join(source_dir, jpeg_file), os.path.join(discard_dir, jpeg_file))

	print('\rDone thinning out frames.')
	print()  # Cancel out the \r from the progress bar
