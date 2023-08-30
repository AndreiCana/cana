import socket
import tkinter as tk
from tkinter import simpledialog

class VideoClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False

    def run(self):
        if not self.connect_to_server():
            return

        self.client_socket.send(b"CLIENT_READY")

        # Așteaptă să primească cererea de informații despre clienți
        response = self.client_socket.recv(1024)
        if response == b"REQUEST_CLIENT_INFO":
            self.send_client_info()

        self.client_socket.close()

    def send_client_info(self):
        num_monitors = simpledialog.askinteger("Numar de monitoare", "Introduceti numarul de monitoare:")
        monitor_positions = []

        for i in range(num_monitors):
            position = simpledialog.askstring(f"Pozitie monitor {i+1}", f"Introduceti pozitia monitorului {i+1} (ex. '0,0'):")
            monitor_positions.append(position)

        client_info = f"{num_monitors};{'|'.join(monitor_positions)}"
        self.client_socket.send(client_info.encode())
        print("Informatii client trimise cu succes.")

if __name__ == "__main__":
    server_ip = "10.0.2.15"
    server_port = 12345

    client = VideoClient(server_ip, server_port)
    client.run()
