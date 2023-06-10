import glob
import os
import cv2
import albumentations as A


def run_augmentations(src_dir, output_path, amount=3):
    # Get all images and txts
    all_images = glob.glob(f"{os.path.join(src_dir, '')}*.jpg")
    all_txts = glob.glob(f"{os.path.join(src_dir, '')}*.txt")

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    for image in all_images:
        filename = os.path.basename(image)
        only_name = filename.split(".")[0]
        txt = [txt for txt in all_txts if only_name in txt][0]

        image = cv2.imread(image)

        with open(txt, "r") as f:
            lines = f.readlines()
            lines = [(line.replace("\n", "")[2:].split(" ") + [0]) for line in lines]

        for i, line in enumerate(lines):
            for x, num in enumerate(line):
                line[x] = round(float(num), 3)
            lines[i] = line

        for i in range(amount):
            try:
                augmented = augment_image(image, lines)
                cv2.imwrite(os.path.join(output_path, f"{only_name}_augmented_{i+1}.jpg"), augmented['image'])
                with open(os.path.join(output_path, f"{only_name}_augmented_{i+1}.txt"), "w") as f:
                    f.writelines(convert_tuple_to_writable_string(augmented['bboxes']))
            except ValueError as e:
                print(f"Error while augmenting {filename}: {e}")
                continue


def augment_image(image, bboxes):
    transform = A.Compose(
        [
            A.GaussNoise(var_limit=(1500.0, 1500.0), mean=0, per_channel=True, p=0.5),
            A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.5, 0.9), p=0.3),
            A.Blur(p=0.3),
            A.MedianBlur(p=0.3),
            A.CLAHE(p=0.3),
            A.RandomBrightnessContrast(p=0.3),
            A.RandomGamma(p=0.3),
            A.ImageCompression(quality_lower=75, p=0.3),
            A.HorizontalFlip(p=0.3),
            A.ShiftScaleRotate(p=0.3),
            A.RandomBrightnessContrast(p=0.3),
            A.RGBShift(p=0.3),
            A.RandomFog(fog_coef_lower=0.3, fog_coef_upper=1, alpha_coef=0.08, p=0.3),
        ],
        bbox_params=A.BboxParams(format='yolo')
    )
    return transform(image=image, bboxes=bboxes, category_ids=[0])


def convert_tuple_to_writable_string(tuple_list):
    return '\n'.join(['0 ' + ' '.join(map(str, tpl)).rstrip(' 0.0') for tpl in tuple_list])

