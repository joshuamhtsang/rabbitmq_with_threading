import json
import threading
import time

import pika


def do_something(channel, method, body):
    try:
        number = int(body["number"])
        for i in range(0, number):
            print(i)
            time.sleep(1)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(e)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        raise e


def on_message(channel, method, properties, body):
    body = json.loads(body)
    print("The number is : ", body["number"])

    thread = threading.Thread(target=do_something, args=[channel, method, body])
    thread.start()
    while thread.is_alive():  # Loop while the thread is processing
        channel._connection.sleep(10.0)
    print('Back from thread')


def main():
    rabbit_credentials = pika.PlainCredentials('joshua', "guest")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='localhost',
            port=5672,
            credentials=rabbit_credentials,
            socket_timeout=1200,
            heartbeat=10
        )
    )
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_message, 'eric.request')
    try:
        print("Consuming...")
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Consumer stopping...!")
        channel.stop_consuming()
    channel.close()


if __name__ == '__main__':
    while True:
        main()
        time.sleep(1)
