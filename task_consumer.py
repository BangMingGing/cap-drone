import argparse
import pika
import pickle

from config import RABBITMQ_CONFIG

RABBITMQ_SERVER_IP = RABBITMQ_CONFIG.SERVER_IP
RABBITMQ_SERVER_PORT = RABBITMQ_CONFIG.SERVER_PORT


class Task_Consumer():
    
    def __init__(self, controller, drone_name):
        self.credentials = pika.PlainCredentials(RABBITMQ_CONFIG.USER, RABBITMQ_CONFIG.PASSWORD)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, RABBITMQ_CONFIG.HOST, self.credentials))
        self.channel = self.connection.channel()
        
        self.my_name = '[Task_Consumer]'
        
        self.drone_name = drone_name
        self.queue_name = drone_name
        self.exchange_name = 'input'

        # Queue 선언
        queue = self.channel.queue_declare(self.queue_name)
        # Queue-Exchange Binding
        self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=f'to{self.queue_name}')

        # Controller 인스턴스 생성
        self.controller = controller
        
    
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
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--drone_name', help='drone_name argument')
    
    args, unknown = parser.parse_known_args()
    
    drone_name = args.drone_name
    
    process = Task_Consumer(drone_name)
    process.consume()
