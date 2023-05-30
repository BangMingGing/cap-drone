import argparse
import pika
import pickle
import time
import asyncio

from Vehicle import Logger

RABBITMQ_SERVER_IP = '203.255.57.129'
RABBITMQ_SERVER_PORT = '5672'


class Logging_Publisher():
    
    def __init__(self, drone_name, lock):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()
        self.my_name = '[Logging Publisher]'
        
        self.drone_name = drone_name
        
        # Exchange 선언
        self.channel.exchange_declare(exchange='monitoring', exchange_type='direct')

        # Logger 인스턴스 생성
        self.logger = Logger(drone_name, lock)
        
        self.term = 1


    
    def publish(self, message, exchange_name, routing_key_name):
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key_name,
            body=pickle.dumps(message)
        )
        return True
    
    
    def Logging(self):
        print(f"{self.my_name} Start Logging")
        while True:
            try:
                GPS_info = asyncio.run(self.logger.get_status())
                create_time = time.time()
                message = {'create_at': create_time, 'drone_name': self.drone_name, 'GPS_info': GPS_info}
                self.publish(message, 'monitoring', 'tolog_queue')
                print(f'{self.my_name} Published')
            except:
                pass
            time.sleep(self.term)




if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--drone_name', help='drone_name argument')
    
    args, unknown = parser.parse_known_args()
    
    drone_name = args.drone_name
    
    
    process = Logging_Publisher(drone_name)
    process.Logging()

    
