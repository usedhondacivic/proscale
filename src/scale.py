import time
import sys
import RPi.GPIO as GPIO
from hx711v0_5_1 import HX711

button_pins = [22,27,17,23]
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

for pin in button_pins:
	GPIO.setup(pin, GPIO.IN,pull_up_down=GPIO.PUD_UP)



run = True
Tare = False
Convert = False

ReferenceUnit = 384
hx = HX711(5,6)
hx.setReferenceUnit(ReferenceUnit)
hx.tare()
hx.setUnit('gram')
hx.reset()
print("[INFO]Start weighting!")

def CleanAndExit():
	print("[INFO]Cleaning..")
	GPIO.cleanup()
	print("[INFO]Bye!")
	sys.exit()

while run:
	try:
		raw_value = hx.getLong()
		offset = hx.getOffset()
		weight = hx.getWeight()
		#print(f"Weight: {weight:.2f} {hx.getUnit()}")
		print(f"Raw Value: {raw_value}, Offset: {offset}, Weight: {weight:.2f} {hx.getUnit()}")
		hx.powerDown()
		hx.powerUp()
		time.sleep(0.2)

		if (not GPIO.input(27)): #exit
			CleanAndExit()
		if (not GPIO.input(17)): #tare
			'''
			hx.autosetOffset()
			OffsetValue = hx.getOffset()
			print(f"[INFO] Automatically setting the offset. The new value is '{OffsetValue}' .")
			print(f"[INFO] Start weighting!")
			'''
			hx.tare()
			print("[INFO] Scale has been tared.")
		
		if (not GPIO.input(22)):
			if hx.getUnit() == 'gram':
				hx.setUnit('ounce')
			else:
				hx.setUnit('gram')
				print(f"[INFO] Unit switched to {hx.getUnit()}.")
			
			'''
			Convert = not Convert
			if Convert:
				hx.setChannel(channel='B')
			else:
				hx.setChannel(channel='A')
			ReferenceUnit = hx.getReferenceUnit()
			hx.setReferenceUnit(ReferenceUnit) 
			'''


	except (KeyboardInterrupt, SystemExit):
		CleanAndExit()

