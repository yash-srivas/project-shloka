import urllib.request
import json
import time

def run_test():
    url = "http://127.0.0.1:8000/api/shlokas/14/analyze?force_refresh=true"
    print(f"Sending request to {url}...")
    t0 = time.time()
    req = urllib.request.Request(url, method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    elapsed = time.time() - t0
    print(f"Analysis completed in {elapsed:.2f}s")
    print(f"Shloka ID: {data.get('shloka_id')}")
    print(f"Execution time reported: {data.get('execution_time_seconds')}s")
    print(f"Cached: {data.get('cached')}\n")

    steps = data.get("steps", {})
    for s in range(1, 8):
        step_data = steps.get(str(s), {})
        sa_name = step_data.get("step_name_sanskrit", "")
        en_name = step_data.get("step_name_english", "")
        out = step_data.get("output", "")
        header = f"STEP {s}: {sa_name} ({en_name})"
        print(f"==================================================")
        print(header.encode("ascii", "replace").decode("ascii"))
        print(f"==================================================")
        safe_out = out.encode("ascii", "replace").decode("ascii")
        print(safe_out)
        print()

if __name__ == "__main__":
    run_test()
