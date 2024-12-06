#!/usr/bin/env python
# coding: utf-8

# In[159]:



# In[1]:


import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import qrcode
from io import BytesIO
import json
import sqlite3  # For database connection
import cv2


# In[2]:


# Database setup
def create_connection():
    conn = sqlite3.connect('vehicle_registration.db')
    return conn


def create_user_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mobile_no TEXT UNIQUE,
                        password TEXT
                    )''')
    conn.commit()
    conn.close()


def create_vehicle_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mobile_no TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        address TEXT,
                        pincode TEXT,
                        vehicle_type TEXT,
                        vehicle_brand TEXT,
                        vehicle_number TEXT,
                        services TEXT,
                        total_price REAL,
                        status TEXT,
                        qr_code BLOB,
                        FOREIGN KEY (mobile_no) REFERENCES users (mobile_no)
                    )''')
    conn.commit()
    conn.close()


# In[3]:


# Function to generate QR code
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save('last.png')
    return img


# In[4]:


# Function to handle user registration
def register_user():
    mobile_no = mobile_entry.get()
    password = password_entry.get()

    if not (mobile_no and password):
        messagebox.showerror("Error", "Please fill in all fields!")
        return

    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (mobile_no, password) VALUES (?, ?)", (mobile_no, password))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful! Please login.")
        login_frame()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Mobile number already exists!")
    finally:
        conn.close()


# Function to handle user login
def handle_login():
    mobile_no = mobile_no_login_entry.get()
    password = password_login_entry.get()

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE mobile_no = ? AND password = ?", (mobile_no, password))
    user = cursor.fetchone()

    # Check for admin credentials
    if mobile_no == "admin" and password == "admin":
        admin_vehicle_data_frame()
    elif user:
        messagebox.showinfo("Success", "Login successful!")
        vehicle_registration_frame()
    else:
        messagebox.showerror("Error", "Invalid mobile number or password!")
    conn.close()


# In[5]:


# Function to submit vehicle registration
def submit_vehicle_form():
    first_name = first_name_entry.get()
    last_name = last_name_entry.get()
    mobile_no = mobile_no_entry.get()
    address = address_entry.get()
    pincode = pincode_entry.get()
    vehicle_type = vehicle_type_combo.get()
    vehicle_brand = vehicle_brand_entry.get()
    vehicle_number = vehicle_number_entry.get()

    # Collect selected services
    selected_services = []
    total_price = 0
    for service, price, var in services:
        if var.get() == 1:
            selected_services.append(f"{service} (₹{price})")
            total_price += price

    if not (first_name and last_name and mobile_no and vehicle_type and vehicle_brand and vehicle_number):
        messagebox.showerror("Error", "Please fill in all the required fields!")
        return

    if len(mobile_no) != 10 or not mobile_no.isdigit():
        messagebox.showerror("Error", "Mobile number must be exactly 10 digits!")
        return

    # Combine all the data to store in the QR code
    services_info = ", ".join(selected_services)
    data = {
        "First Name": first_name,
        "Last Name": last_name,
        "Mobile No": mobile_no,
        "Address": address,
        "Pincode": pincode,
        "Vehicle Type": vehicle_type,
        "Vehicle Brand": vehicle_brand,
        "Vehicle Number": vehicle_number,
        "Services": selected_services,
        "Total Price": total_price
    }
    qr_data = json.dumps(data)

    # Generate and save QR code
    img = generate_qr_code(qr_data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_data = buffer.getvalue()

    # Save data to the database
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO vehicles 
                      (mobile_no, first_name, last_name, address, pincode, vehicle_type, vehicle_brand, vehicle_number, services, total_price, status, qr_code)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (mobile_no, first_name, last_name, address, pincode, vehicle_type, vehicle_brand, vehicle_number,
                    services_info, total_price, "Not Started", qr_code_data))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Vehicle data and QR code saved successfully!")

    # Display QR code in the GUI
    buffer.seek(0)
    qr_img = Image.open(buffer)
    qr_img.thumbnail((200, 200))
    qr_photo = ImageTk.PhotoImage(qr_img)
    barcode_label.config(image=qr_photo)
    barcode_label.image = qr_photo


# In[6]:


# Function to switch to login frame
def login_frame():
    clear_frame()
    login_frame = tk.Frame(canvas, bg="#2d2d44", bd=5)
    canvas.create_window((0, 0), window=login_frame, anchor='nw', width=500, height=400)

    # Title
    tk.Label(
        login_frame,
        text="Welcome to Dr.Vehicle",
        font=("Arial", 18, "bold"),
        bg="#2d2d44",
        fg="#ffffff"
    ).pack(pady=20)

    # Subtitle
    tk.Label(
        login_frame,
        text="Please login to continue",
        font=("Arial", 12),
        bg="#2d2d44",
        fg="#b0b0c9"
    ).pack(pady=5)

    tk.Label(login_frame, text="Mobile No.", font=("Arial", 12), bg="#2d2d44", fg="#ffffff").pack(pady=10)
    global mobile_no_login_entry
    mobile_no_login_entry = tk.Entry(login_frame, font=("Arial", 12), width=25)
    mobile_no_login_entry.pack()

    tk.Label(login_frame, text="Password", font=("Arial", 12), bg="#2d2d44", fg="#ffffff").pack(pady=10)
    global password_login_entry
    password_login_entry = tk.Entry(login_frame, font=("Arial", 12), show='*')
    password_login_entry.pack()

    login_button = tk.Button(login_frame, text="Login", command=handle_login, font=("Arial", 12), bg="#4CAF50",
                             fg="white", width=15)
    login_button.pack(pady=20)

    register_button = tk.Button(login_frame, text="Register", command=register_frame, font=("Arial", 12), bg="#4CAF50",
                                fg="white", width=15)
    register_button.pack(pady=10)


