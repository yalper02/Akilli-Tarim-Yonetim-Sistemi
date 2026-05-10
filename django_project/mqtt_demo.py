import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883)

client.publish("tarim/nem", "Toprak Nemi: 45")

print("MQTT mesaj gönderildi")