import visa

rm = visa.ResourceManager()

class Instrument():
    def __init__(self, address=None, identificator=None):
        if address != None:
            self.instr = rm.open_resource(address)
        elif identificator != None:
            self.find_instrument(identificator)

    def find_instrument(self, instr_type):
        identificators = {'stage': 'ESP300', 'pulser': 'HEWLETT-PACKARD'}
        for i in range(20):
            self.instr = rm.open_resource('GPIB0::{0}::INSTR'.format(i))
            try: self.id = self.instr.query('*IDN?')
            except:
                continue
            if instr_type == 'lockin':
                if self.id[0] in ('+', '-') and len(self.id) == 7:
                    self.id = 'EG&G PARC 5210 lock-in amplifier'
                    return 0
            elif identificators[instr_type] in self.id:
                return 0

        print('Instrument not found!')
        return -1

    def ask(self, cmd):
        return self.instr.ask(cmd)
    def write(self, cmd):
        return self.instr.write(cmd)
