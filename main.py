import numpy as np
import pygame as py
import math
import pyaudio
from scipy.fft import fft, fftfreq

VALUES_PER_SECOND = 20
FPS = 60
DELTA = VALUES_PER_SECOND / FPS

# Переменная для регулировки чувствительности
SENSITIVITY = 1000

# Булевы переменные для включения/выключения эквалайзеров
SHOW_POLYGON = False
SHOW_BARS = False
SHOW_CIRCULAR_BARS = True
SHOW_SOUND_LINE = False


class RealTimeVisualizer:
    def __init__(self):
        # Initialize pyaudio
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=44100,
                                  input=True,
                                  frames_per_buffer=1024)

        self.samplerate = 44100
        self.start = 0
        self.y_origin = 500

        py.init()
        self.screen = py.display.set_mode((600, 600))
        self.clock = py.time.Clock()

    def draw_polygon(self, xf, yf):
        if SHOW_POLYGON:
            points = [(10 + xf[i] / 40, 300 - yf[i] / SENSITIVITY) for i in range(1000)]
            points.append((max(xf) / 40, 300))
            points.append((0, 300))
            py.draw.polygon(self.screen, (100, 100, 255), points)

    def draw_bars(self, xf, yf):
        if SHOW_BARS:
            for i in range(200):
                val = 0
                for j in range(5):
                    val += yf[i + j] / SENSITIVITY
                val /= 5
                py.draw.line(self.screen, (255, 255, 255), (10 + xf[i] / 8, 200 - val), (10 + xf[i] / 8, 200), 2)

    def draw_circular_bars(self, xf, yf):
        if SHOW_CIRCULAR_BARS:
            for i in range(200):
                val = 0
                for j in range(5):
                    val += yf[i + j] / SENSITIVITY
                val /= 5

                ag = xf[i] * math.pi / 2000
                module_ = val

                py.draw.line(self.screen, (255, 255, 255), (300 + math.cos(ag) * 50, 400 + math.sin(ag) * 50),
                             (300 + math.cos(ag) * (50 + val), 400 + math.sin(ag) * (50 + val)), 1)

    def draw_sound_line(self, data):
        if SHOW_SOUND_LINE:
            last_pos = (0, 0)
            for i in range(1000):
                # Use modulo to ensure index is within bounds
                index = (i + self.start) % len(data)
                pos = (i * 6, self.y_origin - data[index] / 400)  # pos_y is every 10th value, divided by 90 to fit
                py.draw.line(self.screen, (255, 255, 255), pos, last_pos, 1)
                last_pos = pos

    def run(self):
        self.run = True

        while self.run:
            self.screen.fill((0, 0, 0))

            for e in py.event.get():
                if e.type == py.QUIT:
                    self.run = False

            # Read data from microphone
            data = np.frombuffer(self.stream.read(1024), dtype=np.int16)

            # Calculate the frequency spectrum
            N = len(data)
            yf = np.abs(fft(data))
            xf = fftfreq(N, 1 / self.samplerate)

            # Draw each type of visualization based on the boolean flags
            self.draw_polygon(xf, yf)
            self.draw_bars(xf, yf)
            self.draw_circular_bars(xf, yf)
            self.draw_sound_line(data)

            self.clock.tick(FPS)
            py.display.set_caption("FPS: " + str(int(self.clock.get_fps())))
            py.display.update()

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


viz = RealTimeVisualizer()
viz.run()
