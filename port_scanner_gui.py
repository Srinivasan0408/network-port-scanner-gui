import socket
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from queue import Queue
import time

# Common port services
common_ports = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
    443: "HTTPS", 3306: "MySQL", 3389: "RDP",
    5900: "VNC", 8080: "HTTP-Alt",
    135: "RPC",
    445: "SMB"
}
# Global variables
queue = Queue()
open_ports = []
stop_scan = False

# Function to scan a single port
def scan_port(target, port):
    global open_ports, stop_scan
    if stop_scan:
        return

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex((target, port))

        if result == 0:
            service = common_ports.get(port, "Unknown")
            output = f"Port {port} OPEN ({service})\n"
            open_ports.append(output)
            result_text.insert(tk.END, output)

        s.close()
    except:
        pass

# Worker thread
def worker(target):
    while not queue.empty() and not stop_scan:
        port = queue.get()
        scan_port(target, port)
        queue.task_done()

# Start scan
def start_scan():
    global stop_scan, open_ports
    stop_scan = False
    open_ports = []
    result_text.delete(1.0, tk.END)

    target = target_entry.get()
    start_port = int(start_entry.get())
    end_port = int(end_entry.get())

    for port in range(start_port, end_port + 1):
        queue.put(port)

    thread_count = 100  # You can increase up to 500
    threads = []

    start_time = time.time()

    for _ in range(thread_count):
        t = threading.Thread(target=worker, args=(target,))
        t.start()
        threads.append(t)

    def update_time():
        if any(t.is_alive() for t in threads):
            elapsed = int(time.time() - start_time)
            time_label.config(text=f"Time: {elapsed}s")
            root.after(1000, update_time)

    update_time()

# Stop scan
def stop_scanning():
    global stop_scan
    stop_scan = True

# Save results
def save_results():
    file = filedialog.asksaveasfilename(defaultextension=".txt")
    if file:
        with open(file, "w") as f:
            f.writelines(open_ports)

# GUI Setup
root = tk.Tk()
root.title("Network Port Scanner")

tk.Label(root, text="Target IP / Host:").grid(row=0, column=0)
target_entry = tk.Entry(root)
target_entry.grid(row=0, column=1)

tk.Label(root, text="Start Port:").grid(row=1, column=0)
start_entry = tk.Entry(root)
start_entry.insert(0, "1")
start_entry.grid(row=1, column=1)

tk.Label(root, text="End Port:").grid(row=2, column=0)
end_entry = tk.Entry(root)
end_entry.insert(0, "1024")
end_entry.grid(row=2, column=1)

start_button = tk.Button(root, text="Start Scan", command=start_scan)
start_button.grid(row=3, column=0)

stop_button = tk.Button(root, text="Stop", command=stop_scanning)
stop_button.grid(row=3, column=1)

save_button = tk.Button(root, text="Save Results", command=save_results)
save_button.grid(row=4, column=0, columnspan=2)

time_label = tk.Label(root, text="Time: 0s")
time_label.grid(row=5, column=0, columnspan=2)

result_text = tk.Text(root, height=15, width=50)
result_text.grid(row=6, column=0, columnspan=2)

root.mainloop()