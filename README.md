# QR_SERVICE_TRACKING

This project automates vehicle service tracking in garages using QR codes to enhance efficiency and transparency.

Features
User Registration

Users can register with their mobile number and password.
User Login

Registered users can log in to:
Search for their car's status.
Use the QR tracking system to monitor updates.
Admin Login

Admin login credentials:
Username: admin
Password: admin
Admin can:
View all vehicle information and statuses.
Update vehicle statuses (Not Starting, In Process, Completed).
Generate bill amounts for vehicles based on services provided.
QR Code Integration

Each vehicle is assigned a unique QR code.
QR codes can be scanned to retrieve vehicle details and service status.
Database Management

Vehicle and user data are stored securely using SQLite3.
All status updates and service details are dynamically reflected in the database.
Project Workflow
User Registration:

Users register using their mobile number and password.
Login Options:

Users can log in to view their vehicle's status or use the QR tracking system.
Admins log in with default credentials to access vehicle data and update statuses.
Vehicle Registration:

After user registration, vehicles are registered in the system with assigned QR codes.
Service Tracking:

Admins update the status of vehicle servicing, which is visible to users.
Billing System:

The admin generates bills based on services provided for each vehicle.
Technologies Used
Programming Language: Python
Database: SQLite3
Libraries:
qrcode for QR code generation.
Pillow for image handling.
Future Enhancements
Advanced analytics for service trends and user behavior.
Multi-language support for broader accessibility.
Integration with payment gateways for seamless transactions.
