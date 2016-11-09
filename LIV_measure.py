from oscilloscope import Oscilloscope
from pulser import Pulser
from lockin import Lockin
from time import sleep
import matplotlib.pyplot as plt
import numpy as np

class LIV():
    def __init__(self):
        self.voltage_start = 1
        self.voltage_max = 8
        self.current_max = 0.25
        self.voltage_step = 0.1

    def initialise(self):
        self.pulser = Pulser()
        self.scope = Oscilloscope(v_channel = 1, i_channel = 2)
        self.lockin = Lockin()

        self.stabilisation_time = lockin.get_timeconstant()*3

        self.pulser.voltage_off()
        sleep(2)
        self.scope.set_offsets()
        self.pulser.voltage_on()

    def measure(self):
        self.scope.reset_offsets()
        self.pulser.voltage_off()
        sleep(2)
        self.scope.set_offsets()
        self.pulser.voltage_on()

        pulser_v_limit = self.pulser.max_voltage(self.pulser.read_DC())

        with open(fname, 'w') as f:
            for v in np. np.arange(self.voltage_start, pulser_v_limit, self.voltage_step):
                sleep(self.stabilisation_time)
                volt = self.scope.get_value(scope.v_channel)
                curr = self.scope.get_value(scope.i_channel)
                sig = self.lockin.read()
                f.write('{0}\t{1}\t{2}'.format(curr, volt, sig))
                if (volt >= self.voltage_max) or (curr >= self.current_max):
                    break

        self.pulser.voltage_off()

def stabilise_temperature(tempcon, target):
    tolerance = 0.5 # we want the temperature to be +-0.5K from the target
    how_many_reads = 5 # 5 reads within the range before measuring
    reads_interval = 2 # 2s before consecutive reads

    tempcon.write('loop 1:setpt %d' % t)

    counter = 1
    while counter:
        if abs(target- tempcon.query_ascii_values('input? A')[0]) < tolerance:
            counter += 1
        else:
            counter = 1

        if counter == 1 + numReads:
            return 0
        time.sleep(1)


fig, ax1 = plt.subplots()
ax1.set_xlim([0, 0.2])
ax2 = ax1.twinx()
values_v = []
values_i = []
values_l = []
ln1, = ax1.plot([], color='green')
ln2, = ax2.plot([], color='red')
plt.ion()
plt.show()

with open(base_filename + '.dat', 'w') as output_file:
    for i in range(int(1/pulser_step),int(20/pulser_step)+1):
        voltage = i*pulser_step
        pulser.write(':voltage {0}v'.format(voltage))
        time.sleep(pulser_delay)
        scopevals = get_scope_values(scope, offsets)
        lockval = get_lockin_value(lockin, sens)
        print('{0}\t{1}\t{2}'.format(scopevals[1], scopevals[0], lockval))
        output_file.write('{0}\t{1}\t{2}'.format(scopevals[1], scopevals[0], lockval))

        values_v.append(scopevals[0])
        values_i.append(scopevals[1])
        values_l.append(lockval)

        ln1.set_xdata(values_i)
        ln1.set_ydata(values_v)
        ln2.set_xdata(values_i)
        ln2.set_ydata(values_l)

        ax1.relim()
        ax1.autoscale_view(True,True,True)
        ax2.relim()
        ax2.autoscale_view(True,True,True)
        #ax1.scatter(scopevals[1], scopevals[0])
        #ax2.scatter(scopevals[1], lockval, color='red')
        plt.pause(0.1)


pulser.write(':output off') # turn the pulser off

'''for t in temperatures:
    if stabilise_temperature(tempcon, t) == 0:
        filename = base_filename + '_{0}K.dat'.format(t)
    else
        return 1
'''
