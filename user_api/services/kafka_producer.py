import json
import logging
from asyncio import get_running_loop
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from confluent_kafka import Producer, KafkaException
from fastapi import HTTPException


class KafkaProducerManager:
    def __init__(self, config: Dict[str, str]):
        """
        Инициализирует Kafka-продюсер.

        :param config: Конфигурация продюсера (словарь).
        """
        try:
            self.message_count = 0
            self.flush_interval = 100
            self.producer = Producer(config)
            logging.info(f"Kafka Producer инициализирован с конфигурацией: {config}")
        except KafkaException as e:
            logging.error(f"Ошибка при создании продюсера: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Ошибка инициализации Kafka Producer: {str(e)}"
            )

    def delivery_report(self, err, msg):
        """
        Callback для обработки результата доставки сообщения.
        """
        if err is not None:
            logging.error(f"Ошибка доставки сообщения: {err}")
        else:
            logging.debug(
                f"Сообщение успешно доставлено в {msg.topic()} [{msg.partition()}]"
            )

    async def send_message(self, topic: str, message: dict):
        """
        Отправляет сообщение в указанный топик Kafka.

        :param topic: Название топика.
        :param message: Сообщение в формате словаря.
        :raises HTTPException: Если произошла ошибка при отправке.
        """
        if not isinstance(topic, str):
            raise HTTPException(status_code=400, detail="Топик должен быть строкой")
        if not isinstance(message, dict):
            raise HTTPException(
                status_code=400, detail="Сообщение должно быть словарем"
            )

        try:
            message_str = json.dumps(message)
            encoded_message = message_str.encode("utf-8")
            loop = get_running_loop()
            with ThreadPoolExecutor() as pool:
                await loop.run_in_executor(
                    pool,
                    lambda: self.producer.produce(
                        topic, value=encoded_message, callback=self.delivery_report
                    ),
                )
            logging.info(f"Сообщение отправлено в топик {topic}: {message}")

            self.message_count += 1
            if self.message_count >= self.flush_interval:
                await self.flush()
                self.message_count = 0
        except UnicodeEncodeError as e:
            logging.error(f"Ошибка кодирования сообщения: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Ошибка кодирования данных: {str(e)}"
            )
        except KafkaException as e:
            logging.error(f"Ошибка при отправке в Kafka: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Ошибка при отправке данных в Kafka: {str(e)}"
            )
        except Exception as e:
            logging.error(f"Неизвестная ошибка: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Неизвестная ошибка: {str(e)}")

    def flush(self):
        """
        Принудительно отправляет все накопленные сообщения.
        """
        try:
            self.producer.flush()
            logging.info("Все сообщения принудительно отправлены")
        except KafkaException as e:
            logging.error(f"Ошибка при вызове flush: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Ошибка при flush: {str(e)}")

    def close(self):
        """
        Корректно завершает работу продюсера.
        """
        if self.producer:
            self.producer.flush()
            logging.info("Kafka Producer закрыт")
