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
        self.master.title('Far-field measurement suite v0.9')
        self.filename = tk.StringVar()
        self.grid()
        self.create_widgets_left()
        self.create_widgets_right()
        self.create_empty_plot()

    def updatefig(self, *args):
        try: data = np.loadtxt(self.filename.get())
        except ValueError:
            return self.image,

        self.image.set_data(data)
        #also update the colorbar
        #http://stackoverflow.com/questions/39472017/how-to-animate-the-colorbar-in-matplotlib
        vmin = np.min(data)
        vmax = np.max(data)
        #self.cbar.update_normal()
        self.image.set_clim(vmin, vmax)
        return self.image,

    def create_empty_plot(self):
        data = np.zeros((5,5))
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.image = self.ax.imshow(data, cmap='viridis')

        canvas = FigureCanvasTkAgg(self.fig, self.right_panel)
        canvas.show()
        canvas.get_tk_widget().grid(column=4, row=3, rowspan=2, columnspan=2)
        self.canvas = canvas

    def create_plot(self):
        #http://stackoverflow.com/questions/33741403/using-figurecanvastkagg-in-two-tkinter-pages-with-python
        data = np.loadtxt(self.filename.get())
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        self.image = self.ax.imshow(data, cmap='viridis', interpolation='none')
        self.cb = self.fig.colorbar(self.image)

        canvas = FigureCanvasTkAgg(self.fig, self.right_panel)
        canvas.show()
        canvas.get_tk_widget().grid(column=4, row=3, rowspan=2, columnspan=2)
        self.canvas = canvas

        #http://stackoverflow.com/questions/12913854/displaying-matplotlib-navigation-toolbar-in-tkinter-via-grid
        self.toolbar_frame = tk.Frame(self.right_panel)
        self.toolbar_frame.grid(row=5,column=4, columnspan=2, sticky='W')
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbar_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.ani = animation.FuncAnimation(self.fig, self.updatefig, interval=500, blit=True)

    def create_widgets_left(self):

        self.left_panel = tk.Frame(self)
        self.left_panel.grid(row=0, column=0, sticky='W')

        self.fileload = tk.Button(self.left_panel, text='Choose file name', command=self.load_file)
        self.fileload.grid(column=0, row=0, sticky='W')

        self.file_entry = tk.Entry(self.left_panel, textvariable=self.filename, width=50)
        self.file_entry.grid(column=1, row=0, columnspan = 3, sticky='W')

        tk.Label(self.left_panel, text="Axis 1:").grid(row=2, column=0)
        tk.Label(self.left_panel, text="Axis 2:").grid(row=3, column=0)
        tk.Label(self.left_panel, text="start:").grid(row=1, column=1)
        tk.Label(self.left_panel, text="stop:").grid(row=1, column=2)
        tk.Label(self.left_panel, text="step:").grid(row=1, column=3)

        #http://stackoverflow.com/questions/8959815/restricting-the-value-in-tkinter-entry-widget
        vcmd = (self.master.register(self.validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        inputs = (('ax1_start', 2, 1, 0), ('ax2_start', 3, 1, 0),
                ('ax1_stop', 2, 2, 10), ('ax2_stop', 3, 2, 10),
                ('ax1_step', 2, 3, 1), ('ax2_step', 3, 3, 1))

        self.inputs = {}
        for inp in inputs:
            self.inputs[inp[0]] = tk.Entry(self.left_panel, validate = 'key', validatecommand = vcmd)
            self.inputs[inp[0]].insert('end', inp[3])
            self.inputs[inp[0]].grid(row=inp[1], column=inp[2])

        tk.Label(self.left_panel, text='lock-in delay').grid(row=4, column=0)
        self.inputs['lockin_delay'] = tk.Entry(self.left_panel, validate = 'key', validatecommand = vcmd)
        self.inputs['lockin_delay'].insert(0, 1500)
        self.inputs['lockin_delay'].grid(row=4, column=1, pady=20)


        self.b_start = tk.Button(self.left_panel)
        self.b_start["text"] = "START measurement"
        self.b_start["command"] = self.start_thread
        self.b_start.grid(column=0, row=6, sticky='W', pady=3)

        self.stop = tk.Button(self.left_panel, text="STOP measurement", command=self.stop_meas)
        self.stop.grid(column=1, row=6, sticky='E', pady=3)

        tk.Label(self.left_panel, text="Lock-in: ").grid(row=7, column=0)
        tk.Label(self.left_panel, text="Pulser: ").grid(row=8, column=0)
        tk.Label(self.left_panel, text="Stages: ").grid(row=9, column=0)

        '''self.quit = tk.Button(self.left_panel, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.grid(column=0, row=8)'''

    def create_widgets_right(self):
        self.right_panel = tk.Frame()
        self.right_panel.grid(row=0, column=1)

        self.int_val = tk.IntVar()
        self.prog_bar = ttk.Progressbar(
            self.right_panel, orient="horizontal",
            length=200, mode="determinate"
            )
        self.prog_bar['variable'] = self.int_val

        self.prog_bar.grid(column=4, row=6, sticky='W')

        self.timeleft_text = tk.StringVar()
        self.timeleft_text.set('')
        self.timeleft = tk.Label(self.right_panel, textvariable=self.timeleft_text)
        self.timeleft.grid(row=6, column=5, sticky='W')

    def load_file(self):
        fname = filedialog.asksaveasfilename()

        if fname:
            self.filename.set(fname)

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
        # create then start a secondary thread to run start_ff()
        self.que = queue.Queue()
        param_values = {k: float(v.get()) for k, v in self.inputs.items()}
        self.f = FF(queue=self.que, filename=self.filename.get(), parameters=param_values)
        if self.check_lockin_delay() == True:
            self.b_start['state'] = 'disable'
            self.secondary_thread = threading.Thread(target=self.start_ff, args=(self.f,))
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
                elif x == 'write_started':
                    self.create_plot()
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

    def start_ff(self, ff):
        ff.measure()

    def stop_meas(self):
        self.f.stop_measurement = True
        self.b_start['state'] = 'normal'

root = tk.Tk()
app = FFgui(master=root)
app.mainloop()
