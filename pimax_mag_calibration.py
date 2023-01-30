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

    while len(gdata) < 2000:
        data = h.read(BUFFER_SIZE, 1000)
        if len(data) > 0:
            if data[0] == 11:
                frame = decode_frame(data)
                #print(frame)

                a = [
                    frame['mag'][0] * 0.0001,
                    frame['mag'][1] * 0.0001,
                    frame['mag'][2] * 0.0001,
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

    min_max = [ (np.min(gdata[:,qq]), np.max(gdata[:,qq])) for qq in range(3)]
    mag_offset = [ (i[1] + i[0]) / 2 for i in min_max ]

    range_scale = 0.0001

    limit = 1.25

    fig, axs = plt.subplots(2,3,figsize=(12,9))
    axs[0, 0].scatter(gdata[:,0], gdata[:, 1], label='XY')
    axs[0, 0].set_xlim([-limit,limit])
    axs[0, 0].set_ylim([-limit,limit])
    axs[0, 0].set_aspect(1)

    axs[0, 1].scatter(gdata[:,1], gdata[:, 2], label='YZ')
    axs[0, 1].set_xlim([-limit,limit])
    axs[0, 1].set_ylim([-limit,limit])
    axs[0, 1].set_aspect(1)

    axs[0, 2].scatter(gdata[:,0], gdata[:, 2], label='XZ')
    axs[0, 2].set_xlim([-limit,limit])
    axs[0, 2].set_ylim([-limit,limit])
    axs[0, 2].set_aspect(1)

    axs[1, 0].scatter(gdata[:,0] - mag_offset[0], gdata[:, 1] - mag_offset[1], label='XY')
    axs[1, 0].set_xlim([-limit,limit])
    axs[1, 0].set_ylim([-limit,limit])
    axs[1, 0].set_aspect(1)

    axs[1, 1].scatter(gdata[:,1] - mag_offset[1], gdata[:, 2] - mag_offset[2], label='YZ')
    axs[1, 1].set_xlim([-limit,limit])
    axs[1, 1].set_ylim([-limit,limit])
    axs[1, 1].set_aspect(1)

    axs[1, 2].scatter(gdata[:,0] - mag_offset[0], gdata[:, 2] - mag_offset[2], label='XZ')
    axs[1, 2].set_xlim([-limit,limit])
    axs[1, 2].set_ylim([-limit,limit])
    axs[1, 2].set_aspect(1)

    print(mag_offset)
    plt.show()

