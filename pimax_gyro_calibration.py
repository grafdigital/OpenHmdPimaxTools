import hid
from time import sleep
from datetime import datetime
import math
import numpy as np
import matplotlib.pyplot as plt
from pimax_common import decode_sample, decode_frame, BufferPointer

vid = 0x0483
pid = 0x0021

BUFFER_SIZE=256

with hid.Device(vid, pid) as h:
    print(f'Device manufacturer: {h.manufacturer}')
    print(f'Product: {h.product}')
    print(f'Serial Number: {h.serial}')

    sleep(1)

    h.send_feature_report(b'\x11\x00\x00\x0b\x10\x27')

    sleep(1)

    keep_alive = datetime.now()

    gdata = []

    while len(gdata) < 1000:
        data = h.read(BUFFER_SIZE, 1000)
        if len(data) > 0:
            if data[0] == 11:
                frame = decode_frame(data)
                #print(frame)

                a = [
                    frame['samples'][0]['gyro'][0] * 0.0001,
                    frame['samples'][0]['gyro'][1] * 0.0001,
                    frame['samples'][0]['gyro'][2] * 0.0001,
                ]
                gdata.append(a)

                if len(gdata) % 50 == 0:
                    print(len(gdata))

            else:
                print(f'Unknown Message: {data[0]:X}')

        now = datetime.now()
        if (now - keep_alive).total_seconds() > 3:
            h.send_feature_report(b'\x11\x00\x00\x0b\x10\x27')
            keep_alive = now

    gdata = np.array(gdata)

    gyro_labels = ['w_x','w_y','w_z']
    gyro_offsets = [-1,-1,-1]

    for qq in range(0,3):
        gyro_offsets[qq] = np.mean(gdata[:,qq]) # average

    fig,axs = plt.subplots(2,1,figsize=(12,9))
    for ii in range(0,3):
        axs[0].plot(gdata[:,ii],
                    label='${}$, Uncalibrated'.format(gyro_labels[ii]))
        axs[1].plot(gdata[:,ii]-gyro_offsets[ii],
                    label='${}$, Calibrated'.format(gyro_labels[ii]))
    axs[0].legend(fontsize=14);axs[1].legend(fontsize=14)
    axs[0].set_ylabel('$w_{x,y,z}$ [$^{\circ}/s$]',fontsize=18)
    axs[1].set_ylabel('$w_{x,y,z}$ [$^{\circ}/s$]',fontsize=18)
    axs[1].set_xlabel('Sample',fontsize=18)
    axs[0].set_title('Gyroscope Calibration Offset Correction',fontsize=22)

    print('*** replace the gryo_offset with the next line in pimax.c ***')
    print('const float gyro_offset[] = { ' + ', '.join([str(x) for x in gyro_offsets]) + ' };')
    print('***') 

    plt.show()

