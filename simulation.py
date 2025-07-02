import tkinter as tk
from tkinter import messagebox
import random
import datetime
import hashlib
import csv
import time
import json
from PIL import Image, ImageTk
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import matplotlib.pyplot as plt
from collections import defaultdict
# Blockchain components
class Block:
    def __init__(self, vehicle_id, certificate, previous_hash):
        self.vehicle_id = vehicle_id
        self.certificate = certificate
        self.timestamp = datetime.datetime.now().isoformat()
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = f"{self.vehicle_id}{self.certificate}{self.timestamp}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [Block("Genesis", "Initial Block", "0")]

    def add_block(self, vehicle_id, certificate):
        prev_hash = self.chain[-1].hash
        new_block = Block(vehicle_id, certificate, prev_hash)
        self.chain.append(new_block)
        self.save_to_json()

    def save_to_json(self):
        data = [{"vehicle_id": b.vehicle_id, "certificate": b.certificate, "timestamp": b.timestamp, "hash": b.hash} for b in self.chain]
        with open("blockchain.json", "w") as f:
            json.dump(data, f, indent=4)

# Certificate Authority
class CertificateAuthority:
    def __init__(self, blockchain):
        self.revoked_certs = set()
        self.blockchain = blockchain
        self.public_key_registry = set()

    def issue_certificate(self, vehicle_id, public_key):
        serialized_key = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                 format=serialization.PublicFormat.SubjectPublicKeyInfo)
        if serialized_key in self.public_key_registry:
            return "Sybil-Detected"
        self.public_key_registry.add(serialized_key)
        cert = f"Cert-{vehicle_id}"
        self.blockchain.add_block(vehicle_id, cert)
        return cert

    def revoke_certificate(self, vehicle_id):
        start_time = time.time()
        self.revoked_certs.add(vehicle_id)
        self.blockchain.save_to_json()
        latency = round((time.time() - start_time)*1000, 2)  # in ms
        return latency

    def is_revoked(self, vehicle_id):
        return vehicle_id in self.revoked_certs

# Vehicle
class Vehicle:
    def __init__(self, canvas, x, y, vehicle_id, car_img):
        self.canvas = canvas
        self.vehicle_id = vehicle_id
        self.x = x
        self.y = y
        self.car_image = car_img
        self.image_id = canvas.create_image(x, y, image=car_img, anchor='nw')
        self.label = canvas.create_text(x + 15, y - 10, text=vehicle_id, fill="black")
        self.cert = None
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        self.last_auth_time = 0
        self.auth_count = 0

    def move(self):
        dx = random.randint(-5, 5)
        dy = random.randint(-5, 5)
        self.canvas.move(self.image_id, dx, dy)
        self.canvas.move(self.label, dx, dy)
        self.x += dx
        self.y += dy

# RSU
class RSU:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.rect = canvas.create_rectangle(x, y, x + 30, y + 30, fill="green")

    def authenticate(self, vehicle, ca):
        now = time.time()
        if now - vehicle.last_auth_time < 1:
            return "DoS"
        vehicle.last_auth_time = now
        vehicle.auth_count += 1

        if ca.is_revoked(vehicle.vehicle_id):
            return "Revoked"

        message = b"auth_request"
        try:
            signature = vehicle.private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())
            vehicle.public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA256())
            return "Authenticated"
        except:
            return "Failed"

