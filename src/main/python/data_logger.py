import time
import csv
import psutil

FILENAME = "system_metrics.csv"

# Write header once
with open(FILENAME, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "timestamp",
        "cpu_percent",
        "ram_percent",
        "disk_read_MBps",
        "disk_write_MBps",
        "net_sent_KBps",
        "net_recv_KBps",
        "process_count"
    ])

print("⏳ Logging system data every 1 second...")
print("Press Ctrl+C to stop.\n")

# Track previous IO stats for delta computation
prev_disk = psutil.disk_io_counters()
prev_net = psutil.net_io_counters()
prev_time = time.time()

try:
    while True:
        time.sleep(1)

        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        curr_disk = psutil.disk_io_counters()
        curr_net = psutil.net_io_counters()
        curr_time = time.time()

        dt = curr_time - prev_time
        if dt == 0:
            continue

        # Calculate per-second deltas
        disk_read_MBps = (curr_disk.read_bytes - prev_disk.read_bytes) / (1024 * 1024 * dt)
        disk_write_MBps = (curr_disk.write_bytes - prev_disk.write_bytes) / (1024 * 1024 * dt)
        net_sent_KBps = (curr_net.bytes_sent - prev_net.bytes_sent) / (1024 * dt)
        net_recv_KBps = (curr_net.bytes_recv - prev_net.bytes_recv) / (1024 * dt)
        process_count = len(psutil.pids())

        with open(FILENAME, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                time.strftime("%H:%M:%S"),
                round(cpu, 2),
                round(ram, 2),
                round(disk_read_MBps, 2),
                round(disk_write_MBps, 2),
                round(net_sent_KBps, 2),
                round(net_recv_KBps, 2),
                process_count
            ])

        print(
            f"CPU={cpu:.1f}%  RAM={ram:.1f}%  DiskR={disk_read_MBps:.2f}MB/s  "
            f"DiskW={disk_write_MBps:.2f}MB/s  Net↑={net_sent_KBps:.1f}KB/s  "
            f"Net↓={net_recv_KBps:.1f}KB/s  Proc={process_count}"
        )

        # Update previous stats
        prev_disk, prev_net, prev_time = curr_disk, curr_net, curr_time

except KeyboardInterrupt:
    print(f"\n✅ Logging stopped. Data saved to {FILENAME}")
