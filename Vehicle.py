import time
import math

from dronekit import connect, Command, LocationGlobal
from pymavlink import mavutil

# from Face_Recog_System import Face_Recognizer




class Controller():
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.my_name = '[Vehicle]'
        self.vehicle._master.mav.command_long_send(
            self.vehicle._master.target_system, 
            self.vehicle._master.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 
            0, 4, 0, 0, 0, 
            0, 0, 0
            )
        self.cmds = vehicle.commands
        self.cmds.clear()
        
        
        # Face_Recognition 인스턴스 생성
        # self.face_recognizer = Face_Recognizer()
        return 
    
    
    def control(self, header, contents):
        if header == 'goto':
            lat = contents['lat']
            lon = contents['lon']
            alt = contents['alt']
            print(f"{self.my_name} goto call")
            self.goto(lat, lon ,alt)
            return

        elif header == 'arm':
            print(f"{self.my_name} arm call")
            self.arm()
        
        elif header == 'disarm':
            print(f"{self.my_name} disarm call")
            self.disarm()
            return
            
        elif header == 'takeoff':
            alt = contents['alt']
            print(f"{self.my_name} takeoff Call")
            self.takeoff(takeoff_alt=alt)
            return
        
        elif header == 'landing':
            print(f"{self.my_name} landing call")
            self.landing()
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
    

    def goto(self, lat, lon, alt):
        print(f"{self.my_name} Goto {lat}, {lon}...")
        
        # 이동할 목표 지점
        target_location = LocationGlobal(lat, lon, alt)
        
        cmd = Command(
            0,0,0, 
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 
            0, 1, 0, 0, 0, 0, 
            target_location.lat, target_location.lon, target_location.alt
        )
        self.cmds.add(cmd)
        
        
        # 목표 지점에 도달할 때까지 대기
        while True:
            current_location = self.vehicle.location.global_relative_frame
            distance = current_location.distance_to(target_location)
            if distance < 1:
                break

        return
    
    def arm(self):
        print(f"{self.my_name} Arming...")
        
        self.vehicle.armed = True
        
        while not self.vehicle.armed:
            time.sleep(1)

        return
    
    def disarm(self):
        print(f"{self.my_name} Disarming...")
        
        self.vehicle.armed = False
        
        while self.vehicle.armed:
            time.sleep(1)    

        return
    
    def takeoff(self, takeoff_alt):
        print(f"{self.my_name} Taking off...")
        
        print('take_off lat: ', takeoff_alt)
        
        current_location = self.vehicle.location.global_relative_frame
        wp = LocationGlobal(current_location.lat, current_location.lon, current_location.alt+takeoff_alt)
        print(current_location)
        cmd = Command(
            0,0,0, 
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 
            0, 1, 0, 0, 0, 0, 
            wp.lat, wp.lon, wp.alt
        )
        self.cmds.add(cmd)
        
        # 설정 고도까지 올라갈 때까지 대기
        while True:
        # 현재 높이 확인
            altitude = self.vehicle.location.global_relative_frame.alt
            # print("alt: ", altitude)
            # 설정 고도에 도달하면 반복문 종료
            if altitude >= takeoff_alt * 0.9:
                break


        return
    
    def landing(self):
        print(f"{self.my_name} Landing...")
        
        current_location = self.vehicle.location.global_relative_frame
        print(current_location)
        wp = LocationGlobal(current_location.lat, current_location.lon, current_location.alt)

        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 1, 0, 0, 0, 0, wp.lat, wp.lon, 0)
        self.cmds.add(cmd)
        
        # 설정 고도까지 올라갈 때까지 대기
        while True:
        # 현재 높이 확인
            altitude = self.vehicle.location.global_relative_frame.alt
            # print("alt: ", altitude)
            # 설정 고도에 도달하면 반복문 종료
            if altitude <= 0.1:
                break
        
        current_location = self.vehicle.location.global_relative_frame
        print(current_location)

        return
    
    

class Logger():
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.GPS = {}

        return
    
    def get_status(self):
        self.GPS['alt'] = self.vehicle.location.global_relative_frame.alt
        self.GPS['lat'] = self.vehicle.location.global_relative_frame.lat
        self.GPS['lon'] = self.vehicle.location.global_relative_frame.lon
        self.GPS['speed'] = self.vehicle.groundspeed
        self.GPS['battery'] = self.vehicle.battery.level

        return self.GPS
    
    
    
if __name__ == "__main__":
    
    # connection_string = '/dev/ttyACM0'
    connection_string = 'udp:127.0.0.1:14540'
    
    vehicle = connect(connection_string, wait_ready=True)
    
    controller = Controller(vehicle)
    controller.arm()
    controller.takeoff(10)
    time.sleep(5)
    controller.landing()