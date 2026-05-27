#!/usr/bin/env python3
"""
YOLO11 模型训练脚本
支持语义化版本管理、自动评估、MinIO 上传

用法:
  python train_model.py --data data/fruits/fruits.yaml --epochs 100 --device 0
  python train_model.py --evaluate --model-path models/fruits_yolo11n/weights/best.pt
  python train_model.py --predict ./test.jpg --conf 0.3
"""

import os
import sys
import json
import argparse
import shutil
from datetime import datetime
from pathlib import Path

from ultralytics import YOLO
import torch

# 后端根目录
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"


def get_version_dir(model_name, version=None):
    """获取模型版本目录，未指定版本则自动递增"""
    model_dir = MODELS_DIR / model_name
    model_dir.mkdir(parents=True, exist_ok=True)

    if version:
        return model_dir / f"v{version}"

    existing = sorted(model_dir.glob("v*"))
    if existing:
        last = existing[-1].name.lstrip("v")
        parts = last.split(".")
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        new_version = f"v{major}.{minor}.{patch + 1}"
    else:
        new_version = "v1.0.0"

    return model_dir / new_version


def train(args):
    """执行模型训练"""
    print("=" * 60)
    print("YOLO11 模型训练")
    print("=" * 60)

    # 设备检测
    if args.device == "0" or args.device == "cuda":
        if torch.cuda.is_available():
            device = 0
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"GPU: {gpu_name} ({vram:.1f} GB)")
        else:
            print("CUDA 不可用，回退到 CPU")
            device = "cpu"
    else:
        device = args.device

    model_name = args.name
    version_dir = get_version_dir(model_name, args.version)
    version_str = version_dir.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"模型名称: {model_name}")
    print(f"版本: {version_str}")
    print(f"数据配置: {args.data}")
    print(f"训练轮数: {args.epochs}")
    print(f"批次大小: {args.batch}")
    print(f"图片尺寸: {args.imgsz}")
    print(f"设备: {device}")
    print(f"输出目录: {version_dir}")
    print("=" * 60)

    version_dir.mkdir(parents=True, exist_ok=True)

    # 加载模型
    model_path = args.model or str(BASE_DIR / "yolo11n.pt")
    print(f"\n加载预训练模型: {model_path}")
    model = YOLO(model_path)

    # 开始训练
    print(f"\n开始训练...")
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=device,
        workers=args.workers,
        lr0=args.lr0,
        patience=args.patience,
        project=str(version_dir),
        name="train",
        exist_ok=True,
        verbose=True,
    )

    # 移动 best.pt 和 last.pt 到 version_dir
    train_dir = version_dir / "train"
    weights_dir = train_dir / "weights"
    if weights_dir.exists():
        for f in ["best.pt", "last.pt"]:
            src = weights_dir / f
            if src.exists():
                shutil.copy(src, version_dir / f)
                print(f"已保存: {version_dir / f}")

    # 评估
    print("\n评估最佳模型...")
    best_pt = version_dir / "best.pt"
    metrics = evaluate_model(best_pt, args.data, device)

    # 生成元数据
    metadata = {
        "name": model_name,
        "version": version_str.lstrip("v"),
        "created_at": datetime.now().isoformat(),
        "description": f"Fruits-360 数据集训练的 YOLO11 模型",
        "metrics": metrics,
        "config": {
            "epochs": args.epochs,
            "batch": args.batch,
            "imgsz": args.imgsz,
            "device": str(device),
            "lr0": args.lr0,
            "patience": args.patience,
            "data": args.data,
        },
        "dataset": {
            "classes": get_class_names(args.data),
            "nc": get_nc(args.data),
        },
    }

    metadata_path = version_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"元数据已保存: {metadata_path}")

    # 上传到 MinIO（如果可用）
    upload_to_minio(version_dir, model_name, version_str, timestamp, metadata)

    print("\n" + "=" * 60)
    print("训练完成!")
    print(f"版本: {version_str}")
    print(f"最佳模型: {version_dir / 'best.pt'}")
    print(f"mAP@0.5: {metrics.get('mAP50', 'N/A')}")
    print(f"mAP@0.5:0.95: {metrics.get('mAP50-95', 'N/A')}")
    print("=" * 60)

    return version_dir


