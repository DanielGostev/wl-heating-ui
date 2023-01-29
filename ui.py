import time
import numpy as np

from sensor_data import SensorLogger
from nicegui import ui
from datetime import datetime
from threading import Thread


class WebUI:
    def __init__(self, sensor_logger: SensorLogger):
        self._sensor_logger = sensor_logger
        self.__draw_ui__()

    def run(self):
        t = Thread(target=self._label_updater)
        t.start()
        ui.run(reload=False)

    def _label_updater(self):
        while True:
            if not self._sensor_logger.enable_logging:
                self._label1.set_text("Sensor: Pico_fb, no active measurements")
            else:
                sd = self._sensor_logger.get_data(sensor_id="pico_fb_1")
                if sd is not None:
                    last_data = sd[-1]
                    self._label1.set_text("Sensor ID: " + last_data.sensor_id + " Temperature: " +
                                          str(last_data.temperature) + " " +
                                          datetime.fromtimestamp(last_data.timestamp).strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    self._label1.set_text("Sensor Pico_fb no data")
            time.sleep(1.0)

    def update_line_plot(self) -> None:
        if not self._sensor_logger.enable_logging:
            return
        sd = self._sensor_logger.get_data(sensor_id="pico_fb_1")
        if sd is not None:
            self.line_plot.push_data(sd)

    def _start_measurement(self):
        self._sensor_logger.enable_logging = True
        self.line_updates = ui.timer(0.5, self.update_line_plot, active=True)
        ui.notify("Starting Measuring")

    def _stop_measurement(self):
        self._sensor_logger.enable_logging = False
        self.line_updates = ui.timer(0.1, self.update_line_plot, active=False)
        ui.notify("Stop Measuring")

    def __draw_ui__(self):
        self._label1 = ui.label("1")
        self.label2 = ui.label("2")
        self.label3 = ui.label("3")
        self.label4 = ui.label("4")
        self.line_plot = TemperaturePlot()

        # with ui.row():
        #     with ui.plot(figsize=(5, 3)):
        #         x = np.linspace(0.0, 5.0)
        #         y1 = np.linspace(0.0, 6.1)
        #         y2 = np.linspace(0.0, 5)
        #         y3 = np.linspace(0.0, 54)
        #         y4 = np.linspace(0.0, 12)
        #         plt.plot(x, y1, '-', x, y2, '-', x, y3, '-', x, y4, '-')

        ui.label("Auto Mode")
        with ui.row():
            slider = ui.slider(min=0, max=75, step=1, value=20)
            ui.linear_progress().bind_value_from(slider, 'value')
            ui.button('Auto Mode Start', on_click=lambda: self._start_measurement())
            ui.button('Stop Measurements', on_click=lambda: self._stop_measurement())

        ui.label("Manual Mode")
        with ui.row():
            ui.button('Heaters On', on_click=lambda: ui.notify(f'You clicked me!'))
            ui.button('Ventilators On', on_click=lambda: ui.notify(f'You clicked me!'))
        with ui.row():
            ui.button('Ventilators Off', on_click=lambda: ui.notify(f'You clicked me!'))
            ui.button('Heaters Off', on_click=lambda: ui.notify(f'You clicked me!'))


class TemperaturePlot:
    def __init__(self):
        self.line_plot = ui.line_plot(n=1, limit=4200, figsize=(12, 5), update_every=1) \
            .with_legend(['pico_fb'], loc='upper center', ncol=2)
        self._last_push = {}

    def push_data(self, sensor_data):
        last_data = sensor_data[-1]
        y1 = last_data.temperature
        if last_data.sensor_id not in self._last_push or last_data.timestamp > self._last_push[last_data.sensor_id]:
            self.line_plot.push([last_data.timestamp], [[y1]])
            self._last_push[last_data.sensor_id] = last_data.timestamp

