#!/usr/bin/env python3
"""
Fruits-360 数据集转换工具
将按类别文件夹组织的分类数据集转换为 YOLO 目标检测格式

Fruits-360 原始结构:
  fruits-360/
  ├── Training/
  │   ├── Apple Red 1/
  │   │   ├── image_001.jpg
  │   │   └── ...
  │   ├── Banana/
  │   └── ...
  └── Test/
      ├── Apple Red 1/
      └── ...

转换后 YOLO 格式:
  data/fruits/
  ├── images/
  │   ├── train/
  │   └── val/
  ├── labels/
  │   ├── train/
  │   └── val/
  └── fruits.yaml

每个水果占据整张图片，bounding box 覆盖全图。
"""

import os
import shutil
import random
from pathlib import Path
import cv2


def get_class_names(src_dir):
    """从 Training 目录获取所有类别名称（子文件夹名）"""
    training_dir = Path(src_dir) / "Training"
    if not training_dir.exists():
        raise FileNotFoundError(f"Training 目录不存在: {training_dir}")

    classes = sorted([
        d.name for d in training_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ])
    return classes


def convert_dataset(src_dir, output_dir, val_ratio=0.15, seed=42):
    """
    将 Fruits-360 转换为 YOLO 格式

    参数:
        src_dir: Fruits-360 数据集根目录（包含 Training/ 和 Test/）
        output_dir: YOLO 格式输出目录
        val_ratio: 从 Training 中划分验证集的比例
        seed: 随机种子
    """
    src_dir = Path(src_dir)
    output_dir = Path(output_dir)

    classes = get_class_names(src_dir)
    class_map = {cls: idx for idx, cls in enumerate(classes)}

    print(f"发现 {len(classes)} 个类别: {classes[:8]}..." if len(classes) > 8 else f"发现 {len(classes)} 个类别: {classes}")

    # 创建输出目录
    for split in ["train", "val"]:
        (output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)

    random.seed(seed)

    train_count = 0
    val_count = 0

    for cls_name in classes:
        class_id = class_map[cls_name]
        cls_dir = src_dir / "Training" / cls_name

        images = sorted([
            f for f in cls_dir.iterdir()
            if f.suffix.lower() in {".jpg", ".jpeg", ".png"}
        ])

        random.shuffle(images)
        split_idx = int(len(images) * (1 - val_ratio))
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]

        for img_path in train_imgs:
            process_image(img_path, output_dir, "train", class_id, train_count)
            train_count += 1

        for img_path in val_imgs:
            process_image(img_path, output_dir, "val", class_id, val_count)
            val_count += 1

    print(f"转换完成: 训练集 {train_count} 张, 验证集 {val_count} 张")

    # 创建 YAML 配置
    yaml_path = output_dir / "fruits.yaml"
    yaml_content = f"""# Fruits-360 数据集配置文件
path: {output_dir.absolute().as_posix()}

train: images/train
val: images/val

nc: {len(classes)}
names: {classes}
"""
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    print(f"配置文件: {yaml_path}")
    return output_dir, classes


def process_image(img_path, output_dir, split, class_id, counter):
    """处理单张图片: 复制图片 + 生成 YOLO 标签（全图 bbox）"""
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"警告: 无法读取 {img_path}，已跳过")
        return

    h, w = img.shape[:2]

    # 新文件名: {class_name}_{original_name}
    cls_name = img_path.parent.name
    safe_cls = cls_name.replace(" ", "_").replace("/", "_")
    new_name = f"{safe_cls}_{img_path.stem}{img_path.suffix}"

    # 复制图片
    dst_img = output_dir / "images" / split / new_name
    shutil.copy(img_path, dst_img)

    # YOLO 标签: 整张图作为一个 bbox
    label_name = f"{safe_cls}_{img_path.stem}.txt"
    label_path = output_dir / "labels" / split / label_name
    with open(label_path, "w") as f:
        f.write(f"{class_id} 0.500000 0.500000 1.000000 1.000000")


if __name__ == "__main__":
    import sys

    src = sys.argv[1] if len(sys.argv) > 1 else None
    dst = sys.argv[2] if len(sys.argv) > 2 else "data/fruits"

    if src is None:
        # 尝试自动查找 kagglehub 缓存路径
        cache = Path.home() / ".cache" / "kagglehub" / "datasets" / "moltean" / "fruits"
        versions = sorted(cache.glob("*")) if cache.exists() else []
        if versions:
            src = str(versions[-1])
            print(f"自动检测到数据集: {src}")
        else:
            print("用法: python convert_fruits360.py <数据集路径> [输出路径]")
            print("示例: python convert_fruits360.py ~/.cache/kagglehub/datasets/moltean/fruits/92 data/fruits")
            sys.exit(1)

    output_dir, classes = convert_dataset(src, dst)
    print(f"\n输出目录: {output_dir}")
    print(f"类别数量: {len(classes)}")
    print("下一步: python train_model.py --data data/fruits/fruits.yaml --epochs 100 --device 0")
