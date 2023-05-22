import time
import math
import asyncio

from mavsdk import System

# from Face_Recog_System import Face_Recognizer


# SYSTEM_ADDRESS = "udp://:14540"
SYSTEM_ADDRESS = "serial:///dev/ttyACM0"

class Controller():
    def __init__(self):
        self.my_name = '[Vehicle]'
        
        # Face_Recognition 인스턴스 생성
        # self.face_recognizer = Face_Recognizer()
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
        
        """    
        elif header == 'face_recognition':
            pre_inference_model = contents['pre_inference_model']
            receiver_info = contents['receiver_info']
            print(f"{self.my_name} face_recognition call")
            self.face_recognizer.face_recognition(pre_inference_model, receiver_info)
            return
        else :
            print("Header keyword Error")
        """
        

        return

    async def goto(self, lat, lon, alt):
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
        await asyncio.sleep(20)
        
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
        await asyncio.sleep(5)
        
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
        await asyncio.sleep(5)
        
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
        await asyncio.sleep(15)
        
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
        await asyncio.sleep(15)
        
        print(f"{self.my_name} Landing End...")

        return
    
    

class Logger():
    def __init__(self):

        self.GPS = {}

        return

    async def get_status(self):
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