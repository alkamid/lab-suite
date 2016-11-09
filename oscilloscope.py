from instrument import Instrument

class Channel():
    def __init__(self, id, desc):
        self.id = id
        self.desc = desc
        self.offset = 0

    def set_offset(self, offset_value):
        self.offset = offset_value


class Oscilloscope(Instrument):
    def __init__(self, address=None, v_channel=None, i_channel=None)
        self.identificator = 'scope'
        super().__init__(address, self.identificator)
        self.v_channel = Channel(v_channel, 'voltage')
        self.i_channel = Channel(i_channel, 'current')

        self.get_value(self, channel):
            val = float(self.ask(':measurement:meas{0}:value?'.format(channel.id)) - channel.offset)

        self.set_offsets(self):
            self.v_channel.set_offset(float(self.get_value(self.v_channel.id)))
            self.i_channel.set_offset(float(self.get_value(self.i_channel.id)))

        self.reset_offsets(self):
            self.v_channel.offset = 0
            self.i_channel.offset = 0
