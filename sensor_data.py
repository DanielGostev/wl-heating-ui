class SensorData:
    def __init__(self, sensor_id, temperature, timestamp):
        self.sensor_id = sensor_id
        self.temperature = temperature
        self.timestamp = timestamp


class SensorLogger:
    def __init__(self):
        self._sensor_data = {}
        self.enable_logging = False
        self.last_data = {}

    def log_data(self, sensor_data: SensorData):
        if not self.enable_logging:  # check if we are logging
            return
        if sensor_data.sensor_id in self._sensor_data:  # data with the same key exist
            self._sensor_data[sensor_data.sensor_id].append(sensor_data)  # append data at the end of the array
        else:
            self._sensor_data[sensor_data.sensor_id] = [sensor_data]  # if there is no value, we create one as an array
        self.last_data[sensor_data.sensor_id] = sensor_data # saves only the last data we get

    def get_data(self, sensor_id):
        return self._sensor_data.get(sensor_id)

    def reset_data(self):
        self._sensor_data = {}
        self.last_data = {}