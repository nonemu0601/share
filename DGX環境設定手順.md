## Kafka設定変更手順
以下の手順に従って外部向けIPアドレスの設定変更をお願いいたします。

- 外部からのアクセス許可設定変更
  - 外部向けIPアドレスの設定が `192.168.0.84` になっているため、環境に合わせて `192.168.0.84` から変更をお願いいたします。
```shell
$ sudo vi /usr/local/src/kafka_2.13-3.9.1/config/server.properties 
```
```shell
listeners=PLAINTEXT://192.168.0.84:9092
```

- kafka サーバ再起動
```shell
$ sudo systemctl restart zookeeper.service
$ sudo systemctl restart kafka.service
```

- トピック作成
  - `192.168.0.84` は環境に合わせて変更をお願いいたします。
```shell
$ sudo /usr/local/src/kafka_2.13-3.9.1/bin/kafka-topics.sh --create --bootstrap-server 192.168.0.84:9092 --replication-factor 1 --partitions 10 --topic inc-collaboration-event
```
```shell
Created topic inc-collaboration-event.
```
- ※トピックが存在している場合は以下のように表示されますが、問題ありません。
```shell
Error while executing topic command : Topic 'inc-collaboration-event' already exists.
[2026-01-27 08:49:37,895] ERROR org.apache.kafka.common.errors.TopicExistsException: Topic 'inc-collaboration-event' already exists.
 (org.apache.kafka.tools.TopicCommand)
```

- メッセージ送受信確認
  - `192.168.0.84` は環境に合わせて変更をお願いいたします。
```shell
$ /usr/local/src/kafka_2.13-3.9.1/bin/kafka-console-producer.sh --broker-list 192.168.0.84:9092 --topic inc-collaboration-event
>{"id": "1a2b3c4d-5e6f-7g8h-9i1j-2a3b4c5d6e7f", "source": "192.168.0.84", "specversion": "1.0", "type": "inc.collaboration.v1", "datacontenttype": "application/json", "subject": "INC Notification", "time": "2025-09-01T10:15:23Z", "data": {"sample": "sample"}}
```
```shell
$ /usr/local/src/kafka_2.13-3.9.1/bin/kafka-console-consumer.sh --bootstrap-server 192.168.0.84:9092 --topic inc-collaboration-event --from-beginning
{"id": "1a2b3c4d-5e6f-7g8h-9i1j-2a3b4c5d6e7f", "source": "192.168.0.84", "specversion": "1.0", "type": "inc.collaboration.v1", "datacontenttype": "application/json", "subject": "INC Notification", "time": "2025-09-01T10:15:23Z", "data": {"sample": "sample"}}
```

## スクリプト配置手順
手順は INC連携環境構築.xlsx のシート[INC連携環境構築]26行目以降をご参照ください。
`inc_subscriver.py` のIPアドレスとポート部分は環境に合わせて変更をお願いいたします。