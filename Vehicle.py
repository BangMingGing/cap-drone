
import asyncio
import time

from threading import Thread, Lock
from mavsdk import System

from face_inferer import Face_Inferer


# SYSTEM_ADDRESS = "udp://:14540"
SYSTEM_ADDRESS = "serial:///dev/ttyACM0"

class Controller():
    def __init__(self, drone_name):
        
        self.my_name = '[Vehicle]'
        self.drone_name = drone_name
        
        self.takeoff_diff = 0.5
        self.landing_diff = 0.3
        self.goto_diff = 1e-5
        
        # Face_Recognition 인스턴스 생성
        self.face_inferer = Face_Inferer()

        self.GPS = {}
        asyncio.run(self.init_gps())
        
        self.url = "http://203.255.57.122:8888/face/face_recog_inference"
        return 


    def control(self, header, contents):
        if header == 'goto':
            lat = contents['lat']
            lon = contents['lon']
            alt = contents['alt']
            print(f"{self.my_name} goto call")
            asyncio.run(self.goto(lat, lon ,alt))
            return

        elif header == 'arm':
            print(f"{self.my_name} arm call")
            asyncio.run(self.arm())
        
        elif header == 'disarm':
            print(f"{self.my_name} disarm call")
            asyncio.run(self.disarm())
            return
            
        elif header == 'takeoff':
            alt = contents['alt']
            print(f"{self.my_name} takeoff Call")
            asyncio.run(self.takeoff(takeoff_alt=alt))
            return
        
        elif header == 'landing':
            print(f"{self.my_name} landing call")
            asyncio.run(self.landing())
            return
        
        elif header == 'wait':
            wait_time = contents['time']
            print(f"{self.my_name} wait call")
            asyncio.run(self.wait(wait_time))
            return
        
        elif header == 'face_recognition':
            pre_inference_model = contents['pre_inference_model']
            receiver_info = contents['receiver_info']
            print(f"{self.my_name} face_recognition call")
            asyncio.run(self.face_inferer.face_recognition_video(pre_inference_model, receiver_info))
            return

        else :
            print("Header keyword Error")
        

        return


    async def init_gps(self):
        
        drone = System()
        await drone.connect(system_address=SYSTEM_ADDRESS)
        
        print("Waiting for drone to connect...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print(f"-- Connected to drone!")
                break

                
        async for position in drone.telemetry.position():
            self.GPS['lat'] = position.latitude_deg
            self.GPS['lon'] = position.longitude_deg
            self.GPS['abs_alt'] = position.absolute_altitude_m
            self.GPS['rel_alt'] = position.relative_altitude_m
            break

        return 
    
    
    async def goto(self, lat, lon, alt):
        
        drone = System()
        await drone.connect(system_address=SYSTEM_ADDRESS)
        
        print("Waiting for drone to connect...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print(f"-- Connected to drone!")
                break
        
        print(f"{self.my_name} Goto {lat}, {lon} / alt change : {alt}...")
        
        # 이동할 목표 지점
        async for position in drone.telemetry.position():
            flying_alt = position.absolute_altitude_m + alt
            break
        
        await drone.action.goto_location(lat, lon, flying_alt, 0)
            
        # 목표 좌표 도달 확인
        while True:
            
            async for position in drone.telemetry.position():
                self.GPS['lat'] = position.latitude_deg
                self.GPS['lon'] = position.longitude_deg
                self.GPS['abs_alt'] = position.absolute_altitude_m
                self.GPS['rel_alt'] = position.relative_altitude_m
                break
                
            if abs(self.GPS['lat'] - lat) < self.goto_diff and abs(self.GPS['lon'] - lon) < self.goto_diff and abs(self.GPS['abs_alt'] - flying_alt) < self.takeoff_diff:
                print("Arrived at Target lat, lon")
                break
            
            await asyncio.sleep(1)
        
        print(f"{self.my_name} Goto {lat}, {lon} End...")
        
        return
    
    
    async def arm(self):
        
        drone = System()
        await drone.connect(system_address=SYSTEM_ADDRESS)
        
        print("Waiting for drone to connect...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print(f"-- Connected to drone!")
                break
            
        print(f"{self.my_name} Arming...")
        
        await drone.action.arm()
        await asyncio.sleep(2)
                
        print(f"{self.my_name} Arming End...")

        return
    
    
    async def disarm(self):
        
        drone = System()
        await drone.connect(system_address=SYSTEM_ADDRESS)
        
        print("Waiting for drone to connect...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print(f"-- Connected to drone!")
                break
            
        print(f"{self.my_name} Disarming...")
        
        await drone.action.disarm()
        await asyncio.sleep(2)
        
        print(f"{self.my_name} Disarming End...")

        return

    
    async def takeoff(self, takeoff_alt):
        
        drone = System()
        await drone.connect(system_address=SYSTEM_ADDRESS)
        
        print("Waiting for drone to connect...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print(f"-- Connected to drone!")
                break
            
        print(f"{self.my_name} Taking off...")
        
        print('take_off lat: ', takeoff_alt)
        
        await drone.action.set_takeoff_altitude(takeoff_alt)
        await drone.action.takeoff()
                
        # 목표 고도 도달 확인
        while True:
            
            async for position in drone.telemetry.position():
                self.GPS['lat'] = position.latitude_deg
                self.GPS['lon'] = position.longitude_deg
                self.GPS['abs_alt'] = position.absolute_altitude_m
                self.GPS['rel_alt'] = position.relative_altitude_m
                break
            
            if abs(self.GPS['rel_alt'] - takeoff_alt) < self.takeoff_diff:
                print("Arrived at Target alt - takeoff")
                break
                
            await asyncio.sleep(1)
        
        print(f"{self.my_name} Taking off End...")
        
        return
            
    
    async def landing(self):
        
        drone = System()
        await drone.connect(system_address=SYSTEM_ADDRESS)
        
        print("Waiting for drone to connect...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print(f"-- Connected to drone!")
                break
            
        print(f"{self.my_name} Landing...")
        
        await drone.action.land()
                
        # 목표 고도 도달 확인
        while True:
            
            async for position in drone.telemetry.position():
                self.GPS['lat'] = position.latitude_deg
                self.GPS['lon'] = position.longitude_deg
                self.GPS['abs_alt'] = position.absolute_altitude_m
                self.GPS['rel_alt'] = position.relative_altitude_m
                break
            
            if self.GPS['rel_alt'] < self.landing_diff:
                print("Arrived at Target alt - landing")
                break
                
            await asyncio.sleep(1)
        
        print(f"{self.my_name} Taking off End...")
        
        print(f"{self.my_name} Landing End...")

        return
        
    async def wait(self, wait_time):
        
        await asyncio.sleep(wait_time)
        
        return


if __name__ == "__main__":
        
    lock = Lock()
    controller = Controller('test')
    
    asyncio.run(controller.arm())
    asyncio.run(controller.takeoff(15))
    asyncio.run(controller.landing())
    
