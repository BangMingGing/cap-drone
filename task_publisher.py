import aio_pika
import asyncio
import pickle

class Publisher():
    
    def __init__(self, connection, exchange_name, drone_name, target_queue):
        self.connection = connection
        self.exchange_name = exchange_name
        self.channel = None
        self.exchange = None
        self.drone_name = drone_name
        self.target_queue = target_queue
    

    async def initialize(self):
        self.channel = await self.connection.channel()

        self.exchange = aio_pika.Exchange(
            self.channel, self.exchange_name, 
            type=aio_pika.ExchangeType.DIRECT
        )
        await self.exchange.declare()


    async def publish(self, message):    
        await self.exchange.publish(
            aio_pika.Message(body=pickle.dumps(message)), 
            routing_key=f"to{self.target_queue}"
        )

    
    async def send_mission_valid_message(self, current_mission):
        message = {'drone_name': self.drone_name, 
                   'header': 'mission_valid', 
                   'contents': {'current_mission': current_mission}
        }
        await self.publish(message)

    async def send_mission_finished_message(self, direction):
        message = {'drone_name': self.drone_name, 
                   'header': 'mission_finished', 
                   'contents': {'direction': direction}
        }
        await self.publish(message)

    async def send_resume_valid_message(self, current_mission):
        message = {'drone_name': self.drone_name,
                   'header': 'resume_valid',
                   'contents': {'current_mission': current_mission}
        }
        await self.publish(message)

    async def send_tensor_data_message(self, tensor):
        message = {'drone_name': self.drone_name,
                   'header': 'face_recog',
                   'contents': {'tensor': tensor}
        }
        await self.publish(message)

    async def send_face_recog_end_message(self, receiver):
        message = {'drone_name': self.drone_name,
                   'header': 'face_recog_finish',
                   'contents': {'receiver': receiver}
        }
        await self.publish(message)

    
    async def close(self):
        if self.connection:
            await self.connection.close()



async def main():
    publisher = Publisher('task')
    await publisher.initialize()


if __name__ == "__main__":
    asyncio.run(main())