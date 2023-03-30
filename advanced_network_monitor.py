import threading
import json
import time
import os
import socket
import tkinter as tk
from tkinter import ttk
from urllib.parse import urlparse
from datetime import datetime
import psutil
import speedtest
from adblockparser import AdblockRules


class AppConfig:
    def __init__(self):
        self.interval = 60


app = AppConfig()

# Carregar regras do Adblock
with open("easylist.txt", "r", encoding="utf-8") as f:
    raw_rules = f.readlines()
rules = AdblockRules(raw_rules)


def test_speed():
    st = speedtest.Speedtest()
    st.get_best_server()

    download_speed = st.download() / 1024 / 1024  # Converter para Mbps
    upload_speed = st.upload() / 1024 / 1024     # Converter para Mbps
    latency = st.results.ping                    # Latência em ms

    return download_speed, upload_speed, latency


def get_network_traffic():
    net_io = psutil.net_io_counters(pernic=True)
    return net_io


def monitor_network():
    prev_net_io = get_network_traffic()
    time.sleep(1)
    curr_net_io = get_network_traffic()

    traffic_data = {}
    for iface in curr_net_io:
        traffic_data[iface] = {
            'bytes_sent': curr_net_io[iface].bytes_sent - prev_net_io[iface].bytes_sent,
            'bytes_received': curr_net_io[iface].bytes_recv - prev_net_io[iface].bytes_recv
        }
    return traffic_data


def get_ad_traffic(hostname, traffic_data):
    if rules.should_block(hostname):
        return traffic_data
    return {'bytes_sent': 0, 'bytes_received': 0}


def save_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def create_gui():
    def update_interval():
        try:
            interval = int(interval_var.get())
            if interval < 1:
                raise ValueError
            app.interval = interval
            interval_label.config(
                text=f"Intervalo atual: {app.interval} segundos")
        except ValueError:
            interval_label.config(
                text="Intervalo inválido. Insira um número inteiro maior que 0.")

    root = tk.Tk()
    root.title("Monitor de Rede Avançado")

    mainframe = ttk.Frame(root, padding="10")
    mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    interval_label = ttk.Label(
        mainframe, text=f"Intervalo atual: {app.interval} segundos")
    interval_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

    interval_var = tk.StringVar()
    interval_entry = ttk.Entry(mainframe, textvariable=interval_var)
    interval_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5)

    update_button = ttk.Button(
        mainframe, text="Atualizar Intervalo", command=update_interval)
    update_button.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

    root.mainloop()


def main():
    results = []

    if not os.path.exists('network_data.json'):
        with open('network_data.json', 'w') as file:
            json.dump([], file)

    with open('network_data.json', 'r') as file:
        data = json.load(file)
        if data:
            results = data

    def run_tests():
        while True:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            download_speed, upload_speed, latency = test_speed()
            traffic_data = monitor_network()

            ad_traffic = {}
            for iface in traffic_data:
                hostname = socket.gethostbyaddr(iface)[0]
                ad_traffic[iface] = get_ad_traffic(
                    hostname, traffic_data[iface])

            result = {
                'timestamp': timestamp,
                'download_speed': download_speed,
                'upload_speed': upload_speed,
                'latency': latency,
                'traffic_data': traffic_data,
                'ad_traffic': ad_traffic
            }
            results.append(result)
            save_to_json(results, 'network_data.json')

            print(f"Timestamp: {timestamp} | Download: {download_speed:.2f} Mbps | Upload: {upload_speed:.2f} Mbps | "
                  f"Latency: {latency:.2f} ms | Traffic data: {traffic_data} | Ad traffic: {ad_traffic}")

            time.sleep(app.interval)

    # Inicie a interface gráfica do usuário e as medições em threads separadas
    gui_thread = threading.Thread(target=create_gui)
    gui_thread.daemon = True
    gui_thread.start()

    run_tests()


if __name__ == "main":
    main()
