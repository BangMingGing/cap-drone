
from mavsdk.mission import MissionItem, MissionPlan

from config import MISSION_STATUS

class Controller():
    def __init__(self, drone):
        self.drone = drone
        self.GPS = {}
        self.mission_status = MISSION_STATUS.WAITIING

        self.current_mission = 0
        self.total_mission = 0


    async def upload_mission(self, way_points):
        if self.mission_status == MISSION_STATUS.WAITIING:
            await self.drone.mission.clear_mission()
            mission_items = []
            for (lat, lon, alt) in way_points:
                mission_items.append(
                    MissionItem(lat, lon, alt, 5, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan')),
                )
            mission_plan = MissionPlan(mission_items)
            await self.drone.mission.set_return_to_launch_after_mission(False)

            print("-- Upload mission")
            await self.drone.mission.upload_mission(mission_plan)
            self.mission_status = MISSION_STATUS.UPLOADED
            return
        
        else:
            print("Performing another mission")
            return

    

    async def start_mission(self):
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
            print("Mission Finished")
            return
        
        elif self.mission_status == MISSION_STATUS.WAITIING:
            print("Waiting for mission")
            return
    

    async def pause_mission(self):
        if self.mission_status == MISSION_STATUS.PERFORMING:
            print("-- Pause mission")
            await self.drone.mission.pause_mission()
            return
        
        else:
            print("Drone is not performing mission")
            return


    async def takeoff(self, takeoff_alt):
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
                self.mission_status == MISSION_STATUS.FINISHED