import time
import serial
import pynmea2
from picamera2 import Picamera2
import threading 
import math
# from gsmmodem.modem import GsmModem, SentSms
# from gsmmodem.exceptions import InterruptedException, CommandError
import gpiod


class piAPI():
	def __init__(self,voice_assistant):
		print('pi API initiated')
		self.voice_assistant = voice_assistant
		# self.db = db
	
		self.setUpGPS()
		self.user_coord = [0,0]
		self.GPSActive = True
		self.fallDetected = False	
		self.setupVibrate()
		self.GSMActive = False
		self.picam2 = None
		self.start_capture()
	
	def send_at(self,command,back,timeout):
		rec_buff = ''
		self.serial.write((command+'\r\n').encode())
		time.sleep(timeout)
		if self.serial.inWaiting():
			time.sleep(0.01 )
			rec_buff = self.serial.read(self.serial.inWaiting())
		if rec_buff != '':
			if back not in rec_buff.decode():
				print(command + ' ERROR')
				print(command + ' back:\t' + rec_buff.decode())
				return 0
			else:
				print(rec_buff.decode())
				return 1
		else:
			print('GPS is not ready')
			return 0
			
	def setUpGPS(self):
		self.serial = serial.Serial('/dev/ttyAMA0',115200, timeout = 3)
		print('Start GPS session...')
		self.send_at('AT+CGPS=1,1','OK',1)
		self.serial.write(('AT+CGPSINFOCFG=1,2\r\n').encode('ISO-8859-1'))
		self.GPSActive = True
	
	def stopGPS(self):
		self.GPSActive = False
		print('Stop GPS session...')
		self.send_at('AT+CGPS=0,1','OK',1)
		self.serial.close()
	
	#to get gps coordinate
	def getLocation(self):
		data = ''
		#self.serial.write(('AT+CGPSINFOCFG=3,2\r\n').encode('ISO-8859-1'))
		data = self.serial.read(self.serial.inWaiting()).decode('ISO-8859-1')
		if data[0:6] == "$GPRMC":
			newmsg = pynmea2.parse(data)
			lat = newmsg.latitude
			lng = newmsg.longitude
			gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
			self.user_coord = [lng, lat]
			# self.db.sendGPS(self.user_coord)
			return [lng,lat]
	
	def setupVibrate(self):
		print('Initate vibration')
		vibration_pin = 17
		chip = gpiod.Chip('gpiochip4')
		self.led_line = chip.get_line(vibration_pin)
		self.led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

	def vibrateMotor(self, t):
		try:
			self.led_line.set_value(1)
			time.sleep(t)
			self.led_line.set_value(0)
		finally:
			self.led_line.release()
	

	 # 启动相机的方法
	def start_capture(self):
		if self.picam2 is None:
			self.picam2 = Picamera2()  # 初始化相机
			self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))  # 配置相机
			self.picam2.start()  # 启动相机
		print("Camera capture started.")
    
    # 停止相机的方法
	def stop_capture(self):
		if self.picam2:
			self.picam2.stop()  # 停止相机
			print("Camera capture stopped.")

   