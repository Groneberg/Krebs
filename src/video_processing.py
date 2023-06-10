import os
import cv2
import config
import requests
import math
import json
from src.progress_bar import progress_bar, end_replaceable_progress_bar


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
                        total_length=math.floor(total_size / chunk_size),
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


def extract_and_resize_frames_from_videos():
    if os.path.isdir(config.DIR_TRAINING):
        for file in os.listdir(config.DIR_TRAINING):
            if file.endswith('txt'):
                video_frame = file[:-4]
                video_id, frame = video_frame.split('-')
                video_file = f'{video_id}.mp4'
                if not os.path.exists(f'{config.DIR_VIDEOS}/{video_file}'):
                    print(f'Video with ID "{video_id}" was not found in Videos Folder')
                else:
                    video = cv2.VideoCapture(f'{config.DIR_VIDEOS}/{video_file}')
                    video.set(cv2.CAP_PROP_POS_FRAMES, int(frame))
                    ret, frame = video.read()
                    image = cv2.resize(frame, (640, 360))
                    cv2.imwrite(f'{config.DIR_TRAINING}/{video_frame}.jpg', image)
