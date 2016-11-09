from instrument import Instrument
from time import sleep

class Stage(Instrument):
    def __init__(self, address=None, axis=1):
        self.identificator = 'stage'
        super().__init__(address, self.identificator)
        self.axis = axis
        self.last_position = None

    def initialise(self):
        self.write("MO")

    def write(self, cmd):
        newcmd = str(self.axis) + cmd
        self.instr.write(newcmd)

    def ask(self, cmd):
        newcmd = str(self.axis) + cmd
        result = self.instr.ask(newcmd)
        return result

    def stop(self):
        self.write('ST')

    def check_motor_status(self):
        try: status = int(self.ask('MD?'))
        except:
            return 1
        if status == 0:
            return 1
        else:
            return 0

    def move_to(self, new_pos, wait=True):
        if self.check_motor_status() == 1:
            self.stop()

        self.write("PA {0}".format(new_pos))
        if wait == True:
            while (self.check_motor_status() == 1):
                sleep(0.05)

    def read_pos(self):
        try:
            pos = float(self.ask('TP'))
            self.last_position = pos
            return pos
        except:
            print("Can't read the stage position!")
            return None