def evaluate_model(model_path, data_yaml, device):
    """评估模型并返回指标字典"""
    if not Path(model_path).exists():
        print(f"模型文件不存在: {model_path}")
        return {}

    model = YOLO(str(model_path))
    results = model.val(data=data_yaml, device=device, verbose=False)

    metrics = {
        "mAP50": round(float(results.box.map50), 4),
        "mAP50-95": round(float(results.box.map), 4),
        "precision": round(float(results.box.mp), 4) if results.box.mp is not None else 0,
        "recall": round(float(results.box.mr), 4) if results.box.mr is not None else 0,
    }

    print(f"  mAP@0.5:     {metrics['mAP50']}")
    print(f"  mAP@0.5:.95: {metrics['mAP50-95']}")
    print(f"  Precision:   {metrics['precision']}")
    print(f"  Recall:      {metrics['recall']}")

    return metrics


def get_class_names(data_yaml):
    """从 YAML 读取类别名称"""
    try:
        from yaml import safe_load
        with open(data_yaml) as f:
            config = safe_load(f)
        return config.get("names", [])
    except Exception:
        return []


def get_nc(data_yaml):
    """从 YAML 读取类别数量"""
    try:
        from yaml import safe_load
        with open(data_yaml) as f:
            config = safe_load(f)
        return config.get("nc", 0)
    except Exception:
        return 0


def upload_to_minio(version_dir, model_name, version_str, timestamp, metadata):
    """上传模型到 MinIO（如果配置可用）"""
    try:
        sys.path.insert(0, str(BASE_DIR))
        from app.services.minio_service import MinioService
        svc = MinioService()
        for pt_file in ["best.pt", "last.pt"]:
            pt_path = version_dir / pt_file
            if pt_path.exists():
                object_name = f"{model_name}-{pt_file.replace('.pt', '')}_{version_str}_{timestamp}.pt"
                svc.upload_model(str(pt_path), object_name, metadata)
                print(f"  已上传到 MinIO: {object_name}")
    except ImportError:
        print("  (MinIO 服务未配置，跳过上传)")
    except Exception as e:
        print(f"  MinIO 上传失败: {e}")


def predict_image(model_path, image_path, conf=0.3):
    """使用模型预测单张图片"""
    model = YOLO(str(model_path))
    results = model.predict(source=image_path, conf=conf, save=True)
    print(f"预测完成，结果保存在: {results[0].save_dir}")
    return results


def main():
    parser = argparse.ArgumentParser(description="YOLO11 模型训练脚本")

    parser.add_argument("--data", default="data/fruits/fruits.yaml", help="数据集 YAML 配置")
    parser.add_argument("--model", default=None, help="预训练模型路径（默认: yolo11n.pt）")
    parser.add_argument("--name", default="fruits_yolo11n", help="模型名称")
    parser.add_argument("--epochs", type=int, default=100, help="训练轮数")
    parser.add_argument("--batch", type=int, default=16, help="批次大小")
    parser.add_argument("--imgsz", type=int, default=640, help="输入图片尺寸")
    parser.add_argument("--device", default="0", help="训练设备 (0/cuda/cpu)")
    parser.add_argument("--workers", type=int, default=4, help="数据加载线程数")
    parser.add_argument("--lr0", type=float, default=0.01, help="初始学习率")
    parser.add_argument("--patience", type=int, default=20, help="早停耐心值")
    parser.add_argument("--version", default=None, help="模型版本号（自动递增）")

    parser.add_argument("--evaluate", action="store_true", help="仅评估模型")
    parser.add_argument("--model-path", default=None, help="模型路径（用于评估/预测）")
    parser.add_argument("--predict", default=None, help="预测图片路径")
    parser.add_argument("--conf", type=float, default=0.3, help="置信度阈值")

    args = parser.parse_args()

    if args.evaluate:
        path = args.model_path or "models/fruits_yolo11n/v1.0.0/best.pt"
        evaluate_model(path, args.data, args.device)
    elif args.predict:
        path = args.model_path or "models/fruits_yolo11n/v1.0.0/best.pt"
        predict_image(path, args.predict, args.conf)
    else:
        train(args)


if __name__ == "__main__":
    main()
