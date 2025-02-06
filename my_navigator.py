import requests
from geopy import distance

class NavigateUser:
    def __init__(self, voice_assistant):
        self.api_key = '817bc7a94413df38442cc19ce29588a7'
        self.user_step_navigation = False
        self.voice_assistant = voice_assistant
        self.user_coord = [80.18016943867312, 13.078225002745956]  # 默认坐标，实际应用中可以获取实时GPS坐标
    
    # 获取目标地址的经纬度
    def get_location_coords(self, address):
        geocode_url = f"https://restapi.amap.com/v3/geocode/geo?address={address}&key={self.api_key}"
        response = requests.get(geocode_url)
        if response.status_code == 200:
            result = response.json()
            if result['status'] == '1' and result['geocodes']:
                coords = result['geocodes'][0]['location'].split(',')
                return [float(coords[0]), float(coords[1])]
            else:
                self.voice_assistant.speak("无法找到该地址，请重试。")
                return None
        else:
            self.voice_assistant.speak("获取坐标失败，请检查网络连接。")
            return None
    
    # 设置导航
    def setupNavigation(self, address):
        destination_coords = self.get_location_coords(address)
        if destination_coords:
            user_coord = self.user_coord  # 实际应用中应使用实时获取的GPS坐标
            self.get_navigation_steps(user_coord, destination_coords)
    
    # 获取从当前位置到目标地点的导航步骤
    def get_navigation_steps(self, user_coord, destination_coords):
        # 调用高德路径规划API获取步行导航路线
        directions_url = f"https://restapi.amap.com/v3/direction/walking?origin={user_coord[0]},{user_coord[1]}&destination={destination_coords[0]},{destination_coords[1]}&key={self.api_key}"
        response = requests.get(directions_url)
        if response.status_code == 200:
            result = response.json()
            if result['status'] == '1' and result['route']['paths']:
                steps = result['route']['paths'][0]['steps']
                self.user_step_navigation = True
                self.steps = steps
                self.prev_dist = 0
                self.total_distance = result['route']['paths'][0]['distance']
                self.voice_assistant.speak(steps[0]['instruction'])  # 给出第一步的指引
            else:
                self.user_step_navigation = False
                self.voice_assistant.speak("无法规划路径，请检查地址或网络连接。")
        else:
            self.user_step_navigation = False
            self.voice_assistant.speak("获取路径失败，请检查网络连接。")
    
    # 停止导航
    def stopNavigation(self):
        self.user_step_navigation = False
        self.voice_assistant.speak('导航已停止')

    # 持续导航，更新位置并给出指引
    def navigate(self, user_coord):
        if self.user_step_navigation and len(self.steps) > 0:
            # 计算当前位置与下一步指令的距离
            loc = self.steps[0]['polyline'].split(';')[0].split(',')
            loc = [float(loc[0]), float(loc[1])]
            dist = distance.distance((loc[1], loc[0]), (user_coord[1], user_coord[0])).meters
            if dist < 20:  # 如果距离小于20米，表示到达该步骤
                self.steps.pop(0)
                if len(self.steps) > 0:
                    self.voice_assistant.speak(self.steps[0]['instruction'])  # 下一步的指示
                else:
                    self.voice_assistant.speak('您已到达目的地')
                    self.user_step_navigation = False
            self.prev_dist = dist
