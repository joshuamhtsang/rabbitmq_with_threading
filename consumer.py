import json
import threading
import time

import pika


def ack_message(channel, method, type):
    if channel.is_open:
        if type == 'ack':
            channel.basic_ack(method.delivery_tag)
        elif type == 'nack':
            channel.basic_nack(method.delivery_tag, requeue=False)
        else:
            print("Invalid acknowledgement type.")
    else:
        print("The channel is now closed and therefore cannot ack message on the same channel.")
        pass


def do_something(channel, method, body):
    try:
        print("The number is : ", body["number"])
        number = int(body["number"])
        for i in range(0, number):
            print(i)
            time.sleep(1)
        ack_message(channel, method, 'ack')
    except Exception as e:
        print(e)
        ack_message(channel, method, 'nack')
        raise e


def on_message(channel, method, properties, body):
    try:
        body = json.loads(body)
    except Exception as e:
        print(e)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        raise e

    thread = threading.Thread(target=do_something, args=[channel, method, body])
    thread.start()
    while thread.is_alive():  # Loop while the thread is processing
        print("Channel staying alive...")
        channel._connection.sleep(1.0)
    print('Back from thread')


def main():
    rabbit_credentials = pika.PlainCredentials('joshua', "guest")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='localhost',
            port=5672,
            credentials=rabbit_credentials,
            #socket_timeout=1200,
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
    except Exception as e:
        pass
    channel.close()


if __name__ == '__main__':
    while True:
        main()
        time.sleep(1)
