import socket
import threading
import json
import onnxruntime as ort
import numpy as np
from PIL import Image
from io import BytesIO

MODEL_PATH = "mnist.onnx"

session = ort.InferenceSession(MODEL_PATH)
input_name = session.get_inputs()[0].name


def preprocess(image_bytes):
    img = Image.open(BytesIO(image_bytes)).convert("L").resize((28, 28))
    arr = np.array(img).astype(np.float32) / 255.0
    arr = arr.reshape(1, 1, 28, 28)
    return arr


def predict(image_bytes):
    tensor = preprocess(image_bytes)
    outputs = session.run(None, {input_name: tensor})
    digit = int(np.argmax(outputs[0]))
    return str(digit)


def handle_task(conn):
    header, image_data = conn.recv(65536).split(b"\n", 1)
    _ = json.loads(header.decode())

    result = predict(image_data)
    conn.sendall(result.encode())
    conn.close()


def start_peer(peer_id, port):
    # Register
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", 5000))
        s.sendall(json.dumps({"id": peer_id, "port": port}).encode())

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", port))
    server.listen()

    print(f"Peer {peer_id} listening on {port}")

    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle_task, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--port", type=int, required=True)

    args = parser.parse_args()

    start_peer(args.id, args.port)