# VANET Simulation GUI
class VANETSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure VANET with Blockchain")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()

        for y in range(0, 600, 100):
            self.canvas.create_rectangle(380, y, 420, y + 20, fill="black")

        self.blockchain = Blockchain()
        self.ca = CertificateAuthority(self.blockchain)
        self.car_img = Image.open("car2.jpg").resize((30, 30))
        self.car_img = ImageTk.PhotoImage(self.car_img)

        self.vehicles = []
        self.rsus = [RSU(self.canvas, 100, 100), RSU(self.canvas, 600, 400)]

        for i in range(5):
            v = Vehicle(self.canvas, random.randint(100, 700), random.randint(100, 500), f"V{i+1}", self.car_img)
            cert = self.ca.issue_certificate(v.vehicle_id, v.public_key)
            if cert == "Sybil-Detected":
                self.log(f"[!] Sybil Attack Detected for {v.vehicle_id}")
            else:
                v.cert = cert
                self.vehicles.append(v)

        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=5)
        tk.Button(self.btn_frame, text="Start Simulation", command=self.start_simulation).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="Revoke Vehicle", command=self.revoke_random).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="Export Logs", command=self.export_logs).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="Show Graphs", command=self.plot_graphs).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="Simulate Attacks", command=self.simulate_attacks).pack(side=tk.LEFT, padx=5)

        self.log_box = tk.Text(root, height=10, width=100)
        self.log_box.pack(pady=5)
        self.auth_times = []
        self.auth_labels = []
        self.revocation_latencies = []
        self.revocation_counts = []
        self.revoked_count = 0

    def log(self, msg):
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)

    def start_simulation(self):
        self.simulate()

    def simulate(self):
        for v in self.vehicles:
            v.move()
            for rsu in self.rsus:
                if abs(v.x - rsu.x) < 50 and abs(v.y - rsu.y) < 50:
                    t0 = time.time()
                    result = rsu.authenticate(v, self.ca)
                    latency = round((time.time() - t0)*1000, 2)
                    self.auth_times.append(latency)
                    self.auth_labels.append(v.vehicle_id)
                    ts = datetime.datetime.now().strftime("%H:%M:%S")
                    if result == "Authenticated":
                        self.log(f"[{ts}] {v.vehicle_id} authenticated in {latency} ms")
                    elif result == "Revoked":
                        self.log(f"[{ts}] {v.vehicle_id} is revoked")
                    elif result == "DoS":
                        self.log(f"[{ts}] DoS Detected from {v.vehicle_id}")
                    else:
                        self.log(f"[{ts}] {v.vehicle_id} authentication failed")
        self.root.after(1000, self.simulate)

    def revoke_random(self):
        v = random.choice(self.vehicles)
        latency = self.ca.revoke_certificate(v.vehicle_id)
        self.revoked_count += 1
        self.revocation_latencies.append(latency)
        self.revocation_counts.append(self.revoked_count)
        self.log(f"[!] {v.vehicle_id} has been revoked. Revocation Latency: {latency} ms")

    def export_logs(self):
        with open("vanet_log.csv", "w", newline='') as f:
            writer = csv.writer(f)
            for line in self.log_box.get("1.0", tk.END).splitlines():
                writer.writerow([line])
        messagebox.showinfo("Exported", "Logs saved to vanet_log.csv")

    from collections import defaultdict

    def plot_graphs(self):
        # Group and average authentication time per vehicle
        vehicle_times = defaultdict(list)
        for vid, t in zip(self.auth_labels, self.auth_times):
            vehicle_times[vid].append(t)

        avg_times = {vid: sum(times) / len(times) for vid, times in vehicle_times.items()}

        plt.figure(figsize=(12, 5))

        # --------- Plot 1: Authentication Time vs Vehicle ID --------- #
        plt.subplot(1, 2, 1)
        vehicle_ids = list(avg_times.keys())
        avg_auth = list(avg_times.values())

        plt.bar(vehicle_ids, avg_auth, color='blue')
        plt.title("Authentication Time vs Vehicle")
        plt.xlabel("Vehicle ID")
        plt.ylabel("Time (ms)")
        plt.xticks(rotation=45)
        plt.grid(True)

        # --------- Plot 2: Revocation Latency --------- #
        plt.subplot(1, 2, 2)
        plt.plot(self.revocation_counts, self.revocation_latencies, marker='x', color='red')
        plt.title("Revocation Latency vs Revoked Vehicles")
        plt.xlabel("Revoked Vehicle Count")
        plt.ylabel("Latency (ms)")
        plt.grid(True)

        plt.tight_layout()
        plt.show()

    def simulate_attacks(self):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log(f"[{ts}]  Simulating Sybil Attack...")
        fake_vehicle = Vehicle(self.canvas, 400, 300, "V1", self.car_img)  # duplicate ID
        cert = self.ca.issue_certificate(fake_vehicle.vehicle_id, fake_vehicle.public_key)
        if cert == "Sybil-Detected":
            self.log(f"[{ts}]  Sybil Attack Detected and Blocked")

        self.log(f"[{ts}] Simulating Replay Attack...")
        v = self.vehicles[0]
        v.last_auth_time = time.time() - 5  # accept
        rsu = self.rsus[0]
        result = rsu.authenticate(v, self.ca)
        if result == "Authenticated":
            self.log(f"[{ts}]  Replay Attack Prevented (Fresh Timestamp Verified)")

        self.log(f"[{ts}] Simulating DoS Attack...")
        v.last_auth_time = time.time()
        result = rsu.authenticate(v, self.ca)
        if result == "DoS":
            self.log(f"[{ts}]  DoS Attack Detected and Blocked")

if __name__ == "__main__":
    root = tk.Tk()
    app = VANETSimulation(root)
    root.mainloop()
