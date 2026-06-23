#!/usr/bin/env python3
"""
Конвертує лейбли з полігонного формату (x1 y1 x2 y2 x3 y3 x4 y4)
у стандартний YOLO формат (x_center y_center width height).

Використання:
    python3 convert_labels.py --input labels/ --output labels_yolo/
    python3 convert_labels.py --input labels/ --output labels_yolo/ --preview
"""

import argparse
import os
from pathlib import Path

def polygon_to_yolo(parts):
    """
    Конвертує полігон (4 точки) у YOLO bbox.

    Вхід:  [class, x1, y1, x2, y2, x3, y3, x4, y4]
    Вихід: [class, x_center, y_center, width, height]
    """
    cls_id = int(parts[0])
    coords = list(map(float, parts[1:]))

    # Витягнути всі x та y координати
    xs = coords[0::2]  # x1, x2, x3, x4
    ys = coords[1::2]  # y1, y2, y3, y4

    x_min = min(xs)
    x_max = max(xs)
    y_min = min(ys)
    y_max = max(ys)

    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    width = x_max - x_min
    height = y_max - y_min

    return cls_id, x_center, y_center, width, height


def main():
    parser = argparse.ArgumentParser(description="Конвертація полігонів → YOLO")
    parser.add_argument("--input", required=True, help="Папка з полігонними лейблами")
    parser.add_argument("--output", required=True, help="Папка для YOLO лейблів")
    parser.add_argument("--preview", action="store_true", help="Показати перші 5 конвертацій")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    files = sorted([f for f in os.listdir(args.input) if f.endswith(".txt")])
    print(f"Знайдено {len(files)} файлів лейблів")

    converted = 0
    skipped = 0
    errors = 0
    preview_count = 0

    for fname in files:
        input_path = os.path.join(args.input, fname)
        output_path = os.path.join(args.output, fname)

        yolo_lines = []

        with open(input_path) as f:
            for line_num, line in enumerate(f, 1):
                parts = line.strip().split()

                if not parts:
                    continue

                if len(parts) == 5:
                    # Вже YOLO формат — копіюємо як є
                    yolo_lines.append(line.strip())
                    continue

                if len(parts) == 9:
                    # Полігон: class x1 y1 x2 y2 x3 y3 x4 y4
                    try:
                        cls_id, xc, yc, w, h = polygon_to_yolo(parts)
                        yolo_line = f"{cls_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}"
                        yolo_lines.append(yolo_line)

                        if args.preview and preview_count < 5:
                            print(f"\n  {fname} line {line_num}:")
                            print(f"    Було:  {line.strip()}")
                            print(f"    Стало: {yolo_line}")
                            preview_count += 1

                    except (ValueError, IndexError) as e:
                        print(f"  ⚠ {fname}:{line_num} помилка: {e}")
                        errors += 1
                else:
                    print(f"  ⚠ {fname}:{line_num} невідомий формат ({len(parts)} значень)")
                    errors += 1

        with open(output_path, "w") as f:
            f.write("\n".join(yolo_lines))
            if yolo_lines:
                f.write("\n")

        if yolo_lines:
            converted += 1
        else:
            skipped += 1

    print(f"\n═══ Результат ═══")
    print(f"  Конвертовано: {converted}")
    print(f"  Порожніх:     {skipped}")
    print(f"  Помилок:      {errors}")
    print(f"  Вихідна папка: {args.output}/")
    print(f"\n  Далі використовуйте --labels {args.output}/ у всіх скриптах")


if __name__ == "__main__":
    main()
