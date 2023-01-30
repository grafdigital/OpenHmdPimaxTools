import hid
from time import sleep
from datetime import datetime
import math
import pygame
from pimax_common import decode_sample, decode_frame, BufferPointer

from collections import deque

def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)

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
    head_filter = deque(maxlen=20)
    lh = 0

    pygame.init()
    screen = pygame.display.set_mode([640,320])

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        data = h.read(BUFFER_SIZE, 1000)
        if len(data) > 0:
            if data[0] == 11:
                frame = decode_frame(data)
                #print(frame)

                screen.fill([0,0,0])

                a = [
                    frame['samples'][0]['accel'][0] * 0.0001, #X
                    frame['samples'][0]['accel'][1] * 0.0001, #Y
                    frame['samples'][0]['accel'][2] * 0.0001, #Z
                ]


                #a = [ -a[2], a[0], -a[1] ] # rotate X 90, Y 90
                #a = [ a[1], -a[2], -a[0] ] # rotate X 90, Y 90
                #a = [ -a[1], a[2], -a[0] ] # rotate X 90, Y 90

                norm = math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
                a[0] /= norm
                a[1] /= norm
                a[2] /= norm

                pygame.draw.rect(screen, [255,255,255], [0, 320/2-1, 640, 2])
                for xx in range(3):
                    v = a[xx] * 150
                    if v > 0:
                        pygame.draw.rect(screen, [0,0,255], [320 + xx * 50, 320/2-v, 30, v])
                    else:                            
                        pygame.draw.rect(screen, [0,0,255], [320 + xx * 50, 320/2, 30, -v])

                cal = [0.03150000000000003, 0.12444999999999998, 0.45130000000000003]
                d = [
                    frame['mag'][0] * 0.0001 - cal[0], #X
                    frame['mag'][1] * 0.0001 - cal[1], #Y
                    frame['mag'][2] * 0.0001 - cal[2], #Z
                ]
                #d = [ d[0], d[2], -d[1] ] # rotate X 90
                #d = [ d[1], -d[2], -d[0] ] # rotate X 90, Y 90
                d = [ d[1], d[2], d[0] ] # rotate Y 90, Z 90

                norm = math.sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2])
                d[0] /= norm
                d[1] /= norm
                d[2] /= norm

                pygame.draw.rect(screen, [255,255,255], [0, 320/2-1, 320, 2])
                for xx in range(3):
                    v = d[xx] * 150
                    if v > 0:
                        pygame.draw.rect(screen, [0,255,0], [100 + xx * 50, 320/2-v, 30, v])
                    else:
                        pygame.draw.rect(screen, [0,255,0], [100 + xx * 50, 320/2, 30, -v])
                
                #print(f'{d[0]:03.2f}, {d[1]:03.2f}, {d[2]:03.2f}')
                #continue

                pitch_rad = -math.asin(a[2])
                c = math.cos(pitch_rad)
                if c != 0:
                    roll_rad = math.asin(clamp(-a[0] / c, -1, 1))
                #print(f'{pitch_rad:03.2f}, {roll_rad:03.2f}')

                for xx, x in enumerate([pitch_rad, roll_rad]):
                    v = x * 150
                    if v > 0:
                        pygame.draw.rect(screen, [255,0,0], [500 + xx * 50, 320/2-v, 30, v])
                    else: 
                        pygame.draw.rect(screen, [255,0,0], [500 + xx * 50, 320/2, 30, -v])


                # get angle from 3 sensors accounting for gravity
                yaw_rad = math.atan2(
                    d[1] * math.cos(roll_rad) + d[2] * math.sin(roll_rad),

                    d[0] * math.cos(pitch_rad) +
                    d[1] * math.sin(pitch_rad) * math.sin(roll_rad) -
                    d[2] * math.sin(pitch_rad) * math.cos(roll_rad)
                )

                #yaw_rad = math.atan2(
                #    d[2] * math.sin(roll_rad) - d[1] * math.cos(roll_rad),
                #    d[0] * math.cos(pitch_rad) +
                #    d[1] * math.sin(pitch_rad) * math.sin(roll_rad) +
                #    d[2] * math.sin(pitch_rad) * math.cos(roll_rad)
                #)

                # get angle from 2 sensors
                yaw_rad = math.atan2(-d[1], d[0])

                # constraint to 360
                head = yaw_rad % (2 * math.pi)
                if head < 0:
                    head += 2.0 * math.pi;

                # convert rad to deg
                head *= 180 / math.pi

                head_filter.append(head)
                a = int(sum(head_filter) / len(head_filter))
                if a != lh:
                    print(a) 
                    lh = a
            else:
                print(f'Unknown Message: {data[0]:X}')

        now = datetime.now()
        if (now - keep_alive).total_seconds() > 3:
            h.send_feature_report(b'\x11\x00\x00\x0b\x10\x27')
            keep_alive = now

        pygame.display.update()

