import argparse

from threading import Thread, Lock

from Task_Manager import Task_Consumer
from Monitoring_System import Logging_Publisher


def task_consumer(drone_name, lock):
    process = Task_Consumer(drone_name, lock)
    process.consume()
    
def logger(drone_name, lock):
    process = Logging_Publisher(drone_name, lock)
    process.Logging()
    
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--drone_name', help='drone_name argument')
    
    args, unknown = parser.parse_known_args()
    
    drone_name = args.drone_name
    
    lock = Lock()
    
    th1 = Thread(target=task_consumer, args=(drone_name, lock))
    th2 = Thread(target=logger, args=(drone_name, lock))
    
    th1.start()
    th2.start()
    
    th1.join()
    th2.join()
    
    print('end')