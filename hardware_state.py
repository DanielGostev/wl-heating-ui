
class HardwareState:
    def __init__(self):
        self._subscribers = []
        self._fan_current_state = "n/a"
        self._fan_desired_state = "n/a"
        self._heater_current_state = "n/a"
        self._heater_desired_state = "n/a"

    def subscribe(self, subscriber):
        self._subscribers.append(subscriber)

    def change_state(self, fan_desired_state=None, heater_desired_state=None):
        if fan_desired_state is not None:
            self._fan_desired_state = fan_desired_state
        if heater_desired_state is not None:
            self._heater_desired_state = heater_desired_state
        for s in self._subscribers:
            s.hardware_state_changed(self)

    def get_state(self):
        return self._heater_current_state, self._heater_desired_state, self._fan_current_state, self._fan_desired_state

    def get_heater_current_state(self):
        return self._heater_current_state

    def get_heater_desired_state(self):
        return self._heater_desired_state

    def get_fan_current_state(self):
        return self._fan_current_state

    def get_fan_desired_state(self):
        return self._fan_desired_state
