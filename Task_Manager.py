import pika
import pickle
import time

from Vehicle import Controller

RABBITMQ_SERVER_IP = '203.255.57.129'
RABBITMQ_SERVER_PORT = '5672'


class Task_Consumer():
    
    def __init__(self, drone_name):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()
        
        self.my_name = '[Task_Consumer]'
        
        self.queue_name = drone_name

        # Queue 선언
        queue = self.channel.queue_declare(self.queue_name)
        # Queue-Exchange Binding
        self.channel.queue_bind(exchange='cap', queue=self.queue_name, routing_key=f'to{self.queue_name}')

        # Controller 인스턴스 생성
        self.controller = Controller()
        
    
    def callback(self, ch, method, properties, body):
        message = pickle.loads(body, encoding='bytes')
        header = message['header']
        contents = message['contents']
        
        self.controller.control(header, contents)
        
        
        ch.basic_ack(delivery_tag=method.delivery_tag)


    def consume(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(on_message_callback=self.callback, queue=self.queue_name)
        print(f"{self.my_name} Start Consuming")
        self.channel.start_consuming()
        
        
if __name__ == '__main__':
    
    process = Task_Consumer()
    process.consume()
