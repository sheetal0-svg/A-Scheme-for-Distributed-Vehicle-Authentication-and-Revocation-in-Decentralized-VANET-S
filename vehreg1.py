import tkinter as tk
from tkinter import messagebox
import rsa
import sqlite3

# Vehicle class to hold vehicle information and generate keys
class Vehicle:
    def __init__(self, vehicle_id):
        self.vehicle_id = vehicle_id
        self.private_key, self.public_key = rsa.newkeys(2048)  # Generate RSA keys for encryption

    def get_public_key(self):
        """
        Return the vehicle's public key in a serializable format.
        """
        return self.public_key.save_pkcs1().decode('utf-8')

# Database handler class
class Database:
    def __init__(self):
        self.connection = sqlite3.connect('vehicle_registration.db')  # Connect to the SQLite database
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        """
        Create the vehicles table if it doesn't exist.
        """
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles (
                                vehicle_id TEXT PRIMARY KEY,
                                public_key TEXT
                                )''')
        self.connection.commit()

    def register_vehicle(self, vehicle):
        """
        Add a vehicle to the database.
        """
        try:
            self.cursor.execute("INSERT INTO vehicles (vehicle_id, public_key) VALUES (?, ?)",
                                (vehicle.vehicle_id, vehicle.get_public_key()))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Vehicle ID already exists

    def get_vehicle_public_key(self, vehicle_id):
        """
        Retrieve the public key of a vehicle by its ID.
        """
        self.cursor.execute("SELECT public_key FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None

# GUI Application Class
class VehicleRegistrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle Registration in VANET")
        self.root.geometry("600x500")  # Set the window size
        self.root.configure(bg="#2C3E50")  # Set background color

        self.db = Database()  # Initialize the database handler

        # Vehicle Registration Form Labels and Entry fields
        self.vehicle_id_label = tk.Label(root, text="Enter Vehicle ID:", font=("Helvetica", 16, "bold"), fg="#ECF0F1", bg="#2C3E50")
        self.vehicle_id_label.pack(pady=20)

        self.vehicle_id_entry = tk.Entry(root, width=30, font=("Helvetica", 14), bd=2, relief="solid", justify="center")
        self.vehicle_id_entry.pack(pady=10)

        # Register Button
        self.register_button = tk.Button(root, text="Register Vehicle", font=("Helvetica", 14, "bold"), bg="#2980B9", fg="white",
                                         relief="raised", command=self.register_vehicle)
        self.register_button.pack(pady=30)

        # Status Label
        self.status_label = tk.Label(root, text="", font=("Helvetica", 12), fg="#ECF0F1", bg="#2C3E50")
        self.status_label.pack(pady=10)

        # Display Public Key
        self.public_key_label = tk.Label(root, text="Public Key: Not Available", font=("Helvetica", 12), fg="#ECF0F1", bg="#2C3E50")
        self.public_key_label.pack(pady=10)

    def register_vehicle(self):
        # Retrieve the entered vehicle ID from the entry widget
        vehicle_id = self.vehicle_id_entry.get()

        # Validate if vehicle ID is provided
        if not vehicle_id:
            messagebox.showerror("Error", "Please enter a vehicle ID.")
            return

        # Create a new Vehicle object
        vehicle = Vehicle(vehicle_id)

        # Try to register the vehicle in the database
        if self.db.register_vehicle(vehicle):
            # Update GUI with success message and public key
            self.status_label.config(text=f"Vehicle {vehicle_id} registered successfully!")
            self.public_key_label.config(text=f"Public Key: {vehicle.get_public_key()}")
            self.vehicle_id_entry.delete(0, tk.END)  # Clear the entry field after registration
        else:
            messagebox.showwarning("Warning", f"Vehicle {vehicle_id} is already registered.")

# Create the main window for the GUI
root = tk.Tk()

# Create an instance of the VehicleRegistrationApp
app = VehicleRegistrationApp(root)

# Run the Tkinter event loop
root.mainloop()
