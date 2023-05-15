import argparse

from threading import Thread
from dronekit import connect

from Task_Manager import Task_Consumer
from Monitoring_System import Logging_Publisher

# connection_string = '/dev/ttyACM0'
connection_string = 'udp:127.0.0.1:14540'

vehicle = connect(connection_string, wait_ready=True)

def task_consumer(vehicle, drone_name):
    connection_vehicle = vehicle
    process = Task_Consumer(connection_vehicle, drone_name)
    process.consume()
    
def logger(vehicle, drone_name):
    connection_vehicle = vehicle
    process = Logging_Publisher(connection_vehicle, drone_name)
    process.Logging()
    
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--drone_name', help='drone_name argument')
    
    args, unknown = parser.parse_known_args()
    
    drone_name = args.drone_name
    
    th1 = Thread(target=task_consumer, args=(vehicle, drone_name))
    th2 = Thread(target=logger, args=(vehicle, drone_name))
    
    th1.start()
    th2.start()
    
    th1.join()
    th2.join()
    
    print('end')