import csv
import os
import speedtest
import tkinter as tk
from datetime import datetime
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

results = []
results_lock = threading.Lock()


class SpeedTestApp:
    def __init__(self, interval):
        """
        Inicializa a aplicação com um intervalo específico entre os testes de velocidade.

        :param interval: Intervalo em segundos entre os testes de velocidade.
        """
        self.interval = interval

    def run(self):
        """
        Executa testes de velocidade continuamente e armazena os resultados.
        """
        while True:
            result = self.perform_speedtest()
            with results_lock:
                results.append(result)
                self.save_result_to_csv(result)
            print(f"{result['timestamp']} - Download: {result['download_speed']} Mbps, Upload: {result['upload_speed']} Mbps, Latency: {result['latency']} ms")
            time.sleep(self.interval)

    def perform_speedtest(self):
        """
        Realiza um único teste de velocidade e devolve os resultados.

        :return: Dicionário que contem o timestamp, velocidade de download, velocidade de upload e latência.
        """
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = round(st.download() / (10**6), 2)
        upload_speed = round(st.upload() / (10**6), 2)
        latency = round(st.results.ping, 2)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {'timestamp': timestamp, 'download_speed': download_speed, 'upload_speed': upload_speed, 'latency': latency}

    def save_result_to_csv(self, result):
        """
        Aramazena o resultado do teste de velocidade num ficheiro CSV.

        :param result: Dicionário que contem o timestamp, velocidade de download, velocidade de upload e latência.
        """
        csv_file = 'speedtest_results.csv'
        file_exists = os.path.isfile(csv_file)
        fieldnames = ['timestamp', 'download_speed', 'upload_speed', 'latency']

        with open(csv_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(result)


def update_graphs():
    """
    Atualiza os gráficos na interface gráfica com os resultados dos testes de velocidade.
    """
    with results_lock:
        timestamps = [result['timestamp'] for result in results]
        download_speeds = [result['download_speed'] for result in results]
        upload_speeds = [result['upload_speed'] for result in results]
        latencies = [result['latency'] for result in results]

        if len(results) > 20:
            results.pop(0)

    ax[0].clear()
    ax[1].clear()
    ax[2].clear()

    ax[0].scatter(timestamps, download_speeds, s=10,
                  c='r', label='Pontos de Download')
    ax[1].scatter(timestamps, upload_speeds, s=10,
                  c='b', label='Pontos de Upload')
    ax[2].scatter(timestamps, latencies, s=10,
                  c='g', label='Pontos de Latência')

    ax[0].plot(timestamps, download_speeds, linestyle='--',
               linewidth=0.5, alpha=0.5, color='r')
    ax[1].plot(timestamps, upload_speeds, linestyle='--',
               linewidth=0.5, alpha=0.5, color='b')
    ax[2].plot(timestamps, latencies, linestyle='--',
               linewidth=0.5, alpha=0.5, color='g')

    ax[0].set_ylabel('Mbps')
    ax[2].set_ylabel('ms')

    ax[0].set_title('Velocidade de Download')
    ax[1].set_title('Velocidade de Upload')
    ax[2].set_title('Latência')

    for axis in ax:
        axis.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
        axis.set_axisbelow(True)
        axis.legend()
        for label in axis.get_xticklabels():
            label.set_rotation(45)

    plt.tight_layout()
    canvas.draw()
    root.after(app.interval * 1000, update_graphs)


def create_gui():
    """
    Cria a interface gráfica para exibir os gráficos dos testes de velocidade.
    """
    global root, canvas, ax

    root = tk.Tk()
    root.title("Advanced Network Monitor")
    mainframe = tk.Frame(root)
    mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    fig, ax = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
    canvas = FigureCanvasTkAgg(fig, master=mainframe)
    canvas.get_tk_widget().grid(row=3, column=0, padx=5, pady=5)

    update_graphs()

    root.mainloop()


def main():
    """
    Função principal que inicia a aplicação, executa testes de velocidade e exibe a interface gráfica.
    """
    global app
    app = SpeedTestApp(interval=10)
    speedtest_thread = threading.Thread(target=app.run, daemon=True)
    speedtest_thread.start()

    create_gui()


if __name__ == "__main__":
    main()
