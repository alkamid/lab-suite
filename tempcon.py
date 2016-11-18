from instrument import Instrument
from time import sleep

class Tempcon(Instrument):
    def __init__(self, address=None):
        self.identificator = 'tempcon'
        super().__init__(address, self.identificator)

    def set_temp(self, temp, wait=True, tolerance=0.5, num_reads=5, reads_interval=2):
        """
        Params:
            tolerance (float): what is the tolerance for the target temperature in K
            num_reads (int): how many times the temperature needs to fall within tolerance
            reads_interval (float): how much time to wait between reads
        """
        tempcon.write('loop 1:setpt {0}'.format(temp))

        if wait == True:
            counter = 0
            while counter <= num_reads:
                if abs(temp - tempcon.ask('input? A')) < tolerance:
                    counter += 1
                else:
                    counter = 0
                sleep(read_interval)
            return 0
