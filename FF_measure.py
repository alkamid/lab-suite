from stage import Stage
from lockin import Lockin
from pulser import Pulser
from time import sleep, time
from datetime import datetime
import numpy as np

class FF():
    def __init__(self, stabilisation_time=None, queue=None, ax1_range=(0,10,1), ax2_range=(0,10,1), filename='test'):
        self.ax1_start = ax1_range[0]
        self.ax1_stop = ax1_range[1]
        self.ax1_step = ax1_range[2]
        self.ax2_start = ax2_range[0]
        self.ax2_stop = ax2_range[1]
        self.ax2_step = ax2_range[2]
        self.ax1 = Stage(axis=1)
        self.ax2 = Stage(axis=2)
        self.lockin = Lockin(address="GPIB0::2::INSTR")
        self.pulser = Pulser(address="GPIB0::6::INSTR")
        ax1_steps = int(abs(self.ax1_start-self.ax1_stop)/self.ax1_step+1)
        ax2_steps = int(abs(self.ax2_start-self.ax2_stop)/self.ax2_step+1)
        self.results = np.zeros((ax1_steps, ax2_steps, 3))
        self.elapsed_time = 0
        self.queue = queue

        self.filename = filename
        self.stop_measurement = False

        if stabilisation_time == None:
            self.stabilisation_time = self.lockin.get_timeconstant()*3
        else:
            self.stabilisation_time = stabilisation_time

    def write_parameters(self):
        with open(self.filename + '_info', 'w') as f:
            f.write('-----------------\n')
            f.write('PARAMETERS\n')
            f.write('date:\t{0}\n'.format(datetime.now()))
            f.write('lock-in_sensitivity:\t{0}\n'.format(self.lockin.get_sensitivity()))
            f.write('lock-in_tc:\t{0}\n'.format(self.lockin.get_timeconstant()))
            f.write('lock-in_freq:\t{0}\n'.format(self.lockin.get_ref_freq()))
            f.write('pulser_freq:\t{0}\n'.format(self.pulser.read_freq()))
            f.write('pulser_DC:\t{0}\n'.format(self.pulser.read_DC()))
            f.write('stabilisation_time:\t{0:.2f}\n'.format(self.stabilisation_time))
            f.write('-----------------\n')

    def write_into_array(self, ax1, ax2):
        reading = self.lockin.read()
        self.results[int(ax1),int(ax2)] = np.array((self.ax1.read_pos(), self.ax2.read_pos(), reading))

    def write_to_file(self):
        np.savetxt(self.filename, self.results[:,:,2])

    def write_sequentially(self):
        with open(self.filename + '_seq', 'w') as f:
            for i in range(self.results.shape[0]):
                for j in range(self.results.shape[1]):
                    f.write('{0}\t{1}\t{2}\n'.format(self.results[i,j,0], self.results[i,j,1], self.results[i,j,2]))

    def estimate_time(self, tic, toc, curr):
        self.elapsed_time += (toc-tic)
        num_steps = abs(self.ax1_start-self.ax1_stop)/self.ax1_step+1
        current_step = (curr-self.ax1_start)/self.ax1_step+1
        print(current_step)
        total_time = num_steps*self.elapsed_time/current_step
        time_left = total_time - self.elapsed_time
        print('Total time:{0}\nTime left:{1}'.format(total_time, time_left))
        if self.queue != None:
            self.queue.put('eta,{0},{1}'.format(int(total_time),int(self.elapsed_time)))

    def measure(self):
        self.ax1.initialise()
        self.ax2.initialise()

        self.write_parameters()

        oddeven = 0
        for i in np.linspace(self.ax1_start, self.ax1_stop, abs(self.ax1_start-self.ax1_stop)/self.ax1_step+1):
            ax2range = np.linspace(self.ax2_start, self.ax2_stop, abs(self.ax2_start-self.ax2_stop)/self.ax2_step+1)
            tic = time()
            if oddeven%2 == 0:
                reverse = 1
            else:
                reverse = -1
            for j in ax2range[::reverse]:
                self.ax1.move_to(i)
                self.ax2.move_to(j)
                sleep(self.stabilisation_time)
                print("Taking measurement at ax1={0}, ax2={1}".format(self.ax1.read_pos(), self.ax2.read_pos()))
                self.write_into_array(i, j)
                self.write_to_file()
                self.write_sequentially()
                if self.stop_measurement == True:
                    return 0
            oddeven+=1
            toc = time()
            self.estimate_time(tic, toc, i)
