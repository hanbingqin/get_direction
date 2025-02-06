import sys
import json
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode, quote_plus
from playsound import playsound
import datetime
from pydub import AudioSegment
from pydub.playback import play
class BaiduTTS:
    """百度语音合成类"""
    def __init__(self, app_id, api_key, secret_key):
        """初始化类的实例，设置必要的 API 配置"""
        self.APP_ID = app_id
        self.API_KEY = api_key
        self.SECRET_KEY = secret_key
        self.TOKEN_URL = 'http://aip.baidubce.com/oauth/2.0/token'
        self.TTS_URL = 'http://tsn.baidu.com/text2audio'
        self.SCOPE = 'audio_tts_post'  # 有此scope表示有tts能力，没有请在网页里勾选
        self.CUID = "123456PYTHON"  # 用户标识（可以自定义）

        self.PER = 4  # 发音人选择，默认为度丫丫（4）
        self.SPD = 6  # 语速（0-15），默认为5
        self.PIT = 5   # 音调（0-15），默认为5
        self.VOL = 9   # 音量（0-9），默认为5
        self.AUE = 3   # 下载的文件格式，3：mp3（默认），4：pcm-16k，5：pcm-8k，6：wav
        self.FORMATS = {3: "mp3", 4: "pcm", 5: "pcm", 6: "wav"}
        self.FORMAT = self.FORMATS[self.AUE]
        print("init TTS successfully!")

    def fetch_token(self):
        """获取百度语音合成的 token"""
        params = {'grant_type': 'client_credentials',
                  'client_id': self.API_KEY,
                  'client_secret': self.SECRET_KEY}
        post_data = urlencode(params).encode('utf-8')

        req = Request(self.TOKEN_URL, post_data)
        try:
            f = urlopen(req, timeout=5)
            result_str = f.read()
        except URLError as err:
            print('token http response http code : ' + str(err.code))
            result_str = err.read()

        result_str = result_str.decode()
        result = json.loads(result_str)

        if 'access_token' in result.keys() and 'scope' in result.keys():
            if self.SCOPE not in result['scope'].split(' '):
                raise Exception('scope is not correct')
            print(f"成功获取 token: {result['access_token']}；过期时间（秒）: {result['expires_in']}")
            return result['access_token']
        else:
            raise Exception('API_KEY 或 SECRET_KEY 不正确，未能获取到 token')

    def text_to_speech(self, text):
        """将文本转换为语音并播放"""
        token = self.fetch_token()  # 获取 token
        
        # print("token:", token)
        if len(text) > 500:
            print("text length is out of max limit")
        else:
            print("text len:", len(text))
        tex = quote_plus(text)  # URL 编码文本
        params = {
            'tok': token,
            'tex': tex,
            'per': self.PER,
            'spd': self.SPD,
            'pit': self.PIT,
            'vol': self.VOL,
            'aue': self.AUE,
            'cuid': self.CUID,
            'lan': 'zh',
            'ctp': 1
        }

        data = urlencode(params).encode('utf-8')
        req = Request(self.TTS_URL, data)
        has_error = False
        try:
            f = urlopen(req)
            result_str = f.read()

            headers = dict((name.lower(), value) for name, value in f.headers.items())
            has_error = ('content-type' not in headers.keys() or headers['content-type'].find('audio/') < 0)
        except URLError as err:
            print(f'ASR http response http code: {err.code}')
            result_str = err.read()
            has_error = True
        

        # 获取当前时间并格式化为字符串
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # 使用时间戳创建文件名
        save_file = f"error_{timestamp}.txt" if has_error else f'result_{timestamp}.{self.FORMAT}'

        # save_file = "error.txt" if has_error else f'result1.{self.FORMAT}'
        with open(save_file, 'wb') as of:
            of.write(result_str)

        if has_error:
            print(f"TTS API 错误: {result_str.decode('utf-8')}")
        else:
            print(f"语音合成结果已保存为: {save_file}")
            
        return save_file

            

def play_audio1(file_path):
    # subprocess.run(['ffmpeg', '-nostats', '-loglevel', '0', '-i', file, '-f', 'null', '-'])
    audio = AudioSegment.from_file(file_path)
    # 播放音频
    play(audio)

def play_audio(file_path):
    # 初始化pygame
    pygame.mixer.init()

    # 加载音频文件
    pygame.mixer.music.load(file_path)

    # 播放音频
    pygame.mixer.music.play()

    # 等待音频播放完成
    while pygame.mixer.music.get_busy():  # 检查是否正在播放
        pygame.time.Clock().tick(10)  # 每10毫秒检查一次








            
# 如果你想直接测试这个模块，可以在这里调用
if __name__ == '__main__':
    tts = BaiduTTS(
        app_id="117214641", 
        api_key="IMI61WO3ZJkWbNDxEmA8trnP", 
        secret_key="LKsRieJPGKcrDYErYvrguHeDwZ7iMf7r"
    )
    tts.text_to_speech("我是语音助手，很高兴能帮助你，请注意周围环境安全")
    # 使用示例
    # play_audio('result1.mp3')
