"""
opuslib from:
https://github.com/OnBeep/opuslib
OpusCodec class modified from:
https://stackoverflow.com/questions/17728706/python-portaudio-opus-encoding-decoding
class provided from David Andersen:
k0rx@uiowa.edu
"""

from opuslib.api import constants as opus_constants
from opuslib.api import ctl as opus_ctl
from opuslib.api import decoder as opus_decoder
from opuslib.api import encoder as opus_encoder

class OpusCodec():
    def __init__(self, fec=0):
        self.chunk = 960#960#2880#960 # 20 ms at 48000
        self.channels = 1 # mono
        self.rate = 48000 # max rate (should this be reduced?)
        self.fec = fec # fec
        self.encoder = opus_encoder.create(self.rate,
                                           self.channels,
                                           opus_constants.APPLICATION_VOIP)
        opus_encoder.ctl(self.encoder, opus_ctl.set_vbr, 0) # disable vbr
        opus_encoder.ctl(self.encoder,
                         opus_ctl.set_packet_loss_perc, 2) # configure expected jitter loss
        if fec:
            print('FEC enabled: this may increase latency slightly.')
            print(' It will also (hopefully) compensate for any lost/delayed packets.')
            print(' It also seems to result in slightly mushier audio.')
            opus_encoder.ctl(self.encoder, opus_ctl.set_inband_fec, 1) # enable fec
        self.decoder = opus_decoder.create(self.rate,
                                           self.channels)
    def encode(self, data):
        return opus_encoder.encode(self.encoder,
                                   data,
                                   self.chunk,
                                   len(data))

    def decode(self, data):
        return opus_decoder.decode(self.decoder,
                                   data,
                                   len(data),
                                   self.chunk,
                                   self.fec,
                                   channels=self.channels)