# In[7]:


# Function to switch to registration frame
def register_frame():
    clear_frame()
    registration_frame = tk.Frame(canvas, bg="#2d2d44", bd=5)
    canvas.create_window((0, 0), window=registration_frame, anchor='nw', width=500, height=400)

    tk.Label(registration_frame, text="Register", font=("Arial", 18, "bold"), bg="#2d2d44", fg="#ffffff").pack(pady=10)

    tk.Label(registration_frame, text="Mobile No.", font=("Arial", 12), bg="#f0f0f5").pack(pady=5)
    global mobile_entry
    mobile_entry = tk.Entry(registration_frame, font=("Arial", 12))
    mobile_entry.pack(pady=5)

    tk.Label(registration_frame, text="Password", font=("Arial", 12), bg="#f0f0f5").pack(pady=5)
    global password_entry
    password_entry = tk.Entry(registration_frame, font=("Arial", 12), show='*')
    password_entry.pack(pady=5)

    register_button = tk.Button(registration_frame, text="Register", command=register_user, font=("Arial", 12),
                                bg="#4CAF50", fg="white")
    register_button.pack(pady=10)


# In[8]:


# Function to show the vehicle registration form
def vehicle_registration_frame():
    clear_frame()
    vehicle_registration_frame = tk.Frame(canvas, bg="#2d2d44", bd=5)
    canvas.create_window((0, 0), window=vehicle_registration_frame, anchor='nw', width=600, height=1000)

    tk.Label(vehicle_registration_frame, text="Vehicle Registration Form", font=("Arial", 18, "bold"), bg="#2d2d44",
             fg="#ffffff").grid(row=0, column=0, columnspan=2, pady=20)

    tk.Label(vehicle_registration_frame, text="First Name :", font=("Arial", 12), bg="#2d2d44", fg="#ffffff").grid(
        row=1, column=0, padx=10, pady=5, sticky='w')
    global first_name_entry
    first_name_entry = tk.Entry(vehicle_registration_frame, font=("Arial", 12), width=25)
    first_name_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(vehicle_registration_frame, text="Last Name :", font=("Arial", 12), bg="#2d2d44", fg="#ffffff").grid(row=2,
                                                                                                                  column=0,
                                                                                                                  padx=10,
                                                                                                                  pady=5,
                                                                                                                  sticky='w')
    global last_name_entry
    last_name_entry = tk.Entry(vehicle_registration_frame, font=("Arial", 12), width=25)
    last_name_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(vehicle_registration_frame, text="Mobile No. :", font=("Arial", 12), bg="#2d2d44", fg="#ffffff").grid(
        row=3, column=0, padx=10, pady=5, sticky='w')
    global mobile_no_entry
    mobile_no_entry = tk.Entry(vehicle_registration_frame, font=("Arial", 12), width=25)
    mobile_no_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(vehicle_registration_frame, text="Address :", font=("Arial", 12), bg="#2d2d44", fg="#ffffff").grid(row=4,
                                                                                                                column=0,
                                                                                                                padx=10,
                                                                                                                pady=5,
                                                                                                                sticky='w')
    global address_entry
    address_entry = tk.Entry(vehicle_registration_frame, font=("Arial", 12), width=25)
    address_entry.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(vehicle_registration_frame, text="Pincode :", font=("Arial", 12), bg="#2d2d44", fg="#ffffff").grid(row=5,
                                                                                                                column=0,
                                                                                                                padx=10,
                                                                                                                pady=5,
                                                                                                                sticky='w')
    global pincode_entry
    pincode_entry = tk.Entry(vehicle_registration_frame, font=("Arial", 12), width=25)
    pincode_entry.grid(row=5, column=1, padx=10, pady=5)

    tk.Label(vehicle_registration_frame, text="Vehicle Type :", font=("Arial", 12), bg="#2d2d44", fg="#ffffff").grid(
        row=6, column=0, padx=10, pady=5, sticky='w')
    global vehicle_type_combo
    vehicle_type_combo = ttk.Combobox(vehicle_registration_frame, values=["Car", "Bike", "Truck"], font=("Arial", 12))
    vehicle_type_combo.grid(row=6, column=1, padx=10, pady=5)

    tk.Label(vehicle_registration_frame, text="Vehicle Brand :", font=("Arial", 12), bg="#2d2d44", fg="#ffffff").grid(
        row=7, column=0, padx=10, pady=5, sticky='w')
    global vehicle_brand_entry
    vehicle_brand_entry = tk.Entry(vehicle_registration_frame, font=("Arial", 12), width=25)
    vehicle_brand_entry.grid(row=7, column=1, padx=10, pady=5)

    tk.Label(vehicle_registration_frame, text="Vehicle Number :", font=("Arial", 12), bg="#2d2d44", fg="#ffffff").grid(
        row=8, column=0, padx=10, pady=5, sticky='w')
    global vehicle_number_entry
    vehicle_number_entry = tk.Entry(vehicle_registration_frame, font=("Arial", 12), width=25)
    vehicle_number_entry.grid(row=8, column=1, padx=10, pady=5)

    tk.Label(vehicle_registration_frame, text="Select Services", font=("Arial", 15, "bold"), bg="#2d2d44",
             fg="#ffffff").grid(row=9, column=0, columnspan=2, pady=10)

    # Services with prices
    global services
    services = [
        ("Oil Change", 1000, tk.IntVar()),
        ("Tire Rotation", 500, tk.IntVar()),
        ("Brake Inspection", 700, tk.IntVar()),
        ("Battery Check", 300, tk.IntVar()),
        ("Transmission Fluid Change", 1200, tk.IntVar()),
        ("Radiator Flush", 800, tk.IntVar()),
        ("Wheel Alignment", 600, tk.IntVar()),
    ]

    for index, (service, price, var) in enumerate(services):
        tk.Checkbutton(vehicle_registration_frame, text=f"{service} (₹{price})", variable=var, bg="white",
                       fg="green").grid(row=10 + index, column=0, columnspan=2, sticky='w')

    submit_button = tk.Button(vehicle_registration_frame, text="Submit", command=submit_vehicle_form,
                              font=("Arial", 12), bg="#4CAF50", fg="white")
    submit_button.grid(row=10 + len(services), column=0, columnspan=2, pady=10)

    global barcode_label
    barcode_label = tk.Label(vehicle_registration_frame, bg="#f0f0f5")
    barcode_label.grid(row=11 + len(services), column=0, columnspan=2, pady=10)

    # Logout Button
    logout_button = tk.Button(vehicle_registration_frame, text="Logout", command=login_frame, font=("Arial", 12),
                              bg="#FF5733", fg="white")
    logout_button.grid(row=12 + len(services), column=0, columnspan=2, pady=10)


