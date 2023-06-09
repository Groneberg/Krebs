import glob
import random
import os
import shutil
from config import DIR_TRAINING, DIR_VALIDATION


def split_dataset(input_dir):
    if not os.path.exists(input_dir):
        raise Exception(f"Dir {input_dir} not found.")

    # Get all images and randomize order
    all_images = glob.glob(f"{os.path.join(input_dir, '')}*.jpg")
    random.shuffle(all_images)

    # Calculate 5% for validation dataset
    length = len(all_images)
    validation_length = int(length * 0.05)

    # Slice dist to create dataset
    validation_dataset = all_images[:validation_length]
    train_dataset = all_images[validation_length:]

    # Create directories if not exists
    if not os.path.exists(DIR_TRAINING):
        os.mkdir(DIR_TRAINING)

    if not os.path.exists(DIR_VALIDATION):
        os.mkdir(DIR_VALIDATION)

    move_dataset(validation_dataset)
    move_dataset(train_dataset, train=True)


def move_dataset(dataset, train=False):
    for image in dataset:
        if os.path.exists(image):
            # Split name
            filename = os.path.basename(image)
            only_name = filename.split(".")[0]

            # move file
            shutil.move(image, os.path.join(DIR_TRAINING if train else DIR_VALIDATION, filename))
            shutil.move(os.path.join(os.path.dirname(image), f"{only_name}.txt"),
                        os.path.join(DIR_TRAINING if train else DIR_VALIDATION, f"{only_name}.txt"))
