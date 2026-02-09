import socket
import threading
import json
import os

peers = {}
lock = threading.Lock()


def handle_peer(conn, addr):
    try:
        data = conn.recv(1024).decode().strip()

        # Ignore empty connections
        if not data:
            conn.close()
            return

        info = json.loads(data)
        peer_id = info["id"]

        with lock:
            peers[peer_id] = (addr[0], info["port"])

        print(f"[+] Peer registered: {peer_id}")

    except json.JSONDecodeError:
        print("[!] Received invalid registration data from peer, ignoring.")

    finally:
        conn.close()


def listen_for_peers():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 5000))
    server.listen()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_peer, args=(conn, addr), daemon=True).start()


def send_task(image_path):
    if not os.path.exists(image_path):
        print("❌ Image not found.")
        return

    with lock:
        if not peers:
            print("❌ No active peers.")
            return

        peer_id, (ip, port) = list(peers.items())[0]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))

        with open(image_path, "rb") as f:
            data = f.read()

        payload = json.dumps({"filename": os.path.basename(image_path), "size": len(data)}).encode()
        s.sendall(payload + b"\n" + data)

        result = s.recv(1024).decode()
        print(f"\n[RESULT from {peer_id}] {result}\n")


def cli():
    print("Commands: list | task <image_path> | exit")

    while True:
        cmd = input("> ").strip()

        if cmd == "list":
            with lock:
                print("\nActive Peers:")
                for p in peers:
                    print(f"  {p}")
                print()

        elif cmd.startswith("task "):
            path = cmd.split(" ", 1)[1]
            send_task(path)

        elif cmd == "exit":
            break


if __name__ == "__main__":
    threading.Thread(target=listen_for_peers, daemon=True).start()
    cli()
