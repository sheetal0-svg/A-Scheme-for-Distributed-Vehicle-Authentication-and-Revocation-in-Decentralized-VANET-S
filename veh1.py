import tkinter as tk
from tkinter import messagebox
import sqlite3
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

# Database setup function
def create_db():
    conn = sqlite3.connect('vanet.db')
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles (
                        vehicle_id TEXT PRIMARY KEY,
                        public_key TEXT,
                        revoked BOOLEAN)''')
    conn.commit()
    conn.close()

# Vehicle class to hold vehicle information and generate keys
class Vehicle:
    def __init__(self, vehicle_id):
        self.vehicle_id = vehicle_id
        # Generate RSA public/private key pair for authentication
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()
        self.revoked = False

    def sign_message(self, message):
        """
        Sign a message using the vehicle's private key
        """
        signature = self.private_key.sign(
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return signature

    def verify_signature(self, message, signature, public_key):
        """
        Verify a message signature using the provided public key
        """
        try:
            public_key.verify(
                signature,
                message.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except:
            return False

    def revoke(self):
        """
        Mark the vehicle as revoked
        """
        self.revoked = True
        print(f"Vehicle {self.vehicle_id} has been revoked!")

# VANET system class to handle vehicle registration, messages, and revocation
class VANET:
    def __init__(self):
        self.vehicles = {}
        self.revocation_list = []
        self.load_vehicles_from_db()

    def load_vehicles_from_db(self):
        """
        Load vehicles from the database and initialize vehicle objects
        """
        conn = sqlite3.connect('vanet.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM vehicles")
        rows = cursor.fetchall()

        for row in rows:
            vehicle_id, public_key, revoked = row
            vehicle = Vehicle(vehicle_id)
            vehicle.public_key = serialization.load_pem_public_key(public_key.encode())
            vehicle.revoked = bool(revoked)
            self.vehicles[vehicle_id] = vehicle

        conn.close()

    def register_vehicle(self, vehicle):
        """
        Register a new vehicle to the VANET network and store it in the database
        """
        conn = sqlite3.connect('vanet.db')
        cursor = conn.cursor()

        cursor.execute("INSERT OR REPLACE INTO vehicles (vehicle_id, public_key, revoked) VALUES (?, ?, ?)",
                       (vehicle.vehicle_id, vehicle.public_key.public_bytes(
                           encoding=serialization.Encoding.PEM,
                           format=serialization.PublicFormat.SubjectPublicKeyInfo).decode(), vehicle.revoked))

        conn.commit()
        conn.close()

        self.vehicles[vehicle.vehicle_id] = vehicle
        print(f"Vehicle {vehicle.vehicle_id} registered.")

    def create_message(self, vehicle, message):
        """
        Create and sign a message with vehicle's signature
        """
        if vehicle.revoked:
            print(f"Vehicle {vehicle.vehicle_id} is revoked and cannot send messages.")
            return None  # Vehicle is revoked, return None

        signature = vehicle.sign_message(message)
        return message, signature  # Return message and signature as a tuple

    def verify_message(self, vehicle, message, signature):
        """
        Verify if the message signature is valid for the given vehicle.
        """
        if vehicle.revoked:
            print(f"Vehicle {vehicle.vehicle_id} is revoked and cannot send messages.")
            return False

        return vehicle.verify_signature(message, signature, vehicle.public_key)

    def revoke_vehicle(self, vehicle):
        """
        Add vehicle to the revocation list and update database
        """
        if vehicle.vehicle_id not in self.revocation_list:
            self.revocation_list.append(vehicle.vehicle_id)
            vehicle.revoke()

            # Update revocation status in the database
            conn = sqlite3.connect('vanet.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE vehicles SET revoked = ? WHERE vehicle_id = ?",
                           (True, vehicle.vehicle_id))
            conn.commit()
            conn.close()

# GUI Application Class
class VehicleRegistrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle Authentication and Revocation System")
        self.root.geometry("600x500")  # Set the window size
        self.root.configure(bg="#2C3E50")  # Set background color

        self.vanet = VANET()

        # Vehicle Registration Form Labels and Entry fields
        self.vehicle_id_label = tk.Label(root, text="Enter Vehicle ID:", font=("Helvetica", 16, "bold"), fg="#ECF0F1", bg="#2C3E50")
        self.vehicle_id_label.pack(pady=20)

        self.vehicle_id_entry = tk.Entry(root, width=30, font=("Helvetica", 14), bd=2, relief="solid", justify="center")
        self.vehicle_id_entry.pack(pady=10)

        # Register Button
        self.register_button = tk.Button(root, text="Register Vehicle", font=("Helvetica", 14, "bold"), bg="#2980B9", fg="white",
                                         relief="raised", command=self.register_vehicle)
        self.register_button.pack(pady=10)

        # Sign Message Section
        self.message_label = tk.Label(root, text="Enter Message to Sign:", font=("Helvetica", 14), fg="#ECF0F1", bg="#2C3E50")
        self.message_label.pack(pady=10)

        self.message_entry = tk.Entry(root, width=30, font=("Helvetica", 14), bd=2, relief="solid", justify="center")
        self.message_entry.pack(pady=10)

        self.sign_button = tk.Button(root, text="Sign Message", font=("Helvetica", 14, "bold"), bg="#16A085", fg="white",
                                     relief="raised", command=self.sign_message)
        self.sign_button.pack(pady=10)

        # Revoke Button
        self.revoke_button = tk.Button(root, text="Revoke Vehicle", font=("Helvetica", 14, "bold"), bg="#E74C3C", fg="white",
                                       relief="raised", command=self.revoke_vehicle)
        self.revoke_button.pack(pady=10)

        # Status Display
        self.status_label = tk.Label(root, text="", font=("Helvetica", 12), fg="#ECF0F1", bg="#2C3E50")
        self.status_label.pack(pady=20)

    def register_vehicle(self):
        # Retrieve the entered vehicle ID from the entry widget
        vehicle_id = self.vehicle_id_entry.get()

        # Validate if vehicle ID is provided
        if not vehicle_id:
            messagebox.showerror("Error", "Please enter a vehicle ID.")
            return

        # Create a new Vehicle object
        vehicle = Vehicle(vehicle_id)

        # Register the vehicle in VANET
        self.vanet.register_vehicle(vehicle)
        messagebox.showinfo("Success", f"Vehicle {vehicle_id} registered successfully!")

        # Clear the entry field
        self.vehicle_id_entry.delete(0, tk.END)

    def sign_message(self):
        # Retrieve the entered message from the entry widget
        message = self.message_entry.get()
        vehicle_id = self.vehicle_id_entry.get()

        # Validate if message and vehicle ID are provided
        if not message or not vehicle_id:
            messagebox.showerror("Error", "Please enter both vehicle ID and message.")
            return

        # Get the vehicle object from the VANET
        vehicle = self.vanet.vehicles.get(vehicle_id)

        if not vehicle:
            messagebox.showerror("Error", f"Vehicle {vehicle_id} is not registered.")
            return

        # Create and sign the message
        result = self.vanet.create_message(vehicle, message)

        # Check if the result is valid
        if result:
            msg, signature = result
            self.status_label.config(text=f"Message signed: {msg}\nSignature: {signature.hex()}")
        else:
            self.status_label.config(text="Message signing failed due to vehicle revocation.")

    def revoke_vehicle(self):
        # Retrieve the entered vehicle ID from the entry widget
        vehicle_id = self.vehicle_id_entry.get()

        # Validate if vehicle ID is provided
        if not vehicle_id:
            messagebox.showerror("Error", "Please enter a vehicle ID.")
            return

        # Get the vehicle object from the VANET
        vehicle = self.vanet.vehicles.get(vehicle_id)

        if not vehicle:
            messagebox.showerror("Error", f"Vehicle {vehicle_id} is not registered.")
            return

        # Revoke the vehicle
        self.vanet.revoke_vehicle(vehicle)
        messagebox.showinfo("Revocation", f"Vehicle {vehicle_id} has been revoked!")

        # Clear the entry field
        self.vehicle_id_entry.delete(0, tk.END)

# Create the main window for the GUI
root = tk.Tk()

# Initialize the database
create_db()

# Create an instance of the VehicleRegistrationApp
app = VehicleRegistrationApp(root)

# Run the Tkinter event loop
root.mainloop()
