import socket
import threading
import json
import os
from collections import Counter, defaultdict

PEER_PORT = 5000

peers = {}  # peer_id -> (ip, port)
reputation = defaultdict(int)
consensus_history = []
tasks_completed = 0
lock = threading.Lock()


# ---------------- METRICS ----------------


METRICS_FILE = "metrics.json"


def save_metrics(consensus_digit=None):
    print(f"DEBUG: save_metrics called with consensus_digit={consensus_digit}")
    
    try:
        data = {
            "tasks_completed": 0,
            "reputation": dict(reputation),
            "active_peers": list(peers.keys()),
            "consensus_history": []
        }

        # If file already exists → append history & increment counter
        if os.path.exists(METRICS_FILE):
            print("DEBUG: File exists, reading...")
            try:
                with open(METRICS_FILE, "r") as f:
                    old = json.load(f)

                data["tasks_completed"] = old.get("tasks_completed", 0)
                data["consensus_history"] = old.get("consensus_history", [])
                    
            except Exception as e:
                print("⚠ metrics read error:", e)

        # Only update if we have a consensus digit
        if consensus_digit is not None:
            data["tasks_completed"] += 1
            data["consensus_history"].append(int(consensus_digit))

        # Always update reputation with current values
        data["reputation"] = dict(reputation)

        # WRITE FILE (this is the key part)
        print(f"DEBUG: Writing to {METRICS_FILE}")
        print(f"DEBUG: Current directory: {os.getcwd()}")
        print(f"DEBUG: Absolute path: {os.path.abspath(METRICS_FILE)}")
        
        with open(METRICS_FILE, "w") as f:
            json.dump(data, f, indent=2)

        print("✅ metrics.json updated")
        
        # Verify file was created
        if os.path.exists(METRICS_FILE):
            file_size = os.path.getsize(METRICS_FILE)
            print(f"✅ File verified - Size: {file_size} bytes")
        else:
            print("❌ WARNING: File not found after write!")
        
    except Exception as e:
        print(f"❌ ERROR in save_metrics: {e}")
        import traceback
        traceback.print_exc()


# ---------------- PEER HANDLING ----------------
def handle_peer(conn, addr):
    try:
        data = conn.recv(1024).decode().strip()
        if not data:
            return

        info = json.loads(data)
        peer_id = info["id"]

        with lock:
            peers[peer_id] = (addr[0], info["port"])
            save_metrics()

        print(f"[+] Peer registered: {peer_id}")

    except Exception:
        print("[!] Invalid peer ignored")

    finally:
        conn.close()


def listen_for_peers():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", PEER_PORT))
    server.listen()

    print(f"Coordinator listening on port {PEER_PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_peer, args=(conn, addr), daemon=True).start()


# ---------------- QUERY PEERS ----------------
def query_peer(peer_id, ip, port, image_bytes, results):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((ip, port))

            payload = json.dumps({"size": len(image_bytes)}).encode()
            s.sendall(payload + b"\n" + image_bytes)

            result = s.recv(1024).decode().strip()
            results[peer_id] = result

    except Exception:
        print(f"[-] Peer {peer_id} unreachable → removing")

        with lock:
            peers.pop(peer_id, None)
            save_metrics()

        results[peer_id] = None


# ---------------- CONSENSUS ----------------
def consensus_task(image_path):
    global tasks_completed, consensus_history

    if not os.path.exists(image_path):
        print("❌ Image not found")
        return

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    with lock:
        active_peers = dict(peers)

    if not active_peers:
        print("❌ No peers available")
        return

    threads = []
    results = {}

    for peer_id, (ip, port) in active_peers.items():
        t = threading.Thread(target=query_peer, args=(peer_id, ip, port, image_bytes, results))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("\nPeer Results:")
    for p, r in results.items():
        print(f"  {p}: {r}")

    valid_results = [r for r in results.values() if r is not None]
    if not valid_results:
        print("❌ No valid predictions")
        return

    majority = Counter(valid_results).most_common(1)[0][0]
    print(f"\n✅ Consensus Digit: {majority}\n")
    
    # reputation update and save metrics (all within lock for thread safety)
    with lock:
        for peer_id, r in results.items():
            if r == majority:
                reputation[peer_id] += 1
            elif r is not None:
                reputation[peer_id] -= 1
        
        # Save metrics immediately after updating reputation
        save_metrics(majority)

    print("Reputation Scores:")
    for p, score in reputation.items():
        print(f"  {p}: {score}")
    print()


# ---------------- CLI ----------------
def cli():
    print("Commands: list | task <image> | rep | exit")

    while True:
        cmd = input("> ").strip()

        if cmd == "list":
            with lock:
                print("\nActive Peers:")
                for p in peers:
                    print(f"  {p}")
                if not peers:
                    print("  (none)")
                print()

        elif cmd.startswith("task "):
            consensus_task(cmd.split(" ", 1)[1])

        elif cmd == "rep":
            print("\nReputation Scores:")
            for p, s in reputation.items():
                print(f"  {p}: {s}")
            print()

        elif cmd == "exit":
            break


if __name__ == "__main__":
    print("=" * 50)
    print("INITIALIZING COORDINATOR")
    print("=" * 50)
    
    save_metrics()  # initialize file
    
    # Double-check the file exists
    print("\n" + "=" * 50)
    if os.path.exists(METRICS_FILE):
        print(f"✅ CONFIRMED: metrics.json exists at:")
        print(f"   {os.path.abspath(METRICS_FILE)}")
        with open(METRICS_FILE, "r") as f:
            content = f.read()
            print(f"   Content preview: {content[:100]}")
    else:
        print(f"❌ WARNING: metrics.json NOT FOUND at:")
        print(f"   {os.path.abspath(METRICS_FILE)}")
    print("=" * 50 + "\n")
    
    threading.Thread(target=listen_for_peers, daemon=True).start()
    cli()