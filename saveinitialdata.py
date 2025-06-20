import json
import numpy as np

np.random.seed(42)

data = []
for _ in range(1000):
    # speed: 20 ~ 100 사이 난수
    speed = np.random.uniform(20, 100)

    # temperature: speed에 비례 + 약간 노이즈
    temperature = 30 + 0.05 * speed + np.random.normal(0, 1)

    # voltage: speed에 비례 (약간 노이즈 포함), 360~400 사이로 유지
    voltage = 360 + 0.3 * speed + np.random.normal(0, 2)

    # JSON 객체로 저장
    entry = {
        "speed": round(speed, 2),
        "temperature": round(temperature, 2),
        "voltage": round(voltage, 2)
    }
    data.append(entry)

# JSON 라인 단위로 파일 저장
with open('normal_data.json', 'w') as f:
    for d in data:
        f.write(json.dumps(d) + "\n")

print("normal_data.json 파일 생성 완료!")
