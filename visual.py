import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import json

# MQTT broker settings
BROKER = "localhost"
RAW_TOPIC = "car/ecu/#"
ANOMALY_TOPIC = "vehicle/anomaly"

MAX_LEN = 200  # Keep up to the last 200 data points

speeds = deque(maxlen=MAX_LEN)
temperatures = deque(maxlen=MAX_LEN)
voltages = deque(maxlen=MAX_LEN)
anomalies = deque(maxlen=MAX_LEN)
ecu_ids = deque(maxlen=MAX_LEN)
timestamps = deque(maxlen=MAX_LEN)
scores = deque(maxlen=MAX_LEN)  # ✅ Store anomaly score

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(RAW_TOPIC)
    client.subscribe(ANOMALY_TOPIC)
    print(f"Subscribed to {RAW_TOPIC} and {ANOMALY_TOPIC}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        if msg.topic.startswith("car/ecu/"):
            speeds.append(payload.get('speed', 0))
            temperatures.append(payload.get('temperature', 0))
            voltages.append(payload.get('voltage', 0))
            anomalies.append(False)  # Mark as normal for raw data
            ecu_ids.append(payload.get('ecu_id', 'unknown'))
            timestamps.append(payload.get('timestamp', 'unknown'))
            scores.append(0.0)  # Raw data has score 0

        elif msg.topic == ANOMALY_TOPIC:
            if len(anomalies) > 0:
                anomalies[-1] = True
                scores[-1] = payload.get('score', 0.0)
            print(f"Anomaly detected: {payload}")

    except Exception as e:
        print(f"Error parsing message: {e}")

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883)
client.loop_start()

# Matplotlib setup: 1 row, 2 columns
fig, axs = plt.subplots(1, 2, figsize=(12, 6))

def animate(i):
    if len(speeds) == 0:
        return

    axs[0].clear()
    axs[1].clear()

    # Speed vs Temperature scatter plot
    normal_speeds = [s for s, a in zip(speeds, anomalies) if not a]
    normal_temps = [t for t, a in zip(temperatures, anomalies) if not a]
    anomaly_speeds = [s for s, a in zip(speeds, anomalies) if a]
    anomaly_temps = [t for t, a in zip(temperatures, anomalies) if a]

    axs[0].scatter(normal_speeds, normal_temps, c='blue', label='Normal')
    axs[0].scatter(anomaly_speeds, anomaly_temps, c='red', label='Anomaly')

    # Annotate anomaly points with ECU ID, timestamp, and score(under 0)
    for idx, (s, t, a) in enumerate(zip(speeds, temperatures, anomalies)):
        if a:
            label = f"ECU:{ecu_ids[idx]}\n{timestamps[idx]}\nScore:{scores[idx]:.3f}"
            axs[0].annotate(label, (s, t), textcoords="offset points", xytext=(5,5), ha='left', fontsize=7, color='red')

    axs[0].set_xlabel('Speed')
    axs[0].set_ylabel('Temperature (°C)')
    axs[0].set_title('Speed vs Temperature')
    axs[0].legend(loc='lower right')
    axs[0].grid(True)

    # Speed vs Voltage scatter plot
    normal_volts = [v for v, a in zip(voltages, anomalies) if not a]
    anomaly_volts = [v for v, a in zip(voltages, anomalies) if a]

    axs[1].scatter(normal_speeds, normal_volts, c='blue', label='Normal')
    axs[1].scatter(anomaly_speeds, anomaly_volts, c='red', label='Anomaly')

    # Annotate anomaly points with ECU ID, timestamp, and score
    for idx, (s, v, a) in enumerate(zip(speeds, voltages, anomalies)):
        if a:
            label = f"ECU:{ecu_ids[idx]}\n{timestamps[idx]}\nScore:{scores[idx]:.3f}"
            axs[1].annotate(label, (s, v), textcoords="offset points", xytext=(5,5), ha='left', fontsize=7, color='red')

    axs[1].set_xlabel('Speed')
    axs[1].set_ylabel('Voltage (V)')
    axs[1].set_title('Speed vs Voltage')
    axs[1].legend(loc='lower right')
    axs[1].grid(True)

    plt.tight_layout()

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
