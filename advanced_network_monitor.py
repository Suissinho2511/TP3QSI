from logging import root
import threading
import json
import time
import os
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


def save_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def display_results(download_speed, upload_speed, latency, traffic_data):
    download_speed_label.config(
        text=f"Velocidade de Download: {download_speed:.2f} Mbps")
    upload_speed_label.config(
        text=f"Velocidade de Upload: {upload_speed:.2f} Mbps")
    latency_label.config(text=f"Latência: {latency:.2f} ms")
    traffic_data_label.config(
        text=f"Dados de Tráfego: {json.dumps(traffic_data, indent=2)}")


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

    download_speed_label = ttk.Label(mainframe)
    download_speed_label.grid(
        row=3, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

    upload_speed_label = ttk.Label(mainframe)
    upload_speed_label.grid(
        row=4, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

    latency_label = ttk.Label(mainframe)
    latency_label.grid(row=5, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

    traffic_data_label = ttk.Label(mainframe)
    traffic_data_label.grid(
        row=6, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

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

            result = {
                'timestamp': timestamp,
                'download_speed': download_speed,
                'upload_speed': upload_speed,
                'latency': latency,
                'traffic_data': traffic_data
            }
            results.append(result)
            save_to_json(results, 'network_data.json')

            print(f"Timestamp: {timestamp} | Download: {download_speed:.2f} Mbps | Upload: {upload_speed:.2f} Mbps | "
                  f"Latency: {latency:.2f} ms | Traffic data: {traffic_data}")

            root.after(0, display_results, download_speed,
                       upload_speed, latency, traffic_data)

            time.sleep(app.interval)

    # Inicie a interface gráfica do usuário e as medições em threads separadas
    gui_thread = threading.Thread(target=create_gui, name="GUI Thread")
    gui_thread.start()

    run_tests_thread = threading.Thread(
        target=run_tests, name="Run Tests Thread")
    run_tests_thread.start()

    gui_thread.join()
    run_tests_thread.join()

    run_tests()


if __name__ == "__main__":
    main()
