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

sys.path.append("/workspaces/ros2/servo/src/pkg_servo/src/scservo_sdk")
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

id_arr=[11,12,13] #servo ids

for scs_id in id_arr:
    scs_comm_result, scs_error = packetHandler.enable_torque(scs_id)
    if scs_comm_result != COMM_SUCCESS:
        print("1 %s" % packetHandler.getTxRxResult(scs_comm_result))
    if scs_error != 0:
        print("%s" % packetHandler.getRxPacketError(scs_error))
packetHandler.RegAction()    

df = pd.read_csv("arm_data.csv")
df = df.drop("Unnamed: 0", axis=1)
display(df)

for i in range(len(df)):

    for scs_id in id_arr:
        scs_addparam_result = packetHandler.SyncWritePosEx(scs_id,df[str(scs_id)].iloc[i], SCS_MOVING_SPEED, SCS_MOVING_ACC)
        if scs_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % scs_id)

    scs_comm_result = packetHandler.groupSyncWrite.txPacket()
    if scs_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(scs_comm_result))
    packetHandler.groupSyncWrite.clearParam()
    time.sleep(0.004) #delay

# # # Close port
portHandler.closePort()
