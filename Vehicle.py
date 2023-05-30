
import asyncio
import requests

from mavsdk import System

from face_recog_system.face_recog import Face_Recognizer


SYSTEM_ADDRESS = "udp://:14540"
# SYSTEM_ADDRESS = "serial:///dev/ttyACM0"

class Controller():
    def __init__(self, drone_name, lock):
        
        self.my_name = '[Vehicle]'
        self.drone_name = drone_name
        self.lock = lock
        
        self.takeoff_diff = 0.1
        self.landing_diff = 0.1
        self.goto_diff = 1e-6
        
        # Face_Recognition 인스턴스 생성
        self.face_recognizer = Face_Recognizer()
        
        self.url = "203.255.57.122:8888/face/face_recog_inference"
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
        
        
        elif header == 'face_recognition':
            pre_inference_model = contents['pre_inference_model']
            receiver_info = contents['receiver_info']
            print(f"{self.my_name} face_recognition call")
            asyncio.run(self.face_recognition(pre_inference_model, receiver_info))
            return
        else :
            print("Header keyword Error")
        

        return

    
    async def face_recognition(self, pre_inference_model, receiver_info):
        for _ in range(30):
            result = self.face_recognizer.face_recognition(cap_name=0)
            payload = {'result': result, 'drone_name': self.drone_name}
            response = requests.post(self.url, json=payload)
            
            await asyncio.sleep(1)
        
        return
    
    
    
    async def goto(self, lat, lon, alt):
        with self.lock:
            drone = System()
            await drone.connect(system_address=SYSTEM_ADDRESS)
            
            print("Waiting for drone to connect...")
            async for state in drone.core.connection_state():
                if state.is_connected:
                    print(f"-- Connected to drone!")
                    break
            
            print(f"{self.my_name} Goto {lat}, {lon}...")
            
            # 이동할 목표 지점
            async for position in drone.telemetry.position():
                flying_alt = position.absolute_altitude_m + alt
                break
            
            await drone.action.goto_location(lat, lon, flying_alt, 0)
            
        # 목표 좌표 도달 확인
        while True:
            with self.lock:
                async for position in drone.telemetry.position():
                    cur_lat = position.latitude_deg
                    cur_lon = position.longitude_deg
                    # print(cur_lat, cur_lon)
                    break
                
            if abs(cur_lat - lat) < self.goto_diff and abs(cur_lon - lon) < self.goto_diff:
                print("Arrived at Target lat, lon")
                break
            
            await asyncio.sleep(1)
        
        print(f"{self.my_name} Goto {lat}, {lon} End...")
        
        return
    
    
    async def arm(self):
        with self.lock:
            drone = System()
            await drone.connect(system_address=SYSTEM_ADDRESS)
            
            print("Waiting for drone to connect...")
            async for state in drone.core.connection_state():
                if state.is_connected:
                    print(f"-- Connected to drone!")
                    break
                
            print(f"{self.my_name} Arming...")
            
            await drone.action.arm()
        await asyncio.sleep(5)
                
        print(f"{self.my_name} Arming End...")

        return
    
    
    async def disarm(self):
        with self.lock:
            drone = System()
            await drone.connect(system_address=SYSTEM_ADDRESS)
            
            print("Waiting for drone to connect...")
            async for state in drone.core.connection_state():
                if state.is_connected:
                    print(f"-- Connected to drone!")
                    break
                
            print(f"{self.my_name} Disarming...")
            
            await drone.action.disarm()
        await asyncio.sleep(5)
        
        print(f"{self.my_name} Disarming End...")

        return

    
    async def takeoff(self, takeoff_alt):
        with self.lock:
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
            with self.lock:
                async for position in drone.telemetry.position():
                    cur_alt = position.relative_altitude_m
                    # print(cur_alt)
                    break
            
            if abs(cur_alt - takeoff_alt) < self.takeoff_diff:
                print("Arrived at Target alt - takeoff")
                break
                
            await asyncio.sleep(1)
        
        print(f"{self.my_name} Taking off End...")
        
        return
            
    
    async def landing(self):
        with self.lock:
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
            with self.lock:
                async for position in drone.telemetry.position():
                    cur_alt = position.relative_altitude_m
                    print(cur_alt)
                    break
            
            if cur_alt < self.landing_diff:
                print("Arrived at Target alt - landing")
                break
                
            await asyncio.sleep(1)
        
        print(f"{self.my_name} Taking off End...")
        
        print(f"{self.my_name} Landing End...")

        return
        


class Logger():
    def __init__(self, drone_name, lock):

        self.drone_name = drone_name
        self.lock = lock
        self.GPS = {}

        return

    async def get_status(self):
        with self.lock:
            drone = System()
            await drone.connect(system_address=SYSTEM_ADDRESS)
            
            # print("Waiting for drone to connect...")
            async for state in drone.core.connection_state():
                if state.is_connected:
                    # print(f"-- Connected to drone!")
                    break
                
            async for position in drone.telemetry.position():
                self.GPS['lat'] = position.latitude_deg
                self.GPS['lon'] = position.longitude_deg
                self.GPS['abs_alt'] = position.absolute_altitude_m
                self.GPS['rel_alt'] = position.relative_altitude_m
                break
            
            """async for speed in drone.telemetry.ground_speed_ned():
                self.GPS['speed'] = math.sqrt(speed.velocity_north_m_s**2 + speed.velocity_east_m_s**2 + speed.velocity_down_m_s**2)
                break"""
                
            async for battery in drone.telemetry.battery():
                self.GPS['battery'] = battery.remaining_percent
                break
            
        return self.GPS



if __name__ == "__main__":
        
    # logger = Logger()
    # gps = asyncio.run(logger.get_status())
    # print(gps)
    
    controller = Controller()
    
    asyncio.run(controller.arm())
    asyncio.run(controller.takeoff(5))
    asyncio.run(controller.goto(47.39777, 8.54565, 0))
    asyncio.run(controller.landing())
    
    
    