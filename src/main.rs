use rumqttc::{Client, MqttOptions, QoS};
use std::{thread, time::Duration};
use rand::Rng;
use rand_distr::{Normal, Distribution};
use chrono::Local;

fn main() {
    // MQTT broker settings
    let mut mqttoptions = MqttOptions::new("rust-edgeai-publisher", "localhost", 1883);
    mqttoptions.set_keep_alive(Duration::from_secs(5));

    // Create client and connection
    let (mut client, mut connection) = Client::new(mqttoptions, 10);

    // Run the connection event loop in a separate thread
    thread::spawn(move || {
        for event in connection.iter() {
            println!("MQTT Event: {:?}", event);
        }
    });

    let mut rng = rand::thread_rng();
    let normal_temp = Normal::new(0.0, 1.0).unwrap();
    let normal_volt = Normal::new(0.0, 2.0).unwrap();

    loop {
        for ecu_id in 1..=2 {
            // speed: random float between 20.0 and 100.0
            let speed: f32 = rng.gen_range(20.0..100.0);

            // temperature = 30 + 0.05 * speed + small noise
            let temperature = 30.0 + 0.05 * speed + normal_temp.sample(&mut rng);

            // voltage = 360 + 0.3 * speed + larger noise
            let voltage = 360.0 + 0.3 * speed + normal_volt.sample(&mut rng);

            // generate timestamp
            let timestamp = Local::now().format("%Y-%m-%dT%H:%M:%S%z").to_string();

            // build JSON payload
            let payload = format!(
                r#"{{"timestamp":"{}","ecu_id":{},"temperature":{:.2},"speed":{:.2},"voltage":{:.2}}}"#,
                timestamp, ecu_id, temperature, speed, voltage
            );

            // publish to MQTT topic
            client
                .publish(format!("car/ecu/{}", ecu_id), QoS::AtLeastOnce, false, payload)
                .unwrap();

            println!("Published data for ECU {}.", ecu_id);
        }

        thread::sleep(Duration::from_secs(1));
    }
}