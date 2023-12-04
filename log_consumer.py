import aio_pika
import asyncio
import pickle

from config import RABBITMQ_CONFIG


async def log_consume(connection):
    channel = await connection.channel()
    exchange = aio_pika.Exchange(channel, "log", type=aio_pika.ExchangeType.DIRECT)
    await exchange.declare()
    queue = await channel.declare_queue('log_saver')
    await queue.bind(exchange, f"to{queue}")

    semaphore = asyncio.Semaphore(value=1)

    async def consume_with_semaphore():
        async with semaphore:
            async for message in queue:
                async with message.process():
                    message_data = pickle.loads(message.body, encoding='bytes')
                    print(f"Received message: {message_data}")


    print("Log Consumer started")

    while True:
        await consume_with_semaphore()

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

    consumer_task = loop.create_task(log_consume(connection))

    try:
        await asyncio.gather(consumer_task)
    except KeyboardInterrupt:
        pass
    finally:
        await connection.close()
        print("Connection closed")

if __name__ == "__main__":
    asyncio.run(main())