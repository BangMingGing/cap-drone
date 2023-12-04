import aio_pika
import asyncio
import pickle

from config import RABBITMQ_CONFIG, VEHICLE_CONFIG


async def task_publish(connection):
    channel = await connection.channel()
    exchange = aio_pika.Exchange(channel, "task", type=aio_pika.ExchangeType.DIRECT)
    await exchange.declare()

    way_points = [
        (47.398039859999997, 8.5455725400000002, 10),   
        (47.398036222362471, 8.5450146439425509, 10),
        (47.397825620791885, 8.5450092830163271, 10)
    ]

    message = {
            'header': 'upload_mission', 
            'contents': {'way_points': way_points}
    }
    await exchange.publish(aio_pika.Message(body=pickle.dumps(message)), routing_key=f"to{VEHICLE_CONFIG.DRONE_NAME}")
    # print('Published')
    await asyncio.sleep(1)

    message = {
        'header': 'takeoff',
        'contents': {'takeoff_alt': 10}
    }
    await exchange.publish(aio_pika.Message(body=pickle.dumps(message)), routing_key=f"to{VEHICLE_CONFIG.DRONE_NAME}")
    # print('Published')
    await asyncio.sleep(1)

    message = {
        'header': 'start_mission',
        'contents': {}
    }
    await exchange.publish(aio_pika.Message(body=pickle.dumps(message)), routing_key=f"to{VEHICLE_CONFIG.DRONE_NAME}")
    # print('Published')
    await asyncio.sleep(1)

    return


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

    consumer_task = loop.create_task(task_publish(connection))

    try:
        await asyncio.gather(consumer_task)
    except KeyboardInterrupt:
        pass
    finally:
        await connection.close()
        print("Connection closed")

if __name__ == "__main__":
    asyncio.run(main())