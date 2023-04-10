import yaml
import os

with open("config.yaml", "r") as stream:
    try:
        config = yaml.safe_load(stream)
        print(config)
        mqtt_config = config["mqtt"]
        if mqtt_config is None or mqtt_config == "":
            mqtt_address = "127.0.0.1"
            mqtt_port = "1883"
            mqtt_topic = "temp/pico"
        else:
            mqtt_address = mqtt_config["address"]
            mqtt_port = mqtt_config["port"]
            mqtt_topic = mqtt_config["topic"]
        data_dir = config["dataDir"]
        if data_dir is None or data_dir == "":
            data_dir = "./data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        sensor_ids = config["sensors"]
        if sensor_ids is None or sensor_ids == "":
            sensor_ids = ["pico_ft", "pico_fb", "pico_bt", "pico_bb"]
        web_ui = config["webUI"]
        if web_ui is None or web_ui == "":
            web_ui = {"host": "0.0.0.0", "port": 8080}
    except yaml.YAMLError as exc:
        print(exc)