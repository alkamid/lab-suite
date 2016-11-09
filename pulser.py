from instrument import Instrument

class Pulser(Instrument):
    def __init__(self, address=None):
        self.identificator = 'pulser'
        super().__init__(address, self.identificator)

    def initialise(self):
        self.set_gated_trigger()
        self.write(':HOLD VOLTAGE')

    def set_gated_trigger(self):
        self.write(':TRIGGER:SOURCE EXTERNAL')
        self.write(':TRIGGER:SENSE LEVEL')
        self.write(':TRIGGER:SLOPE POSITIVE')

    def max_voltage(self, dc):
        #Max voltage depends on the duty cycle. See Fig. 6-1 in the manual.
        if dc < 15:
            max_v = 50
        elif dc < 36.9:
            max_v = 50-(dc-15)
        else:
            max_v = 28.1-(dc-36.9)*(28.1-20)/(100-36.9)

        return round(max_v, 1)

    def voltage_off(self):
        self.write(':output off')
    def voltage_onn(self):
        self.write(':output on')

    def read_DC(self):
        return float(self.ask(':PULSE:DCYCLE?'))
    def set_DC(self, dc):
        self.write(':PULSE:DCYCLE {0:.1f}PCT'.format(dc))

    def read_freq(self):
        return float(self.ask(':FREQ?'))
    def set_freq(self, freq):
        self.write(':FREQ {0:.1f}'.format(freq))

    def read_voltage(self):
        return float(self.ask(':VOLTAGE?'))
    def set_voltage(self, voltage):
        self.write(':VOLTAGE {0:.1f}V'.format(voltage))
