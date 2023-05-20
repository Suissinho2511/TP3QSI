import numpy as np
import matplotlib.pyplot as plt

# Definindo os dados
metrics = ['Download Speed', 'Upload Speed', 'Latency']
# Definindo os dados para as conexões wireless
vodafone_stats_wireless = np.array([[403.32, 388.54, 424.64, 11.27],
                                    [99.47, 92.42, 103.8, 3.77],
                                    [8.33, 6.36, 12.63, 2.19]])

meo_stats_wireless = np.array([[362.38, 440.68, 305.82, 38.74],
                               [118.36, 127.89, 108.33, 6.85],
                               [18.54, 24.6, 14.19, 2.38]])

barWidth = 0.25
r1 = np.arange(len(metrics))
r2 = [x + barWidth for x in r1]

plt.figure(figsize=(12, 8))

# Criando as barras
# Criando as barras
plt.bar(r1, vodafone_stats_wireless[:, 0], yerr=vodafone_stats_wireless[:, 3],
        color='b', width=barWidth, edgecolor='grey', label='Vodafone (Wireless)')
plt.bar(r2, meo_stats_wireless[:, 0], yerr=meo_stats_wireless[:, 3],
        color='r', width=barWidth, edgecolor='grey', label='Meo (Wireless)')

# Adicionando labels para as barras
plt.xlabel('Metrics', fontweight='bold')
plt.ylabel('Values', fontweight='bold')
plt.xticks([r + barWidth/2 for r in range(len(metrics))], metrics)

plt.legend()
plt.show()
