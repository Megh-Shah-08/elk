import json
import socket
import time
import argparse
import platform
from datetime import datetime, timezone


def read_cpu():
    with open("/proc/stat", "r") as f:
        values = list(map(int, f.readline().split()[1:]))

    idle = values[3] + values[4]
    total = sum(values)
    return idle, total


def get_cpu_usage(interval):
    idle1, total1 = read_cpu()
    time.sleep(interval)
    idle2, total2 = read_cpu()

    total_diff = total2 - total1
    idle_diff = idle2 - idle1

    if total_diff == 0:
        return 0.0

    return round((1 - idle_diff / total_diff) * 100, 2)


def send_event(stage, cpu_usage):
    event = {
        "stage": stage,
        "cpu_usage": cpu_usage,
        "hostname": platform.node(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    with socket.create_connection(("localhost", 5044)) as sock:
        sock.sendall((json.dumps(event) + "\n").encode())

    print(f"{stage}: CPU Usage = {cpu_usage}%")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", help="Before Load / During Load / After Load")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--interval", type=float, default=1)
    args = parser.parse_args()

    for _ in range(args.count):
        usage = get_cpu_usage(args.interval)
        send_event(args.stage, usage)


if __name__ == "__main__":
    main()
