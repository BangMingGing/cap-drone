import asyncio
import aio_pika
import time
import pickle

from mavsdk import System

from task_publisher import Publisher
from controller import Controller
from config import VEHICLE_CONFIG, RABBITMQ_CONFIG

async def task_consume(connection, controller):
    drone_name = VEHICLE_CONFIG.DRONE_NAME

    channel = await connection.channel()
    exchange = aio_pika.Exchange(channel, RABBITMQ_CONFIG.TASK_EXCHANGE, type=aio_pika.ExchangeType.DIRECT)
    await exchange.declare()
    queue = await channel.declare_queue(drone_name)
    await queue.bind(exchange, f"to{queue}")

    semaphore = asyncio.Semaphore(value=1)

    async def consume_with_semaphore():
        async with semaphore:
            async for message in queue:
                async with message.process():
                    message_data = pickle.loads(message.body, encoding='bytes')
                    print(f"Received message: {message_data}")
                    
                    header = message_data['header']
                    contents = message_data['contents']

                    if header == 'takeoff':
                        print('Takeoff Called')
                        takeoff_alt = contents['takeoff_alt']
                        await controller.takeoff(takeoff_alt)

                    elif header == 'upload_mission':
                        print('Upload Mission Called')
                        mission = contents['mission']
                        direction = contents['direction']
                        await controller.upload_mission(mission, direction)

                    elif header == 'start_mission':
                        print('Start Mission Called')
                        await controller.start_mission()

                    elif header == 'pause_mission':
                        print('Pause Mission Called')
                        await controller.pause_mission()

                    elif header == 'land':
                        print('Land Called')
                        await controller.land()

                    elif header == 'upload_receiver':
                        print('Upload Receiver Called')
                        receiver = contents['receiver']
                        await controller.set_receiver(receiver)

                    elif header == 'face_recog_start':
                        print('Face Recog StartCalled')
                        await controller.temp_face_recog_start()
                        # await controller.face_recog_start()
                        

                    print("message finished")
                        


    print("Task Consumer started", VEHICLE_CONFIG.SYSTEM_ADDRESS)

    while True:
        await consume_with_semaphore()


async def log_publish(connection, controller):
    drone_name = VEHICLE_CONFIG.DRONE_NAME

    channel = await connection.channel()
    exchange = aio_pika.Exchange(channel, RABBITMQ_CONFIG.LOG_EXCHANGE, type=aio_pika.ExchangeType.DIRECT)
    await exchange.declare()
    
    print("Log Publisher started")
    while True:
        message = {
            'create_at': time.time(), 
            'drone_name': drone_name, 
            'GPS_info': controller.GPS,
            'mission_status': controller.mission_status,
            'current_mission': controller.current_mission,
            'total_mission': controller.total_mission
        }

        await exchange.publish(aio_pika.Message(body=pickle.dumps(message)), routing_key=f"to{RABBITMQ_CONFIG.LOG_QUEUE}")
        await asyncio.sleep(1)

async def set_gps(controller):
    while True:
        await controller.set_GPS()
        await asyncio.sleep(1)


async def set_mission_progress(controller):
    while True:
        await controller.set_mission_progress()

async def px4_connect_drone():
    drone = System()
    await drone.connect(system_address=VEHICLE_CONFIG.SYSTEM_ADDRESS)
    
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            return drone
        
async def rabbitmq_connect():
    connection = await aio_pika.connect_robust(
        host=RABBITMQ_CONFIG.SERVER_IP,
        port=RABBITMQ_CONFIG.SERVER_PORT,
        login=RABBITMQ_CONFIG.USER,
        password=RABBITMQ_CONFIG.PASSWORD,
        virtualhost=RABBITMQ_CONFIG.HOST,
    )
    print(" -- Connected to Rabbitmq")
    return connection


async def main():
    loop = asyncio.get_event_loop()

    connection = await rabbitmq_connect()

    publisher = Publisher(connection, RABBITMQ_CONFIG.TASK_EXCHANGE, VEHICLE_CONFIG.DRONE_NAME, RABBITMQ_CONFIG.TASK_QUEUE)
    await publisher.initialize()

    drone = await px4_connect_drone()
    controller = Controller(drone, publisher)

    consumer_task = loop.create_task(task_consume(connection, controller))
    publisher_task = loop.create_task(log_publish(connection, controller))
    set_gps_task = loop.create_task(set_gps(controller))
    set_mission_progress_task = loop.create_task(set_mission_progress(controller))

    try:
        await asyncio.gather(
            consumer_task, 
            publisher_task, 
            set_gps_task, 
            set_mission_progress_task
        )
    except KeyboardInterrupt:
        pass
    finally:
        channel = await connection.channel()
        queue = await channel.declare_queue(VEHICLE_CONFIG.DRONE_NAME)
        await queue.unbind(RABBITMQ_CONFIG.TASK_EXCHANGE, f"to{VEHICLE_CONFIG.DRONE_NAME}")
        await queue.delete()
        print("Queue Deleted")
        await connection.close()
        print("Connection closed")

if __name__ == "__main__":
    asyncio.run(main())
