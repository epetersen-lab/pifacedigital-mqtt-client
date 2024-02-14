# PiFace Digital MQTT Client

This client connects to an MQTT broker service and subscribes and publishes  
to specific topics. The IO pin's can be monitored and controlled by  
subscribing/publishing to those topics. A topic for each pin of the PiFace Digital  
is subscribed and current status is published.

## Installation
```sh
make dist
sudo pip3 install -U dist/pifacedigital_mqtt_client-<version>-py3-none-any.whl
```
#### Install and enable as systemd service
```sh
sudo make systemd-install
```
#### Remove the systemd service
```sh
sudo make systemd-remove
```

### Configuration

Config options are located in `etc/pifacedigital-mqtt-client/config.ini`.

```
; config.ini

HOST: mqtt.example.com
PORT: 1883
USERNAME: mqttuser
PASSWORD: mqttpassword
BASE_TOPIC: pifacedigital_1
```

## Home Assistant integration
The project can integrate to Home Assistant, so it is possible to use the  
state information and control the outputs in your automations.  
The MQTT integration has to added and configured.  
Also user as specified in the `config.ini` has to be created within HA. 

#### Integrate input pin's
The state of input pin's can be monitored by Home Assistant via the  
MQTT binary sensor. The example below will make Home Assistant subscribe to the  
topics of input pin0 and pin1.

```
# configuration.yaml

mqtt:
   binary_sensor:
     - unique_id: pifacedigital_input_0
       name: "PiFaceDigital Input 0"
       state_topic: "pifacedigital_1/input/0"

     - unique_id: pifacedigital_input_1
       name: "PiFaceDigital Input 1"
       state_topic: "pifacedigital_1/input/1"

```

#### Integrate output pin's
The state of output pin's can be controlled and monitored by Home Assistant  
via the MQTT Switch integration.  
This example below shows how to add output pin0 and pin1. 

```
# configuration.yaml

mqtt:
   switch:
     - unique_id: pifacedigital_output_0
       name: "PiFaceDigital Output 0"
       device_class: switch
       state_topic: "pifacedigital_1/output/0"
       command_topic: "pifacedigital_1/output/0/set"
       retain: true

     - unique_id: pifacedigital_output_1
       name: "PiFaceDigital Output 1"
       device_class: switch
       state_topic: "pifacedigital_1/output/1"
       command_topic: "pifacedigital_1/output/1/set"
       retain: true

```

#### References
- [PiFace Digital I/O's documentation](https://pifacedigitalio.readthedocs.io/)
- [Eclipse paho-mqtt-client](https://eclipse.dev/paho/files/paho.mqtt.python/html/index.html#)
- [Home Assistant](https://www.home-assistant.io)