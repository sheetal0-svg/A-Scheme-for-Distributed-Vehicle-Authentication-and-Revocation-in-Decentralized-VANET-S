import tkinter as tk
from tkinter import messagebox
import datetime
import hashlib
import json
import random

# ----------------- Blockchain Components ---------------- #
class Block:
    def __init__(self, vehicle_id, action, previous_hash):
        self.vehicle_id = vehicle_id
        self.action = action  # e.g., "revoked"
        self.timestamp = datetime.datetime.now().isoformat()
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_data = f"{self.vehicle_id}{self.action}{self.timestamp}{self.previous_hash}"
        return hashlib.sha256(block_data.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [Block("Genesis", "Init", "0")]

    def add_block(self, vehicle_id, action):
        prev_hash = self.chain[-1].hash
        new_block = Block(vehicle_id, action, prev_hash)
        self.chain.append(new_block)
        self.save_chain()

    def save_chain(self):
        data = [{
            "vehicle_id": b.vehicle_id,
            "action": b.action,
            "timestamp": b.timestamp,
            "hash": b.hash
        } for b in self.chain]
        with open("revocation_blockchain.json", "w") as f:
            json.dump(data, f, indent=4)

# ----------------- Main Application ---------------- #
class RevocationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Revocation via Blockchain")

        self.blockchain = Blockchain()
        self.vehicles = [f"V{i+1}" for i in range(5)]
        self.revoked_vehicles = set()

        tk.Label(root, text="Registered Vehicles", font=("Arial", 14, "bold")).pack(pady=10)

        self.vehicle_listbox = tk.Listbox(root, width=30, font=("Arial", 12))
        self.vehicle_listbox.pack(pady=5)
        for v in self.vehicles:
            self.vehicle_listbox.insert(tk.END, v)

        self.revoke_btn = tk.Button(root, text="Revoke Selected Vehicle", font=("Arial", 12),
                                    bg="red", fg="white", command=self.revoke_selected)
        self.revoke_btn.pack(pady=10)

        self.show_revoked_btn = tk.Button(root, text="Show Revoked Vehicles", font=("Arial", 12),
                                          command=self.show_revoked)
        self.show_revoked_btn.pack(pady=5)

        self.show_blockchain_btn = tk.Button(root, text="Show Blockchain Log", font=("Arial", 12),
                                             command=self.show_blockchain)
        self.show_blockchain_btn.pack(pady=5)

        self.output_box = tk.Text(root, height=12, width=60)
        self.output_box.pack(pady=10)

    def revoke_selected(self):
        selected = self.vehicle_listbox.curselection()
        if not selected:
            messagebox.showwarning("Select Vehicle", "Please select a vehicle to revoke.")
            return
        vehicle_id = self.vehicle_listbox.get(selected[0])
        if vehicle_id in self.revoked_vehicles:
            messagebox.showinfo("Already Revoked", f"{vehicle_id} is already revoked.")
            return
        self.revoked_vehicles.add(vehicle_id)
        self.blockchain.add_block(vehicle_id, "revoked")
        messagebox.showinfo("Revoked", f"{vehicle_id} has been revoked and recorded to blockchain.")
        self.output_box.insert(tk.END, f"{vehicle_id} revoked at {datetime.datetime.now().strftime('%H:%M:%S')}\n")
        self.output_box.see(tk.END)

    def show_revoked(self):
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "Revoked Vehicles:\n")
        for v in sorted(self.revoked_vehicles):
            self.output_box.insert(tk.END, f"• {v}\n")

    def show_blockchain(self):
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "Blockchain Revocation Log:\n\n")
        for block in self.blockchain.chain[1:]:  # Skip genesis block
            self.output_box.insert(tk.END,
                f"[{block.timestamp}] {block.vehicle_id} => {block.action}\n")

# ----------------- Launch GUI ---------------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = RevocationApp(root)
    root.mainloop()
