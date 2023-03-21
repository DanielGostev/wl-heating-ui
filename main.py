import mqtt
import time
import sensor_data
import ui


def main():
    sensor_logger = sensor_data.SensorLogger()
#    mqtt_control = mqtt.MqttControl("192.168.45.19", 1883, sensor_logger)
#    mqtt_control = mqtt.MqttControl("192.168.178.35", 1883, sensor_logger)
    mqtt_control = mqtt.MqttControl("192.168.0.216", 1883, sensor_logger) # Pazardzhik
    mqtt_control.connect_broker()
    mqtt_control.subscribe("temp/pico")

    web_ui = ui.WebUI(sensor_logger)
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