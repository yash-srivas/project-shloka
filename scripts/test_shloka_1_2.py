import urllib.request
import json
import time
import sys

def run_test():
    url = "http://127.0.0.1:8000/api/shlokas/1/analyze?force_refresh=true"
    sys.stdout.buffer.write(f"Sending request to {url}...\n".encode("utf-8"))
    t0 = time.time()
    req = urllib.request.Request(url, method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    elapsed = time.time() - t0
    sys.stdout.buffer.write(f"Analysis completed in {elapsed:.2f}s\n".encode("utf-8"))
    sys.stdout.buffer.write(f"Shloka ID: {data.get('shloka_id')}\n".encode("utf-8"))
    sys.stdout.buffer.write(f"Execution time: {data.get('execution_time_seconds')}s\n".encode("utf-8"))
    sys.stdout.buffer.write(f"Cached: {data.get('cached')}\n\n".encode("utf-8"))

    steps = data.get("steps", {})
    for s in range(1, 8):
        step_data = steps.get(str(s), {})
        sa_name = step_data.get("step_name_sanskrit", "")
        en_name = step_data.get("step_name_english", "")
        out = step_data.get("output", "")
        header = f"==================================================\nSTEP {s}: {sa_name} ({en_name})\n==================================================\n"
        sys.stdout.buffer.write(header.encode("utf-8"))
        sys.stdout.buffer.write(out.encode("utf-8"))
        sys.stdout.buffer.write(b"\n\n")

if __name__ == "__main__":
    run_test()
