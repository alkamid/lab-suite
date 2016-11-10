from instrument import Instrument
from time import sleep
import pyvisa as visa

class Lockin(Instrument):
    def __init__(self, address=None):
        self.identificator = 'lockin'
        super().__init__(address, self.identificator)

    def read(self, trial=0):
        try:
            reading = int(self.ask('MAG?'))
        except ValueError:
            sleep(0.01)
            reading = int(self.ask('MAG?'))
        except visa.errors.VisaIOError:
            print('-----------------timeout--------------------')
            if trial < 10:
                return self.read(trial+1)
            else:
                raise visa.errors.VisaIOError

        return reading

    def get_ref_freq(self):
        sleep(0.1)
        frq = float(self.ask('frq?'))/1000
        return frq

    def get_sensitivity(self):
        # We can ask the lock-in for its sensitivity but it will output a number 0-15.
        # Below is the table of sensitivities
        lockin_sensitivities = [100e-9,300e-9,1e-6,3e-6,10e-6,30e-6,300e-6,1e-3,3e-3,10e-3,10e-3,30e-3,100e-3,300e-3,1,3]
        sleep(0.1)
        index = int(self.ask('sen?'))
        return lockin_sensitivities[index]

    def get_timeconstant(self):
        lockin_tcs = [1e-3,3e-3,10e-3,30e-3,100e-3,300e-3,1,3,10,30,100,300,1e3,3e3]
        sleep(0.1)
        index = int(self.ask('tc?'))
        return lockin_tcs[index]