# Function to clear the frame
def clear_frame():
    for widget in canvas.winfo_children():
        widget.destroy()


# In[9]:


# Function to display admin vehicle data
def admin_vehicle_data_frame():
    clear_frame()
    admin_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=admin_frame, anchor='nw')

    tk.Label(admin_frame, text="Admin - Vehicle Data", font=("Arial", 18, "bold"), bg="#f0f0f5").pack(pady=10)

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()
    conn.close()

    for index, vehicle in enumerate(vehicles):
        vehicle_data = f"ID: {vehicle[0]}, Mobile No: {vehicle[1]}, Name: {vehicle[2]} {vehicle[3]}, Vehicle Number: {vehicle[8]}, Status: {vehicle[11]}"
        tk.Label(admin_frame, text=vehicle_data, font=("Arial", 12), bg="#f0f0f5").pack(pady=5)

        status_label = tk.Label(admin_frame, text="Change Status:", font=("Arial", 10), bg="#f0f0f5")
        status_label.pack()

        status_var = tk.StringVar(value=vehicle[11])
        status_combo = ttk.Combobox(admin_frame, textvariable=status_var,
                                    values=["Not Started", "In Process", "Completed"], state="readonly")
        status_combo.pack(pady=5)

        def update_status(vehicle_id, status_combo):
            new_status = status_combo.get()
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE vehicles SET status = ? WHERE id = ?", (new_status, vehicle_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Status updated successfully!")
            admin_vehicle_data_frame()

        update_button = tk.Button(admin_frame, text="Update",
                                  command=lambda v_id=vehicle[0]: update_status(v_id, status_combo), font=("Arial", 10),
                                  bg="#4CAF50", fg="white")
        update_button.pack(pady=5)

    back_button = tk.Button(admin_frame, text="Back to Login", command=login_frame, font=("Arial", 12), bg="#4CAF50",
                            fg="white")
    back_button.pack(pady=10)

    # Logout Button
    logout_button = tk.Button(admin_frame, text="Logout", command=login_frame, font=("Arial", 12), bg="#FF5733",
                              fg="white")
    logout_button.pack(pady=10)


# In[ ]:


# Main application setup
root = tk.Tk()
root.title("Dr.Vehicle")
root.geometry("500x400")
root.configure(bg="#f0f0f5")

canvas = tk.Canvas(root, bg="#1f1f2e", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

create_user_table()
create_vehicle_table()

login_frame()  # Start with the login frame
root.mainloop()

# In[ ]:




