from __future__ import print_function
import time
import pychromecast

name = 'Kitchen Speaker'
chromecasts = pychromecast.get_chromecasts()

cast = next(cc for cc in chromecasts if cc.device.friendly_name == name)
cast.wait()
print(cast.device)
print(cast.status)

mc = cast.media_controller
mc.play_media( 'http://192.168.0.23:8080/mic', 'audio/wav', stream_type="LIVE")
mc.block_until_active()

while(not mc.status.player_is_playing):
    print('.', end='', flush=True)
    time.sleep(0.2)

print('\n', mc.status)

while(mc.status.player_is_playing):
    print('\n', mc.status)
    #print('.', end='', flush=True)
    time.sleep(2)

