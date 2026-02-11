# Decentralized AI Inference Network

A production-style prototype of a **decentralized peer‑to‑peer AI inference system** inspired by Gradient, Bittensor, and Gensyn.

This project demonstrates real-world engineering across:

* Distributed systems & consensus
* Edge AI inference with ONNX
* Reputation & incentive simulation
* Observability + metrics pipeline
* Dockerized multi‑node deployment
* Real‑time dashboard visualization

---

# 🚀 Demo Overview

**Flow:**

Coordinator → distributes image task → multiple peers run ONNX inference → majority consensus → reputation updates → metrics exposed via HTTP → dashboard visualizes results.

---

# 🧠 Architecture

## Components

### 1. Coordinator

* Registers peers via TCP
* Sends inference tasks to all active peers
* Aggregates predictions
* Computes **majority‑vote consensus**
* Updates **peer reputation scores**
* Persists metrics to `metrics.json`

### 2. Peer Nodes

* Receive image bytes over socket
* Preprocess to MNIST tensor
* Run **ONNX Runtime inference**
* Return predicted digit

### 3. Metrics Server

* Lightweight HTTP server
* Serves system state at:

```
http://localhost:8000/metrics
```

### 4. React Dashboard (optional extension)

* Displays:

  * Tasks completed
  * Consensus history
  * Peer reputation
  * Active peers

---

# ⚙️ Tech Stack

* **Python** — networking, orchestration, consensus
* **ONNX Runtime** — edge inference execution
* **NumPy / Pillow** — preprocessing
* **Multithreading + TCP sockets** — distributed coordination
* **JSON persistence** — metrics & observability
* **Docker Compose** — multi‑node deployment
* **React** — visualization dashboard

---

# 📦 Project Structure

```
mini-gradient/
│
├── coordinator.py
├── peer.py
├── metrics_server.py
├── create_mnist_onnx.py
├── mnist.onnx
├── digit5.png
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── dashboard/ (React UI)
```

---

# 🏃 Local Setup

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Start coordinator

```bash
python coordinator.py
```

## 3. Start metrics server

```bash
python metrics_server.py
```

## 4. Launch peers

```bash
python peer.py --id peer1 --port 6001
python peer.py --id peer2 --port 6002
python peer.py --id peer3 --port 6003
```

## 5. Run inference task

Inside coordinator CLI:

```
task digit5.png
```

## 6. View metrics

Open:

```
http://localhost:8000/metrics
```

---

# 🐳 Docker Deployment

Run full distributed stack:

```bash
docker compose up --build
```

---

# 📊 Example Metrics Output

```json
{
  "tasks_completed": 3,
  "consensus_history": [5, 3, 7],
  "reputation": {
    "peer1": 2,
    "peer2": 3,
    "peer3": 1
  },
  "active_peers": ["peer1", "peer2", "peer3"]
}
```

---

# 🔐 Future Improvements

Planned production‑grade upgrades:

* Byzantine fault tolerance
* Stake‑weighted consensus
* Cryptographic proof of inference
* Gossip‑based peer discovery
* Async networking (asyncio / Rust)
* GPU worker marketplace
* Token incentives & slashing

---

# 🎯 Why This Project Matters

Centralized AI compute is becoming a bottleneck for open innovation.

Decentralized inference networks enable:

* Permissionless compute markets
* Trust‑minimized AI execution
* Global edge participation

This repository is a **minimal working prototype** of that future.

---

# ⭐ If you find this useful

Give the repo a star and feel free to contribute!
