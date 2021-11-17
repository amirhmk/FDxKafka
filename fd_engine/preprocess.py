import os
import glob
import argparse
from shutil import copy2

def copy_files(src_path, dst_path, img_extension="jpg"):
    filenames = glob.glob(f"{src_path}/*.{img_extension}")
    for f in filenames:
        parent_dir, filename = os.path.split(f)
        image_class, image_id, ext = filename.split(".")
        copy2(f, f"{dst_path}/{image_class}/")


def create_dirs(dst_path="data/train"):
    os.makedirs(dst_path, exist_ok=True)

    # Create cat subdir
    os.makedirs(f"{dst_path}/cat", exist_ok=True)

    # create dog subclass
    os.makedirs(f"{dst_path}/dog", exist_ok=True)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--src", type=str, required=True)
    parser.add_argument("--dst", type=str, default="data/train")

    args = parser.parse_args()

    create_dirs(args.dst)
    copy_files(args.src, args.dst)

if __name__ == "__main__":
    main()
