import urllib
import json
import subprocess as sp
import time
import numpy


import socket
import time
from math import pi

UDP_IP = '192.168.23.223'
UDP_PORT = 5078


def CreatePixel(red, green, blue):
  return [red, green, blue]

def Push(messages):
  assert type(messages) == list
  for message in messages:
    message = "".join(map(chr, message))
    sock = socket.socket(
      socket.AF_INET, # Internet
      socket.SOCK_DGRAM) # UDP
    bytes_sent = sock.sendto(message, (UDP_IP, UDP_PORT))

RANGE = pi

key = API-KEY
playlistId = "PLWPWDUIg1sHnNKsx8CTdfTfG3VBFYBGVL"
maxResults = 50

pItemsUrl = 'https://www.googleapis.com/youtube/v3/playlistItems'
params = {'key': key, 'playlistId': playlistId,
          'part': 'snippet', 'maxResults': 50}
url = '%s?%s' % (pItemsUrl, urllib.urlencode(params))
res = urllib.urlopen(url).read()
videos = []
data = json.loads(res)
for i in data['items']:
    tmp = {}
    tmp['title'] = i['snippet']['title']
    tmp['desc'] = i['snippet']['description']
    tmp['id'] = i['snippet']['resourceId']['videoId']
    videos.append(tmp)

videoIds = ','.join(i['id'] for i in videos)
videoUrl = 'https://www.googleapis.com/youtube/v3/videos'

params = {'key': key, 'id': videoIds,
          'part': 'snippet,contentDetails'}
url = '%s?%s' % (videoUrl, urllib.urlencode(params))
res = urllib.urlopen(url).read()
data = json.loads(res)

for video in videos:
    for i in data['items']:
        if i['id'] == video['id']:
            tmpDuration = i['contentDetails']['duration']
            # duration format: PT1M30S for a 01:30 video, PT30S for a 00:30 video

            # parse duration without regex

            tmpDuration = tmpDuration.strip('PT').strip('S')
            duration = ''
            if 'M' in tmpDuration:
                tmp = tmpDuration.split('M')
                duration = '%s:%s' % (tmp[0].zfill(2), tmp[1].zfill(2))
            else:
                duration = '00:%s' % tmpDuration.zfill(2)

            video['duration'] = duration
            print video['id']
            print video['duration']
            print video['title']

            getStream = sp.Popen(["youtube-dl", "-g", "http://www.youtube.com/watch?v=" + video['id']],
                                 stdout=sp.PIPE)
            streamNow, err = getStream.communicate()

            height = 64
            width = 96

            if streamNow != "":
                scale = 'scale=%d:%d' % (width, height)
                command = ["ffmpeg", "-re",
                           '-i', streamNow.strip(),
                           "-f", "alsa", "hw:0",
                           '-f', 'image2pipe',
                           '-pix_fmt', 'rgb24',
                           '-vf', scale,
                           '-fflags', 'nobuffer',
                           '-vcodec', 'rawvideo', '-']
                print command
                pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10 ** 8)
                print "Playback startet!"


                while True:
                    raw_image = pipe.stdout.read(width * height * 3)
                    image = numpy.fromstring(raw_image, dtype='uint8')
                    image = image.reshape((height, width, 3))
                    pipe.stdout.flush()


                    msg = [148, 16, 0, 0, 0]

                    for strip in xrange(32):
                        for i in xrange(192):
                            #image[0,0][]

                            if i < 64:
                                y=95-strip
                                x=i

                            if i >= 64 and i < 128:
                                y=63-strip
                                x=i - 64

                            if i >= 128:
                                y = 31 - strip
                                x = i - 128

                            red = image[x, y][0]
                            green = image[x, y][1]
                            blue = image[x, y][2]

                            msg += CreatePixel(red, green, blue)
                        if strip < 31:
                            msg += [strip + 1]
                    Push([msg])
                    time.sleep(0.015)



