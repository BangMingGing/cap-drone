import time
import cv2 as cv

from mavsdk.mission import MissionItem, MissionPlan

from face_recog_module.client import Client_Inferer

from config import MISSION_STATUS, ADMIN_STATUS, VEHICLE_CONFIG

class Controller():
    def __init__(self, drone, publisher):
        self.drone = drone
        
        self.publisher = publisher

        self.GPS = {}
        self.mission_status = MISSION_STATUS.WAITIING
        self.admin_status = ADMIN_STATUS.NORMAL
        self.direction = None

        self.client_inferer = Client_Inferer()
        self.receiver = None

        self.current_mission = 0
        self.total_mission = 0


    async def set_receiver(self, receiver):
        self.receiver = receiver


    async def upload_mission(self, mission, direction):
        if self.mission_status == MISSION_STATUS.WAITIING or self.mission_status == MISSION_STATUS.FINISHED:
            await self.drone.mission.clear_mission()
            self.direction = direction

            mission_items = []
            for (lon, lat, alt) in mission:
                mission_items.append(
                    MissionItem(lat, lon, alt+VEHICLE_CONFIG.ALT_UP, VEHICLE_CONFIG.SPEED, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan')),
                )
            mission_plan = MissionPlan(mission_items)
            await self.drone.mission.set_return_to_launch_after_mission(False)

            async for current_state in self.drone.telemetry.health():
                if current_state.is_global_position_ok:
                    print("Vehicle is ready for a new mission.")
                    break
                else:
                    print("Vehicle is not in a state to upload a new mission.")

            print("-- Upload mission")
            await self.drone.mission.upload_mission(mission_plan)
            self.mission_status = MISSION_STATUS.UPLOADED
            return
        
        else:
            print("Performing another mission")
            return

    

    async def start_mission(self):
        if self.admin_status == ADMIN_STATUS.NORMAL:
            if self.mission_status == MISSION_STATUS.UPLOADED:
                print("-- Start mission")
                await self.drone.mission.start_mission()
                self.mission_status = MISSION_STATUS.PERFORMING
                return
            
            elif self.mission_status == MISSION_STATUS.PAUSED:
                print("-- Resume mission")
                await self.drone.mission.start_mission()
                self.mission_status = MISSION_STATUS.PERFORMING
                return

            elif self.mission_status == MISSION_STATUS.PERFORMING:
                print("Already performing mission")
                return
            
            elif self.mission_status == MISSION_STATUS.FINISHED:
                print("Mission Finished But Return Mission Start")
                await self.drone.mission.start_mission()
                self.mission_status = MISSION_STATUS.PERFORMING
                return
            
            elif self.mission_status == MISSION_STATUS.WAITIING:
                print("Waiting for mission")
                return
    

    async def pause_mission(self):
        if self.mission_status == MISSION_STATUS.PERFORMING:
            print("-- Pause mission")
            await self.drone.mission.pause_mission()
            await self.publisher.send_resume_valid_meessage(self.current_mission)
            return
        
        else:
            print("Drone is not performing mission")
            return


    async def takeoff(self, takeoff_alt):
        if self.admin_status == ADMIN_STATUS.NORMAL:
            if self.mission_status == MISSION_STATUS.UPLOADED:
                print(f"-- Takeoff {takeoff_alt}m")
                await self.drone.action.arm()
                await self.drone.action.set_takeoff_altitude(takeoff_alt)
                await self.drone.action.takeoff()
                return
            
            else:
                print("Mission is not uploaded")
                return


    async def land(self):
        if self.mission_status == MISSION_STATUS.FINISHED:
            print("-- Landing")
            await self.drone.action.land()
            self.mission_status = MISSION_STATUS.WAITIING
            return
        
        else:
            print("Mission is not finished")
            return
        

    async def set_GPS(self):
        async for position in self.drone.telemetry.position():
            self.GPS['lat'] = position.latitude_deg
            self.GPS['lon'] = position.longitude_deg
            self.GPS['abs_alt'] = position.absolute_altitude_m
            self.GPS['rel_alt'] = position.relative_altitude_m
            return

    async def set_mission_progress(self):
        async for mission_progress in self.drone.mission.mission_progress():
            print(f"Mission progress: "
            f"{mission_progress.current}/"
            f"{mission_progress.total}")

            self.current_mission = mission_progress.current
            self.total_mission = mission_progress.total

            if self.current_mission == self.total_mission:
                self.mission_status = MISSION_STATUS.FINISHED
                await self.publisher.send_mission_finished_message(self.direction)

            else:
                await self.publisher.send_mission_valid_message(mission_progress.current)


    async def admin_pause(self):
        print("-- Admin Pause")
        await self.drone.mission.pause_mission()
        self.admin_status = ADMIN_STATUS.ABNORMAL

    async def admin_resume(self):
        print("-- Admin Resume")
        await self.drone.mission.start_mission()
        self.admin_status = ADMIN_STATUS.NORMAL

    async def admin_land(self):
        print("-- Admin Land")
        await self.drone.action.land()
        self.admin_status = ADMIN_STATUS.ABNORMAL
    
    
    async def temp_face_recog_start(self):
        await self.drone.action.hold()

        end_time = time.time() + 6

        while True:
            if time.time() > end_time:
                break
        await self.publisher.send_face_recog_end_message(self.receiver)
        print('face_recog_end_message published')


    async def face_recog_start(self):
        cap = cv.VideoCapture(0)

        end_time = time.time() + 6

        while True:
            if time.time() > end_time:
                break

            if not cap.isOpened():
                print("Failed to open the camera")
                break

            ret, img = cap.read()

            if ret:
                is_face, tensor = await self.client_inferer.inference_img(img)
                
                if is_face:
                    print('tensor published')
                    await self.publisher.send_tensor_data_message(tensor)
        
        await self.publisher.send_face_recog_end_message(self.receiver)
        print('face_recog_end_message published')
