import cv2
from pyzbar.pyzbar import decode
import json
import tkinter as tk
from tkinter import messagebox
import threading
import sqlite3


class QRTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Garage Service Tracking")

        # Frame for User Information
        self.user_info_frame = tk.Frame(root)
        self.user_info_frame.pack(pady=10)

        # Frame for status messages
        self.status_label = tk.Label(root, text="", font=("Helvetica", 12), fg="green")
        self.status_label.pack(pady=5)

        # Frame to hold services and their statuses
        self.services_frame = tk.Frame(root)
        self.services_frame.pack(pady=10)

        # Start QR code scanning
        scan_button = tk.Button(root, text="Start Scanning", command=self.start_scan)
        scan_button.pack(pady=10)

    def start_scan(self):
        # Open a separate thread to avoid blocking the UI while scanning
        scan_thread = threading.Thread(target=self.scan_qr_code)
        scan_thread.start()

    def scan_qr_code(self):
        # Try capturing video from the webcam
        print("Opening camera...")
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        print("Camera opened successfully. Scanning...")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            decoded_objects = decode(frame)
            if decoded_objects:
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    print("QR Data:", qr_data)  # Debugging to verify content

                    try:
                        data = json.loads(qr_data)  # Parse JSON data
                        vehicle_number = data.get("Vehicle Number")
                        if vehicle_number:
                            self.fetch_and_display_info(vehicle_number)
                            cap.release()  # Close the camera
                            cv2.destroyAllWindows()  # Close the video window
                            return  # Stop scanning once a valid QR code is found
                    except json.JSONDecodeError as e:
                        print("Error decoding JSON:", e)

            cv2.imshow('QR Code Scanner', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
                break

        cap.release()
        cv2.destroyAllWindows()

    def fetch_and_display_info(self, vehicle_number):
        """Fetch vehicle information from the database and display it."""
        # Clear the previous vehicle info
        for widget in self.user_info_frame.winfo_children():
            widget.destroy()

        # Query the database for the vehicle information
        conn = sqlite3.connect("vehicle_registration.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehicles WHERE vehicle_number = ?", (vehicle_number,))
        row = cursor.fetchone()
        conn.close()

        if row:
            # row is a tuple of all columns; unpack it based on the table structure
            (id, mobile_no, first_name, last_name, address, pincode,
             vehicle_type, vehicle_brand, vehicle_number, services,
             total_price, status, qr_code) = row

            # Display user information
            tk.Label(self.user_info_frame, text=f"First Name: {first_name}", font=("Helvetica", 14)).pack(anchor='w')
            tk.Label(self.user_info_frame, text=f"Last Name: {last_name}", font=("Helvetica", 14)).pack(anchor='w')
            tk.Label(self.user_info_frame, text=f"Mobile No: {mobile_no}", font=("Helvetica", 14)).pack(anchor='w')
            tk.Label(self.user_info_frame, text=f"Address: {address}", font=("Helvetica", 14)).pack(anchor='w')
            tk.Label(self.user_info_frame, text=f"Pincode: {pincode}", font=("Helvetica", 14)).pack(anchor='w')
            tk.Label(self.user_info_frame, text=f"Vehicle Type: {vehicle_type}", font=("Helvetica", 14)).pack(
                anchor='w')
            tk.Label(self.user_info_frame, text=f"Vehicle Brand: {vehicle_brand}", font=("Helvetica", 14)).pack(
                anchor='w')
            tk.Label(self.user_info_frame, text=f"Vehicle Number: {vehicle_number}", font=("Helvetica", 14)).pack(
                anchor='w')

            # Clear the previous service widgets
            for widget in self.services_frame.winfo_children():
                widget.destroy()

            # Display services and their statuses
            services_list = services.split(',') if services else []
            for service in services_list:
                service_label = tk.Label(self.services_frame, text=f"Service: {service.strip()}",
                                         font=("Helvetica", 12))
                service_label.pack(anchor='w')

            # Display total price
            tk.Label(self.services_frame, text=f"Total Price: ₹{total_price}", font=("Helvetica", 14)).pack(anchor='w')
            tk.Label(self.services_frame, text=f"Status: {status}", font=("Helvetica", 14)).pack(anchor='w')

            # Display a message about the current status
            self.status_label.config(text="Vehicle information loaded successfully.", fg="green")
        else:
            messagebox.showerror("Error", "Vehicle not found in the database.")
            self.status_label.config(text="Vehicle not found.", fg="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = QRTrackingApp(root)
    root.mainloop()
