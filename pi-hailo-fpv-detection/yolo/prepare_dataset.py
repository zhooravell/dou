#!/usr/bin/env python3
"""
Розділяє датасет на train/val/test для YOLOv8.

Використання:
    python3 prepare_dataset.py --images images/ --labels labels/
"""

import argparse
import os
import random
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Підготовка датасету YOLOv8")
    parser.add_argument("--images", required=True, help="Папка з зображеннями")
    parser.add_argument("--labels", required=True, help="Папка з .txt лейблами")
    parser.add_argument("--output", default="drone_dataset", help="Вихідна папка")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    # Збір зображень
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    all_images = sorted([
        f for f in os.listdir(args.images)
        if Path(f).suffix.lower() in exts
    ])
    random.shuffle(all_images)

    # Статистика
    matched = 0
    no_label = 0
    for img in all_images:
        lbl = os.path.join(args.labels, Path(img).stem + ".txt")
        if os.path.exists(lbl):
            matched += 1
        else:
            no_label += 1

    print(f"═══ Статистика ═══")
    print(f"  Зображень:    {len(all_images)}")
    print(f"  З лейблами:   {matched}")
    print(f"  Без лейблів:  {no_label}")

    # Розділення 80/15/5
    n = len(all_images)
    train_end = int(n * 0.80)
    val_end = int(n * 0.95)

    splits = {
        "train": all_images[:train_end],
        "val":   all_images[train_end:val_end],
        "test":  all_images[val_end:],
    }

    # Копіювання
    for split, files in splits.items():
        img_dir = os.path.join(args.output, "images", split)
        lbl_dir = os.path.join(args.output, "labels", split)
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(lbl_dir, exist_ok=True)

        for img_file in files:
            stem = Path(img_file).stem
            shutil.copy2(
                os.path.join(args.images, img_file),
                os.path.join(img_dir, img_file),
            )
            label_src = os.path.join(args.labels, stem + ".txt")
            if os.path.exists(label_src):
                shutil.copy2(label_src, os.path.join(lbl_dir, stem + ".txt"))
            else:
                open(os.path.join(lbl_dir, stem + ".txt"), "w").close()

        print(f"  {split}: {len(files)} зображень")

    # dataset.yaml
    abs_path = os.path.abspath(args.output)
    yaml_content = f"""path: {abs_path}
train: images/train
val: images/val
test: images/test

nc: 1
names:
  0: fpv_drone
"""
    yaml_path = os.path.join(args.output, "dataset.yaml")
    with open(yaml_path, "w") as f:
        f.write(yaml_content)

    print(f"\n✓ Датасет готовий: {args.output}/")
    print(f"✓ Конфіг: {yaml_path}")


if __name__ == "__main__":
    main()
