## AI Anomaly Detection of EV Battery Real-Time Data 
A lightweight edge AI demo that collects real-time vehicle ECU data(a sample EV battery), detects anomalies using PCA-based Isolation Forest, and visualizes the results via MQTT

## Requirements

- Python 3.7 or higher
- MQTT broker (e.g., Mosquitto) running locally
- Python packages:
  - numpy
  - scikit-learn
  - paho-mqtt
  - matplotlib (for visualization)

## Setup

1. Install Python dependencies:

   pip3 install numpy scikit-learn paho-mqtt matplotlib

2. Run a local MQTT broker. For example, to start Mosquitto:

   mosquitto

3. Start the Rust data publisher **main.rs** to simulate real-time ECU sensor data and publish it via MQTT (main.rs):

   cargo run

4. Run the anomaly detection service in another terminal, **app.py** subscribes to MQTT topics, applies PCA and IsolationForest models for anomaly detection, and publishes anomaly alerts:

   python3 app.py

5. Run the visualization client in another terminal again, **visual.py** visualizes real-time sensor data and highlights detected anomalies with ECU ID, timestamp, and the score. The anomaly score points display a score that indicates how far each data point deviates from the learned normal data distribution, with lower scores representing stronger anomalies:

   python3 visual.py

<img width="1312" alt="image" src="https://github.com/user-attachments/assets/2de72e3a-6455-4cec-aaf6-ace08ebebe50" />


 
This AI model for anomaly detection is based on an unsupervised learning approach. 
First, we generate "normal" operational data using the script saveinitialdata.py, which simulates typical 3 kinds of vehicle sensor readings such as speed, temperature, and voltage. This normal dataset acts as the foundation for training the anomaly detection model.

The training process consists of two main steps:

1. Dimensionality Reduction with PCA (Principal Component Analysis):
Since the original data has three features (speed, temperature, voltage), we reduce it to two principal components using PCA. This step helps to capture the most significant variance in the data while simplifying the model’s input space.

2. Anomaly Detection with Isolation Forest:
We then train an Isolation Forest model on the PCA-transformed normal data. Isolation Forest is an unsupervised algorithm that isolates anomalies by randomly partitioning the data space using binary trees. Data points that are easier to isolate (i.e., require fewer splits) are considered more anomalous.

During real-time operation, new sensor data is transformed through the same PCA pipeline and then passed to the Isolation Forest for anomaly scoring. If the anomaly score exceeds a threshold (based on a contamination rate set during training), the data point is flagged as anomalous.


Regarding the temperature feature learning issue:
In our data, the relationship **between speed and voltage(RIGHT side)** shows a strong, almost linear correlation with relatively low noise, which makes it easier for the model to learn a consistent pattern and distinguish outliers effectively. However, the **speed-to-temperature(LEFT side)** relationship is noisier and more spread out around the expected correlation line. The temperature variable has a much narrower natural range than voltage, so even small random noise causes data points to appear further from the main cluster relative to their scale. Additionally, PCA reduces dimensionality by emphasizing directions of highest variance (dominated by voltage), which distorts the temperature information when projected to 2D. These factors together make the speed–temperature correlation more sensitive to noise and PCA artifacts, causing IsolationForest to misclassify normal points near the cluster center as anomalies.
