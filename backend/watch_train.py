#!/usr/bin/env python3
"""实时监控 YOLO 训练进度"""
import time, re, sys
from pathlib import Path

OUTPUT = Path.home() / "AppData/Local/Temp/claude/c--Users-81577-Desktop-----\7e167261-c139-45e7-a1d1-21ab64a9cf5f/tasks/b03n6p2ud.output"

def get_metrics():
    """从输出文件提取最新指标"""
    if not OUTPUT.exists():
        return None
    text = OUTPUT.read_text(encoding="utf-8", errors="ignore")

    # 提取所有 epoch 验证结果
    pattern = r"all\s+1000\s+\d+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)"
    matches = list(re.finditer(pattern, text))
    if not matches:
        return None

    last = matches[-1]
    p, r, mAP50, mAP5095 = [float(x) for x in last.groups()]

    # 提取当前 epoch 号和进度
    epoch_match = re.findall(r"(\d+)/100\s+\S+G\s+([\d.]+)\s+", text)
    epoch = int(epoch_match[-1][0]) if epoch_match else 0
    loss = float(epoch_match[-1][1]) if epoch_match else 0

    # 提取最后一个 batch 进度
    batch_match = re.findall(r"(\d+)/(\d+)\s+\S+it/s", text)
    batch_progress = int(batch_match[-1][0]) / int(batch_match[-1][1]) if batch_match else 0

    return {
        "epoch": epoch,
        "mAP50": mAP50,
        "mAP50-95": mAP5095,
        "precision": p,
        "recall": r,
        "box_loss": loss,
        "batch_pct": batch_progress,
        "total_metrics": [(i+1, *[float(x) for x in m.groups()]) for i, m in enumerate(matches)],
    }


def bar(value, width=30, full="█", empty="░"):
    filled = int(value / 100 * width)
    return full * filled + empty * (width - filled)


def main():
    print("\033[?25l")  # hide cursor
    print("\n" + "=" * 72)
    print("  YOLO11 训练实时监控 — fruits_yolo11n v1.0.0")
    print("  类别: Raw_Banana | Raw_Mango | Ripe_Banana | Ripe_Mango")
    print("=" * 72)

    last_epoch = 0
    try:
        while True:
            m = get_metrics()
            if m is None:
                time.sleep(2)
                continue

            if m["epoch"] != last_epoch:
                last_epoch = m["epoch"]
                # 显示所有历史记录
                print(f"\n  {'Epoch':<6} {'mAP50':<8} {'mAP50-95':<10} {'P':<8} {'R':<8}")
                print(f"  {'-'*40}")
                for ep, p, r, m50, m95 in m["total_metrics"][-6:]:
                    marker = "←" if ep == m["epoch"] else " "
                    print(f"  {ep:<6} {m50:<8.3f} {m95:<10.3f} {p:<8.3f} {r:<8.3f} {marker}")

            # 当前 epoch 进度条
            print(f"\r  Epoch {m['epoch']}/100 {bar(m['batch_pct']*100, 40)} {m['batch_pct']*100:.0f}%  box_loss={m['box_loss']:.4f}", end="")
            sys.stdout.flush()
            time.sleep(1)

    except KeyboardInterrupt:
        print("\033[?25h")  # show cursor
        print("\n监控已停止（训练仍在后台运行）")


if __name__ == "__main__":
    main()
