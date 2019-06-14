# rabbitmq_with_threading
Proof of concept for using threading in RabbitMQ consumers

Build the RabbitMQ image

$ docker build --tag rabbitmq:try_threading .

$ docker run -d --hostname my-rabbit --name rabbitmq_threading_test -p 8080:15672 rabbitmq:try_threading

You can now login to the Management UI at: http://localhost:8080/
For login use 'joshua' and 'guest' (this can be changed if you desire in the UI).