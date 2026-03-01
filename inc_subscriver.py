#!/usr/bin/python3
# coding: utf-8
import os
import sys
import json
from kafka import  KafkaConsumer
from logging import Formatter, StreamHandler, getLogger, DEBUG, INFO, WARNING, ERROR
import urllib.request

# Kafka bootstrap
KAFKA_BOOTSTRAP = "192.168.0.48:9092"
# Consumer Group
#CONSUMER_GROUP = "inc"
# Kafka Topic
KAFKA_TOPIC_CONSUMER = "inc-collaboration-event"
# controll server URL
LLM_SV_URL = "http://192.168.0.22:5000"
ADD_URL = "/model/new"
DEL_URL = "/model/delete"
REQUEST_HEADER = {"Authorization": "Bearer sk-admin-123456", "Content-Type": "application/json"}
ADD_PARAM = {
    "model_name": "hayashi",
    "litellm_params": {
        "model": "openai/smolvlm",
        "api_base": "http://192.168.0.122:5000/v1",
        "api_key": "sk-local-dummy"
    }
}
DEL_PARAM = { "id": "" }
M_ID_REQ_PARAM = {
    "url": "http://192.168.0.22:5000/model/info",
    "header": {"Authorization": "Bearer sk-admin-123456"}
}

# logger
logger = getLogger(__name__)
handler = StreamHandler()
logger.addHandler(handler)
logger.setLevel(DEBUG)
fmt = Formatter("%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(levelname)s]: %(message)s")
handler.setFormatter(fmt)

def getEventMessage(message):
    getMessage = None
    try:
        getMessage = json.loads(message.value)
        logger.debug(f"event message : {getMessage}")
    except Exception as e:
        logger.error(f"Failed to get event message : {e}")
    return getMessage

def createAddParam():
    add_url = LLM_SV_URL + ADD_URL
    add_param = ADD_PARAM
    return add_url, add_param

def createDelParam(model_id):
    del_url = LLM_SV_URL + DEL_URL
    del_param = DEL_PARAM
    del_param["id"] = model_id
    return del_url, del_param

def getModelId():
    req = urllib.request.Request(M_ID_REQ_PARAM["url"], headers=M_ID_REQ_PARAM["header"])
    with urllib.request.urlopen(req) as res:
        body = res.read()
        status = res.getcode()
        logger.info(f"GET model_id respose. status: {status}, body: {body}")
        body_json = json.loads(body.decode('utf-8'))
        if "data" not in body_json:
            logger.warning("KeyError - 'data' is not found in Response body")
            return None
        elif len(body_json["data"]) == 0:
            logger.warning("Warning - 'Response body[\"data\"] is empty")
            return None
        elif "model_info" not in body_json["data"][0]:
            logger.warning("KeyError - 'model_info' is not found in Response body[\"data\"][0] ")
            return None
        elif "id" not in body_json["data"][0]["model_info"]:
            logger.warning("KeyError - 'id' is not found in Response body[\"data\"][0][\"model_info\"] ")
            return None
        model_id = body_json["data"][0]["model_info"]["id"]
    return model_id

def requestModify(url, ctl_param):
    data = ctl_param
    headers = REQUEST_HEADER

    logger.info(f"POST request \n url: {url} \n data: {data}")

    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req) as res:
        body = res.read()
        status = res.getcode()
        logger.info(f"POST respose status: {status}, \n body: {body}")

def EventMessageListener():
    consumer = None
    try:
        consumer = KafkaConsumer(
           bootstrap_servers=KAFKA_BOOTSTRAP,
           #group_id=CONSUMER_GROUP,
           value_deserializer= lambda m: m.decode("utf-8")
        )
        consumer.subscribe([KAFKA_TOPIC_CONSUMER])
    except Exception as e:
        return logger.error(f"define consumer error : {e}")

    logger.info("KafkaConsumer is ready. Listening to Kafka topic.")

    for message in consumer:
        try:
            # kafka topic からメッセージを取得
            logger.info("Get event message")
            message_value = getEventMessage(message)

            if message_value is None:
                continue
            elif "data" not in message_value:
                logger.warning("KeyError - 'data' is not found in jsondata")
                continue
            elif "routing" not in message_value["data"]:
                logger.warning("KeyError - 'routing' is not found in messege[\"data\"] ")
                continue

            # 追加/削除を判定
            if message_value["data"]["routing"] == "on":
                # 追加用パラメータを作成
                url, ctl_param = createAddParam()
            elif message_value["data"]["routing"] == "off":
                model_id = getModelId()
                if model_id is None:
                  continue
                # 削除用パラメータを作成
                url, ctl_param = createDelParam(model_id)
            else:
                logger.warning(f"ValueError - 'routing' can accept on/off. but value is {message_value['data']['routing']}")
                continue

            #HTTPリクエスト作成
            requestModify(url, ctl_param)

        except Exception as e:
            logger.warning(f"unexpected error in EventMessageListener : {e}")
        finally:
            pass

def main():
    logger.info(f"start In-Network-Computing collaboration")
    logger.info(f"Kafka Topic Name for consumer : {KAFKA_TOPIC_CONSUMER}")

    try:
        # kafka topic監視常時起動
        EventMessageListener()
    except KeyboardInterrupt:
        logger.info(f"KeyboardInterrupt")
        pass

    logger.info(f"stop In-Network-Computing collaboration")

if __name__ == "__main__":
    main()