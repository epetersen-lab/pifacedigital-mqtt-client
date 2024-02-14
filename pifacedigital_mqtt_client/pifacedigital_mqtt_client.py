import configparser
import errno
import re
import signal
import sys
import os
import paho.mqtt.client as mqtt
import pifacedigitalio


MQTT_BASE_TOPIC = None
pifacedigital = pifacedigitalio.PiFaceDigital()
listener = None


def on_connect(client, userdata, flags, reason_code, properties):
    global listener

    def publish_input_state_on(interrupt):
        client.publish(topic=f"{MQTT_BASE_TOPIC}/input/{interrupt.pin_num}", payload="ON", retain=True)

    def publish_input_state_off(interrupt):
        client.publish(topic=f"{MQTT_BASE_TOPIC}/input/{interrupt.pin_num}", payload="OFF", retain=True)

    listener = pifacedigitalio.InputEventListener(chip=pifacedigital)
    for pin in range(0, 8):
        client.subscribe(f"{MQTT_BASE_TOPIC}/output/{pin}/set")

        if pifacedigital.input_pins[pin].value == 0:
            client.publish(topic=f"{MQTT_BASE_TOPIC}/input/{pin}", payload="OFF", retain=True)
        else:
            client.publish(topic=f"{MQTT_BASE_TOPIC}/input/{pin}", payload="ON", retain=True)

        listener.register(pin, pifacedigitalio.IODIR_FALLING_EDGE, publish_input_state_on)
        listener.register(pin, pifacedigitalio.IODIR_RISING_EDGE, publish_input_state_off)

    listener.activate()


def on_message(client, userdata, msg):
    result = re.search(MQTT_BASE_TOPIC + r"/output/([0-7]{1})/set", msg.topic)
    if result:
        pin = int(result.group(1))
        payload = msg.payload.decode()
        if payload == "ON":
            pifacedigital.output_pins[pin].turn_on()
            client.publish(topic=f"{MQTT_BASE_TOPIC}/output/{pin}", payload="ON", retain=True)
        if payload == "OFF":
            pifacedigital.output_pins[pin].turn_off()
            client.publish(topic=f"{MQTT_BASE_TOPIC}/output/{pin}", payload="OFF", retain=True)


def read_config(path):
    if os.path.exists(path):
        config = configparser.ConfigParser()
        config.read_file(open(path))
        return config
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)


def main():
    global MQTT_BASE_TOPIC
    config = read_config("/etc/pifacedigital-mqtt-client/config.ini")

    if config["MQTT"]["BASE_TOPIC"]:
        MQTT_BASE_TOPIC = config["MQTT"]["BASE_TOPIC"]

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def signal_handler(*_):
        listener.deactivate()
        client.disconnect()
        client.loop_stop()
        sys.exit()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    client.username_pw_set(config["MQTT"]["USERNAME"], password=config["MQTT"]["PASSWORD"])
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config["MQTT"]["HOST"], int(config["MQTT"]["PORT"]), keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
