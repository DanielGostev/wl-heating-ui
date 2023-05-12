import mqtt
import time
import sensor_data
import ui
import hardware_state as hs
import config


def main():
    sensor_logger = sensor_data.SensorLogger()
    hardware_state = hs.HardwareState()

    mqtt_control = mqtt.MqttControl(config.mqtt_address, config.mqtt_port, sensor_logger)
    mqtt_control.connect_broker()
    mqtt_control.subscribe(config.mqtt_topic)
    hardware_state.subscribe(mqtt_control)

    web_ui = ui.WebUI(sensor_logger, hardware_state)
    hardware_state.subscribe(web_ui)
    web_ui.run()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("exiting")
        mqtt_control.paho_client.disconnect()
        mqtt_control.paho_client.loop_stop()


if __name__ == "__main__":
    main()
