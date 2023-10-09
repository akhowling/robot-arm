#!/usr/bin/env python3

from IPython.display import display, HTML
import sys
import os
import pandas as pd

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

sys.path.append("..")
# Uses SCServo SDK library
from scservo_sdk import *                       
# Default setting
BAUDRATE                    = 1000000           # SCServo default baudrate : 1000000
DEVICENAME                  = '/dev/ttyUSB0'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
SCS_MOVING_SPEED            = 2400              # SCServo moving speed
SCS_MOVING_ACC              = 50                # SCServo moving acc


# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Get methods and members of Protocol
packetHandler = sms_sts(portHandler)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()


# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

groupSyncRead = GroupSyncRead(packetHandler, SMS_STS_PRESENT_POSITION_L, 4)
# groupSyncWrite = GroupSyncWrite(packetHandler, SMS_STS_GOAL_POSITION_L, 2)

id_arr=[11,12,13] #servo ids

df = pd.DataFrame(columns=[11,12,13])


# Write SCServo goal position/moving speed/moving acc
for scs_id in id_arr:
    scs_comm_result, scs_error = packetHandler.disable_torque(scs_id)
    if scs_comm_result != COMM_SUCCESS:
        print("1 %s" % packetHandler.getTxRxResult(scs_comm_result))
    if scs_error != 0:
        print("%s" % packetHandler.getRxPacketError(scs_error))
packetHandler.RegAction()

while 1:
    try:
        for scs_id in id_arr:
            scs_addparam_result = groupSyncRead.addParam(scs_id)
            if scs_addparam_result != True:
                print("[ID:%03d] groupSyncRead addparam failed" % scs_id)

        scs_comm_result = groupSyncRead.txRxPacket()
        if scs_comm_result != COMM_SUCCESS:
            print("2 %s" % packetHandler.getTxRxResult(scs_comm_result))
        data=[]

        for scs_id in id_arr:            
            scs_data_result, scs_error = groupSyncRead.isAvailable(scs_id, SMS_STS_PRESENT_POSITION_L, 4)
            if scs_data_result == True:
                scs_present_position = groupSyncRead.getData(scs_id, SMS_STS_PRESENT_POSITION_L, 2)
                scs_present_speed = groupSyncRead.getData(scs_id, SMS_STS_PRESENT_SPEED_L, 2)
                data.append(scs_present_position)
            else:
                print("[ID:%03d] groupSyncRead getdata failed" % scs_id)
                continue
            if scs_error != 0:
                print("%s" % packetHandler.getRxPacketError(scs_error))     
        groupSyncRead.clearParam()
        df.loc[len(df)] = data
        data=[]
        time.sleep(0.004)  #delay

    except KeyboardInterrupt:
        break
display(df) 
df.to_csv('arm_data.csv')     

# for scs_id in id_arr:
#     scs_comm_result, scs_error = packetHandler.enable_torque(scs_id)
#     if scs_comm_result != COMM_SUCCESS:
#         print("1 %s" % packetHandler.getTxRxResult(scs_comm_result))
#     if scs_error != 0:
#         print("%s" % packetHandler.getRxPacketError(scs_error))
# packetHandler.RegAction()





# # Close port
portHandler.closePort()
