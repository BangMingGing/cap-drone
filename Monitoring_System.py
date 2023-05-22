import pika
import pickle
import time

from Vehicle import Logger

RABBITMQ_SERVER_IP = '203.255.57.129'
RABBITMQ_SERVER_PORT = '5672'


class Logging_Publisher():
    
    def __init__(self, drone_name):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()
        self.my_name = '[Logging Publisher]'
        
        self.drone_name = drone_name
        
        # Exchange 선언
        self.channel.exchange_declare(exchange='monitoring', exchange_type='direct')

        # Logger 인스턴스 생성
        self.logger = Logger()
        
        self.term = 5


    
    def publish(self, message, exchange_name, routing_key_name):
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key_name,
            body=pickle.dumps(message)
        )
        return True
    
    
    def Logging(self):
        """print(f"{self.my_name} Start Logging")
        while True:
            GPS_info = self.logger.get_status()
            CAM_info = 'cam' # get CAM image
            create_time = time.time()
            message = {'create_at': create_time, 'drone_name': self.drone_name, GPS_info': GPS_info, 'CAM_info': CAM_info}
            self.publish(message, 'monitoring', 'tocapdb')
            print(f'{self.my_name} Published')
            time.sleep(self.term)"""




if __name__ == '__main__':
    
    process = Logging_Publisher()
    process.Logging()

    
