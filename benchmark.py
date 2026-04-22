#!/usr/bin/env python3
import argparse
import csv
import json
import subprocess
import time
from pathlib import Path

INSTANCE_PRICES = {
    "c8g.large": 0.068,
    "c6i.large": 0.085,
}

def ffprobe_video(path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=nb_frames,duration,r_frame_rate",
        "-of", "json",
        str(path),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    s = json.loads(p.stdout)["streams"][0]
    a, b = s.get("r_frame_rate", "0/1").split("/")
    fps = float(a) / float(b) if float(b) != 0 else 0
    frames = int(s.get("nb_frames") or float(s.get("duration", 0)) * fps)
    return frames

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", nargs="+", required=True)
    ap.add_argument("--presets", nargs="+", default=["medium"])
    ap.add_argument("--instance-type", required=True, choices=["c8g.large", "c6i.large"])
    ap.add_argument("--repeats", type=int, default=1)
    args = ap.parse_args()

    Path("output").mkdir(exist_ok=True)
    rows = []

    for vid in args.videos:
        frames = ffprobe_video(vid)

        for preset in args.presets:
            for rep in range(1, args.repeats + 1):
                print(f"[{time.strftime('%H:%M:%S')}] Running {vid} | preset={preset} | repeat={rep}", flush=True)

                out_file = f"output/temp_{args.instance_type}_{preset}_{rep}.mp4"
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i", vid,
                    "-c:v", "libx265",
                    "-preset", preset,
                    "-crf", "23",
                    "-an",
                    out_file,
                ]

                start = time.time()
                proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
                elapsed = time.time() - start

                if proc.returncode != 0:
                    print(f"[{time.strftime('%H:%M:%S')}] ERROR: ffmpeg failed for preset={preset}, repeat={rep}", flush=True)
                    print(proc.stderr[-500:], flush=True)
                    rows.append({
                        "instance": args.instance_type,
                        "video": vid,
                        "preset": preset,
                        "repeat": rep,
                        "status": "failed",
                        "time_s": round(elapsed, 2),
                        "fps": 0,
                        "cost_usd": 0,
                    })
                    continue

                app_fps = frames / elapsed if frames else 0
                cost = INSTANCE_PRICES[args.instance_type] * (elapsed / 3600)

                rows.append({
                    "instance": args.instance_type,
                    "video": vid,
                    "preset": preset,
                    "repeat": rep,
                    "status": "success",
                    "time_s": round(elapsed, 2),
                    "fps": round(app_fps, 2),
                    "cost_usd": round(cost, 6),
                })

                print(
                    f"[{time.strftime('%H:%M:%S')}] Done | time={elapsed:.2f}s | fps={app_fps:.2f} | cost=${cost:.6f}",
                    flush=True
                )

    out_csv = f"output/benchmark_results_{args.instance_type}.csv"
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["instance", "video", "preset", "repeat", "status", "time_s", "fps", "cost_usd"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"[{time.strftime('%H:%M:%S')}] Results saved to {out_csv}", flush=True)

if __name__ == "__main__":
    main()