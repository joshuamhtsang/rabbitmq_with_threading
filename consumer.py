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
        channel.basic_ack(delivery_tag=method.delivery_tag)
        raise e


def on_message(channel, method, properties, body):
    body = json.loads(body)
    print(body["number"])

    thread = threading.Thread(target=do_something, args=[channel, method, body])
    thread.start()
    while thread.is_alive():  # Loop while the thread is processing
        channel._connection.sleep(1.0)
    print('Back from thread')
    #channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    rabbit_credentials = pika.PlainCredentials('joshua', "guest")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='localhost',
            port=5672,
            credentials=rabbit_credentials,
            socket_timeout=1200,
            heartbeat=60)
    )
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_message, 'eric.request')
    try:
        print("Consuming...")
        channel.start_consuming()
        print("... Yummy!")
    except KeyboardInterrupt:
        channel.stop_consuming()
    channel.close()


if __name__ == '__main__':
    main()
