import tkinter as tk
from tkinter import ttk
import cv2
import threading
import socket
import requests

class VideoDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem de afisare video pe ecrane multiple")

        self.config = {
            'num_monitors': 2,
            'resolution': (1920, 1080),
            'video_path': ''
        }

        self.cap = None
        self.client_positions = {}

        self.setup_ui()

    def setup_ui(self):
        self.num_monitors_label = ttk.Label(self.root, text="Numar de monitoare:")
        self.num_monitors_label.pack()

        self.num_monitors_entry = ttk.Entry(self.root, width=5)
        self.num_monitors_entry.pack()
        self.num_monitors_entry.insert(0, self.config['num_monitors'])

        self.resolution_label = ttk.Label(self.root, text="Rezolutie: 1920x1080")
        self.resolution_label.pack()

        self.video_path_label = ttk.Label(self.root, text="Video Link:")
        self.video_path_label.pack()

        self.video_path_entry = ttk.Entry(self.root, width=50)
        self.video_path_entry.pack()
        self.video_path_entry.insert(0, self.config['video_path'])

        self.find_clients_button = ttk.Button(self.root, text="Gaseste Clienti", command=self.find_and_assign_clients)
        self.find_clients_button.pack()

        self.load_button = ttk.Button(self.root, text="Incarcare Video", command=self.load_video)
        self.load_button.pack()

        self.play_button = ttk.Button(self.root, text="Play Video", command=self.play_video)
        self.play_button.pack()

    def load_video(self):
        self.config['video_path'] = self.video_path_entry.get()
        self.cap = cv2.VideoCapture(self.config['video_path'])
        self.config['num_monitors'] = int(self.num_monitors_entry.get())

    def find_clients(self):
        server_ip = "10.0.2.15"  # Înlocuiește cu adresa IP a serverului tău
        server_port = 12345  # Înlocuiește cu portul serverului tău

        client_ips = []

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        try:
            s.bind(("", server_port))
            s.sendto(b"find_clients", (server_ip, server_port))
            while True:
                try:
                    data, addr = s.recvfrom(1024)
                    if data.decode() == "client_found":
                        client_ips.append(addr[0])
                except socket.timeout:
                    break
        finally:
            s.close()

        return client_ips

    def find_and_assign_clients(self):
        client_ips = self.find_clients()

        if not client_ips:
            print("No clients found.")
            return

        self.client_positions = {}
        for i, client_ip in enumerate(client_ips):
            self.client_positions[client_ip] = i

        print("Clients found:")
        for i, client_ip in enumerate(client_ips):
            print(f"Client {i + 1}: {client_ip}")

    def start_client_playback(self, client_ip, client_position, client_data):
        client_port = 12345  # Portul la care ascultă clientul pentru comenzi
        response = requests.post(f"http://{client_ip}:{client_port}/start_playback", json=client_data)
        if response.status_code != 200:
            print(f"Failed to start playback on client {client_ip}")
        else:
            print(f"Playback started on client {client_ip} at position {client_position}")

    def play_video(self):
        if self.cap is None:
            return

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(self.cap.get(3))
        frame_height = int(self.cap.get(4))

        monitor_cols = int(self.config['num_monitors'] ** 0.5)
        monitor_rows = (self.config['num_monitors'] + monitor_cols - 1) // monitor_cols
        monitor_frame_width = frame_width // monitor_cols
        monitor_frame_height = frame_height // monitor_rows

        for i, client_ip in enumerate(self.client_positions.keys()):
            col = i % monitor_cols
            row = i // monitor_cols
            start_x = col * monitor_frame_width
            start_y = row * monitor_frame_height
            end_x = start_x + monitor_frame_width
            end_y = start_y + monitor_frame_height

            client_position = self.client_positions[client_ip]
            client_data = {
                'frame_width': monitor_frame_width,
                'frame_height': monitor_frame_height,
                'start_x': start_x,
                'start_y': start_y,
                'end_x': end_x,
                'end_y': end_y,
                'fps': fps,
                'video_path': self.config['video_path']
            }

            threading.Thread(target=self.start_client_playback, args=(client_ip, client_position, client_data)).start()

    def quit(self):
        if self.cap:
            self.cap.release()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDisplayApp(root)
    root.protocol("WM_DELETE_WINDOW", app.quit)
    root.mainloop()
