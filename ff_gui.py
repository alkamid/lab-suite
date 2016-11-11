import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import numpy as np
import threading
import queue

from FF_measure import FF

class FFgui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.filename = tk.StringVar()
        self.grid()
        self.create_widgets()
        #self.create_plot()

    def updatefig(self, *args):
        try: data = np.loadtxt(self.filename.get())
        except ValueError:
            return self.image,

        self.image.set_data(data)
        return self.image,

    def create_plot(self):
        #http://stackoverflow.com/questions/33741403/using-figurecanvastkagg-in-two-tkinter-pages-with-python
        data = np.loadtxt(self.filename.get())
        fig = plt.figure()

        im = plt.imshow(data, cmap='viridis', interpolation='none')
        self.image = im

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.show()
        canvas.get_tk_widget().grid(column=4, row=3, rowspan=2, columnspan=2)
        self.canvas = canvas

        #http://stackoverflow.com/questions/12913854/displaying-matplotlib-navigation-toolbar-in-tkinter-via-grid
        toolbar_frame = tk.Frame(self)
        toolbar_frame.grid(row=5,column=4, columnspan=2, sticky='W')
        toolbar = NavigationToolbar2TkAgg(canvas, toolbar_frame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.ani = animation.FuncAnimation(fig, self.updatefig, interval=500, blit=True)


    def create_widgets(self):

        tk.Label(self, text="Axis 1:").grid(row=1, column=0)
        tk.Label(self, text="Axis 2:").grid(row=2, column=0)
        tk.Label(self, text="start:").grid(row=0, column=1)
        tk.Label(self, text="stop:").grid(row=0, column=2)
        tk.Label(self, text="step:").grid(row=0, column=3)

        #http://stackoverflow.com/questions/8959815/restricting-the-value-in-tkinter-entry-widget
        vcmd = (self.master.register(self.validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        inputs = (('ax1_start', 1, 1, 0), ('ax2_start', 2, 1, 0),
                ('ax1_stop', 1, 2, 10), ('ax2_stop', 2, 2, 10),
                ('ax1_step', 1, 3, 1), ('ax2_step', 2, 3, 1))

        self.inputs = {}
        for inp in inputs:
            self.inputs[inp[0]] = tk.Entry(self, validate = 'key', validatecommand = vcmd)
            self.inputs[inp[0]].insert('end', inp[3])
            self.inputs[inp[0]].grid(row=inp[1], column=inp[2])

        tk.Label(self, text='lock-in delay').grid(row=3, column=0)
        self.inputs['lockin_delay'] = tk.Entry(self, validate = 'key', validatecommand = vcmd)
        self.inputs['lockin_delay'].insert(0, 1500)
        self.inputs['lockin_delay'].grid(row=3, column=1)

        self.fileload = tk.Button(self, text='Browse', command=self.load_file)
        self.fileload.grid(column=4, row=0, sticky='W')

        self.file_entry = tk.Entry(self, textvariable=self.filename, width=50)
        self.file_entry.grid(column=5, row=0, sticky='W')


        self.b_start = tk.Button(self)
        self.b_start["text"] = "Start measurement"
        self.b_start["command"] = self.start_thread
        self.b_start.grid(column=0, row=4)

        self.stop = tk.Button(self, text="STOP measurement", command=self.stop_meas)
        self.stop.grid(column=0, row=5)

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.grid(column=0, row=6)

        self.int_val = tk.IntVar()
        self.prog_bar = ttk.Progressbar(
            self, orient="horizontal",
            length=200, mode="determinate"
            )
        self.prog_bar['variable'] = self.int_val

        self.prog_bar.grid(column=4, row=6, sticky='W')

        self.timeleft_text = tk.StringVar()
        self.timeleft_text.set('')
        self.timeleft = tk.Label(self, textvariable=self.timeleft_text)
        self.timeleft.grid(row=6, column=5, sticky='W')

    def load_file(self):
        fname = filedialog.asksaveasfilename()

        if fname:
            self.filename.set(fname)
            self.create_plot()

    def validate(self, action, index, value_if_allowed,
                       prior_value, text, validation_type, trigger_type, widget_name):
        try:
            float(value_if_allowed)
            return True
        except ValueError:
            if value_if_allowed == '':
                return True
            else:
                return False

    def start_thread(self):
        if self.filename.get() == '':
            messagebox.showerror('Error', 'You didn\'t choose a filename!')
            return -1

        #http://stackoverflow.com/questions/16745507/tkinter-how-to-use-threads-to-preventing-main-event-loop-from-freezing
        # create then start a secondary thread to run arbitrary()
        self.que = queue.Queue()
        param_values = {k: float(v.get()) for k, v in self.inputs.items()}
        self.f = FF(queue=self.que, filename=self.filename.get(), parameters=param_values)
        if self.check_lockin_delay() == True:
            self.b_start['state'] = 'disable'
            self.secondary_thread = threading.Thread(target=self.arbitrary, args=(self.f,))
            self.secondary_thread.start()
            # check the Queue in 50ms
            self.master.after(50, self.check_que)

    def check_lockin_delay(self):
        if self.f.recomm_delay > float(self.inputs['lockin_delay'].get()):
            if messagebox.askyesno('Lock-in delay', 'The lock-in delay ({0} ms) is less than 3*lock-in timeconstant ({1:.0f} ms). Do you want to continue?'
                                .format(self.inputs['lockin_delay'].get(), self.f.recomm_delay)):
                return True
            else:
                return False
        else:
            return True

    def check_que(self):
        while True:
            try: x = self.que.get_nowait()
            except queue.Empty:
                self.master.after(25, self.check_que)
                break
            else: # continue from the try suite
                if x == 'finished':
                    self.b_start['state'] = 'normal'
                    self.timeleft_text.set('Measurement finished!')
                    break
                elif x.startswith('eta'):
                    self.update_progressbar(x)

    def update_progressbar(self, params):
        vals = params.split(',')
        self.prog_bar['maximum'] = int(vals[1])
        self.int_val.set(vals[2])
        seconds_left = int(vals[1])-int(vals[2])
        m, s = divmod(seconds_left, 60)
        h, m = divmod(m, 60)
        self.timeleft_text.set('Time left: {0:02}:{1:02}:{2:02}'.format(h,m,s))

    def arbitrary(self, ff):
        ff.measure()

    def stop_meas(self):
        self.f.stop_measurement = True
        self.b_start['state'] = 'normal'

root = tk.Tk()
app = FFgui(master=root)
app.mainloop()
