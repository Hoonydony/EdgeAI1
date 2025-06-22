import json
import numpy as np

np.random.seed(42)

data = []
for _ in range(1000):
    # speed: generate a random number between 20 and 100
    speed = np.random.uniform(20, 100)

    # temperature: proportional to speed with a small amount of noise
    temperature = 30 + 0.05 * speed + np.random.normal(0, 1)

    # voltage: proportional to speed (with some noise), kept roughly between 360 and 400
    voltage = 360 + 0.3 * speed + np.random.normal(0, 2)

    # store as a JSON object
    entry = {
        "speed": round(speed, 2),
        "temperature": round(temperature, 2),
        "voltage": round(voltage, 2)
    }
    data.append(entry)

# save to file in JSON Lines format
with open('normal_data.json', 'w') as f:
    for d in data:
        f.write(json.dumps(d) + "\n")

print("normal_data.json file has been created!")
