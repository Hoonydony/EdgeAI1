use rumqttc::{Client, MqttOptions, QoS};
use std::{thread, time::Duration};
use rand::Rng;
use rand_distr::{Normal, Distribution};
use chrono::Local;

fn main() {
    // MQTT 브로커 설정
    let mut mqttoptions = MqttOptions::new("rust-edgeai-publisher", "localhost", 1883);
    mqttoptions.set_keep_alive(Duration::from_secs(5));

    // 클라이언트와 connection 생성
    let (mut client, mut connection) = Client::new(mqttoptions, 10);

    // connection 이벤트 루프를 별도 스레드에서 실행 (중요!)
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
            // speed: 20.0 ~ 100.0 float
            let speed: f32 = rng.gen_range(20.0..100.0);

            // temperature = 30 + 0.05 * speed + 노이즈
            let temperature = 30.0 + 0.05 * speed + normal_temp.sample(&mut rng);

            // voltage = 360 + 0.3 * speed + 노이즈
            let voltage = 360.0 + 0.3 * speed + normal_volt.sample(&mut rng);

            // 타임스탬프
            let timestamp = Local::now().format("%Y-%m-%dT%H:%M:%S%z").to_string();

            // JSON 문자열
            let payload = format!(
                r#"{{"timestamp":"{}","ecu_id":{},"temperature":{:.2},"speed":{:.2},"voltage":{:.2}}}"#,
                timestamp, ecu_id, temperature, speed, voltage
            );

            // MQTT publish
            client
                .publish(format!("car/ecu/{}", ecu_id), QoS::AtLeastOnce, false, payload)
                .unwrap();

            println!("Published data for ECU {}.", ecu_id);
        }

        thread::sleep(Duration::from_secs(1));
    }
}
