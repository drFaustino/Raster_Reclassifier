from qgis.core import QgsTask, QgsMessageLog, Qgis
import numpy as np
import matplotlib.pyplot as plt
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtCore import QThread


class ReclassifierTask(QgsTask):
    progressChanged = pyqtSignal(int)

    def __init__(self, description, data, min_val, max_val, stats, num_classes, method,
                 hist_color=None, line_color=None):
        super().__init__(description, QgsTask.CanCancel)

        self.data = data
        self.min_val = min_val
        self.max_val = max_val
        self.stats = stats
        self.num_classes = num_classes
        self.method = method

        self.hist_color = hist_color
        self.line_color = line_color

        self.breaks = None
        self.fig = None

    def run(self):
        try:
            self.setProgress(5)

            data = self.data
            num_classes = self.num_classes
            min_val = self.min_val
            max_val = self.max_val
            method = self.method

            # -------------------------
            # CLASSIFICAZIONE
            # -------------------------
            if method == 0:
                self.breaks = np.linspace(min_val, max_val, num_classes + 1)

            elif method == 1:
                self.breaks = np.percentile(data, np.linspace(0, 100, num_classes + 1))

            elif method == 2:
                self.progressChanged.emit(20)

                from sklearn.cluster import KMeans
                X = data.reshape(-1, 1)
                # Simulazione avanzamento progress bar durante KMeans
                for p in range(20, 60, 5):
                    self.progressChanged.emit(p)
                    self.setProgress(p)
                    QThread.msleep(80)  # piccola pausa per rendere visibile l'avanzamento

                # Fit reale (bloccante ma in thread separato)
                km = KMeans(n_clusters=num_classes, n_init=10, random_state=0).fit(X)

                centers = sorted(km.cluster_centers_.flatten())
                self.breaks = [
                    min_val
                ] + [
                    (centers[i] + centers[i + 1]) / 2
                    for i in range(len(centers) - 1)
                ] + [max_val]

            elif method == 3:
                # Natural Breaks (approx) — velocissimo
                # 1. Istogramma
                _, bin_edges = np.histogram(data, bins=256)

                # 2. Applica Jenks sui bin (256 valori, non milioni)
                def jenks_on_bins(values, k):
                    n = len(values)
                    mat1 = np.zeros((n + 1, k + 1))
                    mat2 = np.zeros((n + 1, k + 1))

                    for i in range(1, k + 1):
                        mat1[0][i] = 1
                        mat2[0][i] = 0
                        for j in range(1, n + 1):
                            mat2[j][i] = float('inf')

                    v = 0.0

                    for level in range(2, n + 1):
                        s1 = s2 = w = 0.0
                        for m in range(1, level + 1):
                            i3 = level - m + 1
                            val = values[i3 - 1]
                            s2 += val * val
                            s1 += val
                            w += 1
                            v = s2 - (s1 * s1) / w
                            i4 = i3 - 1
                            if i4 != 0:
                                for j in range(2, k + 1):
                                    if mat2[level][j] >= (v + mat2[i4][j - 1]):
                                        mat1[level][j] = i3
                                        mat2[level][j] = v + mat2[i4][j - 1]
                        mat1[level][1] = 1
                        mat2[level][1] = v

                    kclass = [0] * (k + 1)
                    kclass[k] = values[-1]
                    idx = n

                    for j in range(k, 1, -1):
                        idxt = int(mat1[idx][j]) - 2
                        kclass[j - 1] = values[idxt]
                        idx = int(mat1[idx][j] - 1)

                    kclass[0] = values[0]
                    return kclass

                # 3. Applica Jenks ai bin
                bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                approx_breaks = jenks_on_bins(bin_centers, num_classes)

                # 4. Assicura min e max corretti
                approx_breaks[0] = min_val
                approx_breaks[-1] = max_val

                self.breaks = approx_breaks

            elif method == 4:
                self.breaks = [None] * (num_classes + 1)

            self.progressChanged.emit(60)

            # -------------------------
            # GRAFICO
            # -------------------------
            plt.close("all")
            fig = plt.figure(figsize=(4.41, 3.41))
            ax = fig.add_subplot(111)
            ax.grid(True)
            ax.hist(data, bins=200, color=self.hist_color, alpha=0.7)

            self.progressChanged.emit(80)

            if method != 4:
                for b in self.breaks:
                    ax.axvline(b, color=self.line_color, linestyle="--", linewidth=1)

            self.fig = fig

            self.setProgress(100)
            return True

        except Exception as e:
            QgsMessageLog.logMessage(str(e), "Reclassifier", Qgis.Critical)
            return False
