import json
import numpy as np
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
import paho.mqtt.client as mqtt

# -------------------------
# 1) 정상 데이터 로드 + 전처리
# -------------------------

with open("normal_data.json") as f:
    lines = f.readlines()
    normal_data = [json.loads(line) for line in lines]

X_train = np.array([
    [d['speed'], d['temperature'], d['voltage']]
    for d in normal_data
])

print(f"✅ 정상 데이터 shape: {X_train.shape}")

# -------------------------
# 2) PCA 2차원 축소 + IsolationForest 학습
# -------------------------

pca = PCA(n_components=2, random_state=42)
X_train_pca = pca.fit_transform(X_train)

iso_forest = IsolationForest(
    contamination=0.01,  # 예상 이상치 비율
    random_state=42
)
iso_forest.fit(X_train_pca)

print(f"✅ PCA + IsolationForest 학습 완료")

# -------------------------
# 3) MQTT 설정
# -------------------------

BROKER = "localhost"
RAW_TOPIC = "car/ecu/#"
ANOMALY_TOPIC = "vehicle/anomaly"

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"✅ Connected: {rc}")
    client.subscribe(RAW_TOPIC)
    print(f"✅ Subscribed to {RAW_TOPIC}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"📥 Received: {payload}")

        # 수신 데이터 PCA 변환
        X_new = np.array([[payload['speed'], payload['temperature'], payload['voltage']]])
        X_new_pca = pca.transform(X_new)

        # IsolationForest 예측 & score
        score = iso_forest.decision_function(X_new_pca)[0]
        is_anomaly = iso_forest.predict(X_new_pca)[0] == -1

        # 이상치이면 anomaly topic 발행
        if is_anomaly:
            payload['anomaly'] = True
            payload['score'] = score
            client.publish(ANOMALY_TOPIC, json.dumps(payload))
            print(f"🚨 Anomaly published: {payload}")

    except Exception as e:
        print(f"❌ Error: {e}")

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883)
client.loop_forever()
