# CS5296 Cloud Computing Theory & Practice - Project
## Benchmarking Video Transcoding Performance: AWS Graviton (ARM64) vs Intel x86

This repository contains the source code, benchmarking scripts, and experimental results for evaluating the cost-performance of video transcoding workloads on AWS cloud infrastructure. The project compares AWS Graviton3 (`c8g.large`, ARM64) against Intel 3rd Gen Xeon (`c6i.large`, x86) using the FFmpeg `libx265` encoder.

## 📂 Folder Structure

```text
CS5296_Cloud-ComputingTheo-Practice-Project/
│
├── benchmark.py                  # The main Python script to run the FFmpeg benchmark
├── README.md                     # Project documentation (this file)
│
├── videos/                       # Directory containing input video files (Add your videos here)
│   ├── test_1080p_60s.mp4        # Sample 1080p video for testing
│   └── test_4k.mp4               # Sample 4K video for testing
│
└── output/                       # Auto-generated directory for benchmark outputs
    ├── benchmark_results_c6i.large_1080p-3.csv   # Results for 1080p on x86
    ├── benchmark_results_c6i.large_4k-2.csv      # Results for 4K on x86
    ├── benchmark_results_c8g.large_1080p-5.csv   # Results for 1080p on ARM64
    ├── benchmark_results_c8g.large_4k-4.csv      # Results for 4K on ARM64
    └── temp/                     # Temporary encoded videos (auto-deleted or overwritten)
```

## ⚙️ Prerequisites and Dependencies

To run the benchmark script on an AWS EC2 instance (Ubuntu 24.04 recommended), you must install the following dependencies:

```bash
# Update package list
sudo apt update

# Install FFmpeg (must support libx265) and Python3
sudo apt install -y ffmpeg python3 python3-pip
```

You can verify the installation by running:
```bash
ffmpeg -version
python3 --version
```

## 🚀 How to Run the Benchmark Script

The `benchmark.py` script automates the FFmpeg transcoding process, parses `ffprobe` to calculate video frames, executes the encoding, and calculates the exact execution time, FPS, and estimated AWS instance cost.

### Command-Line Arguments:
* `--videos`: Path to one or more input video files (Required).
* `--presets`: FFmpeg CPU presets to test (e.g., `medium`, `slow`). Default is `medium`.
* `--instance-type`: The type of EC2 instance running the test (Choices: `c8g.large`, `c6i.large`) (Required).
* `--repeats`: Number of times to repeat the exact same test to calculate average performance (Default: 1).

### Examples:

**1. Running a 1080p Benchmark on an ARM64 Instance (`c8g.large`)**
```bash
python3 benchmark.py \
  --videos videos/test_1080p_60s.mp4 \
  --presets medium slow \
  --instance-type c8g.large \
  --repeats 2
```

**2. Running a 4K Benchmark on an x86 Instance (`c6i.large`) in the Background**
Since 4K video transcoding takes a significant amount of time, it is highly recommended to run the script using `nohup` to prevent the process from stopping if your SSH session disconnects:
```bash
nohup python3 benchmark.py \
  --videos videos/test_4k.mp4 \
  --presets medium slow \
  --instance-type c6i.large \
  --repeats 2 </dev/null > run_x86_4k.log 2>&1 &
```

## 📊 Expected Output

Upon successful completion, the script will create a CSV file inside the `output/` directory containing the raw data of the runs.

Example CSV format (`output/benchmark_results_c8g.large.csv`):
```csv
instance,video,preset,repeat,status,time_s,fps,cost_usd
c8g.large,videos/test_1080p_60s.mp4,medium,1,success,339.18,5.31,0.006407
c8g.large,videos/test_1080p_60s.mp4,medium,2,success,338.84,5.31,0.006400
```
*Note: The cost is estimated based on standard AWS hourly on-demand rates ($0.068 for c8g.large and $0.085 for c6i.large).*
