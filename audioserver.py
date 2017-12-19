from flask import Flask, Response
app = Flask(__name__)

import time, pyaudio, wave, struct

#
# Flask entry points
#
@app.route('/')
def hello_world():
    print('Got a request')
    return 'Hello, World!'

#
# Serve a WAV file
#
@app.route("/wav")
def streamwav():
    def generate():
        with open("audio/fastcar.wav", "rb") as fwav:
            packetSize = 1448                   # match size of ethernet payload
            blockSize = 48
            print('Serving audio in', packetSize, 'bytes per packet, in blocks of', blockSize)
            data = fwav.read(packetSize)
            packet = 0
            while data:
                yield data
                print('.', end='', flush=True)
                packet += 1
                if(packet % blockSize == 0):
                    print('\n')
                    #time.sleep(0.5)             # impose a buffering delay
                data = fwav.read(packetSize)
            print('\nFile finished')
    return Response(generate(), mimetype="audio/x-wav")

#
# Based on wave.py, this class allows construction of a wav header
#
WAVE_FORMAT_PCM = 0x0001

class wav_header:
    def __init__(self):
        self._nchannels = 0
        self._sampwidth = 0
        self._framerate = 0
        self._nframes   = 0
        self._datalength= 0

    def setnchannels(self, nchannels):
        if nchannels < 1:
            raise Error('bad # of channels')
        self._nchannels = nchannels

    def setsampwidth(self, sampwidth):
        if sampwidth < 1 or sampwidth > 4:
            raise Error('bad sample width')
        self._sampwidth = sampwidth

    def setframerate(self, framerate):
        if framerate <= 0:
            raise Error('bad frame rate')
        self._framerate = int(round(framerate))

    def setnframes(self, nframes):
        self._nframes = nframes

    def headerAsBytes(self, initlength):
        b = bytearray(b'RIFF')
        if not self._nframes:
            self._nframes = initlength // (self._nchannels * self._sampwidth)
        self._datalength = self._nframes * self._nchannels * self._sampwidth

        b.extend(struct.pack('<L4s4sLHHLLHH4s',
             36 + self._datalength, b'WAVE', b'fmt ', 16,
             WAVE_FORMAT_PCM, self._nchannels, self._framerate,
             self._nchannels * self._framerate * self._sampwidth,
             self._nchannels * self._sampwidth,
             self._sampwidth * 8, b'data'))
        b.extend(struct.pack('<L', self._datalength))

        return bytes(b)
#
# Stream live from microphone input
#
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
PACKETSIZE = 1448   # match size of ethernet payload
BLOCKSIZE = 16      # not really meaningful for live streams, but pretty-prints the output
MAXLEN = 2**29-1

@app.route("/mic")
def streamlive():

    def generate():
        # Create a dummy RIFF / WAV header for the live stream
        w = wav_header()
        w.setnchannels(CHANNELS)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.setnframes(MAXLEN)

        b = w.headerAsBytes(MAXLEN)
        yield b

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=PACKETSIZE)
        flush = 128
        print('Flushing input', flush, 'packets')
        while flush:
            data = stream.read(PACKETSIZE)
            print('.', end='', flush=True)
            flush -= 1
        print('\n')

        packet = 0
        starve = 64
        print('Serving audio in', PACKETSIZE, 'bytes per packet - with starvation', starve)
        while True:
            data = stream.read(PACKETSIZE)
            yield data
            print('.', end='', flush=True)
            packet += 1
            if(packet % BLOCKSIZE == 0):
                if starve:
                    starve -= 1
                    print('\nPacket ', packet, 'starving one')
                    data = stream.read(PACKETSIZE)
                else:
                    print('\nPacket ', packet)

        print('\nInput stream closed')
    return Response(generate(), mimetype="audio/x-wav")


#
# Start the app
if __name__ == "__main__":
    app.run(debug=True, port=8080, host='0.0.0.0')