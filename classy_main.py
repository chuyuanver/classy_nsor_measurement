import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from nidaqmx.task import Task
from nidaqmx import constants
import numpy as np
from numpy import pi
from nmr_pulses import pulse_interpreter
import matplotlib as mpl
mpl.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import json

SMALL_FONT = ('Helvetica', 12)

BIG_FONT = ('Helvetica', 16)
parameter_file = r'C:\Users\Hilty\Desktop\python\nsor_measurement\NSOR_measurement\parameter.json'

def read_parameter(parameter_file):
    with open(parameter_file, 'r') as f:
        parameter_raw = f.read()
    parameters = json.loads(parameter_raw)
    return parameters

def save_parameter(parameter_file, **kwargs):
    parameters = read_parameter(parameter_file)
    with open(parameter_file,'w') as f:
        for key,val in kwargs.items():
            parameters[key] = val
        json.dump(parameters, f, indent = 2)

def zero_pad_sig(np_array, pad_power):
    x = np.ceil(np.log2(len(np_array)))
    n = 2**(pad_power-1)
    l = int(2**x*n)
    time_sig = np.pad(np_array,(0,l-len(np_array)),'constant')
    return np.abs(np.fft.rfft(time_sig,norm = "ortho"))

def time2freq(time_data, pad_power):
    x = np.ceil(np.log2(len(time_data)))
    n = 2**(pad_power-1)
    l = 2**x*n
    dt = time_data[1]-time_data[0]
    f_max =1/(2*dt)
    return np.linspace(0, f_max, int(l/2)+1)

class CirculationNsor(tk.Tk):
    def __init__(self,  *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default = r"C:\Users\Hilty\Desktop\python\nsor_measurement\NSOR_measurement\favicon.ico")
        tk.Tk.wm_title(self,"NSOR")
        self.geometry('1440x768')
        container = tk.Frame(self)
        container.pack()
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        self.frames = {}
        for F in (NaviPage, StatMeasPage, InjMeasPage, DataAnalyPage, SetupPage, StatMeasMoniPage):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = 'nswe')

        self.show_frame(NaviPage)

    def show_frame(self, ctrl):
        frame = self.frames[ctrl]
        frame.tkraise()


class NaviPage(tk.Frame):
    def __init__(self, parent, ctrl):
        tk.Frame.__init__(self,parent)

        button_1 = ttk.Button(self, text = "Static Measurement", command = lambda: ctrl.show_frame(StatMeasPage))


        button_2 = ttk.Button(self, text = "Injection Measurement", command = lambda: ctrl.show_frame(InjMeasPage))


        button_3 = ttk.Button(self, text = "Data Analysis", command = lambda: ctrl.show_frame(DataAnalyPage))

        button_1.grid(row = 0, column = 0, sticky = 'WE')
        button_2.grid(row = 1, column = 0)
        button_3.grid(row = 2, column = 0)

class StatMeasPage(tk.Frame):
    def __init__(self, parent, ctrl):
        tk.Frame.__init__(self,parent)

        parameters = read_parameter(parameter_file)

        file_path_entry = ttk.Entry(self, font = SMALL_FONT)

        file_path_entry.insert(0, parameters["file_path"])
        file_name_entry = ttk.Entry(self, font = SMALL_FONT)
        file_path_label = ttk.Label(self,text = 'File Path:', font = SMALL_FONT)
        file_name_label = ttk.Label(self,text = 'File Name:', font = SMALL_FONT)
        file_name_entry.insert(0, parameters["file_name"])

        pulse_label = ttk.Label(self,text = 'Pulse:', font = SMALL_FONT)
        pulse_entry = ttk.Entry(self, font = SMALL_FONT)
        pulse_entry.insert(0, parameters["pulse_file"])

        file_path_entry.grid(row = 0, column = 1, ipadx = 160, sticky = "W")
        file_path_label.grid(row = 0, column = 0, sticky = "W")
        file_name_entry.grid(row = 1, column = 1, sticky = "W")
        file_name_label.grid(row = 1, column = 0, sticky = "W")
        pulse_label.grid(row = 2, column = 0, sticky = "W")
        pulse_entry.grid(row = 2, column = 1, ipadx = 200, sticky = "W")

        button_sp = ttk.Button(self, text = "Save Parameters",
                                    command = lambda: save_parameter(parameter_file,
                                    **{"file_path": file_path_entry.get(),
                                    "file_name": file_name_entry.get(),
                                    "pulse_file": pulse_entry.get()}))
        button_sp.grid(row = 3, column = 0)

        page_frame = tk.Frame(self)
        button_Navi = ttk.Button(page_frame, text = "Navigation -->", command = lambda: ctrl.show_frame(NaviPage))
        label_1 = ttk.Label(page_frame, text = "Static Measurement -->")
        button_1 = ttk.Button(page_frame, text = "Basic setup -->", command = lambda: ctrl.show_frame(SetupPage))
        button_2 = ttk.Button(page_frame, text = 'Start Experiment -->', command = lambda: ctrl.show_frame(StatMeasMoniPage))

        page_frame.grid(row = 4, column = 0, columnspan = 2)
        button_Navi.grid(row = 0, column = 0)
        label_1.grid(row = 0, column = 1)
        button_1.grid(row = 0, column = 2)
        button_2.grid(row = 0, column = 3)


class InjMeasPage(tk.Frame):
    def __init__(self, parent, ctrl):
        tk.Frame.__init__(self,parent)

        page_frame = tk.Frame(self)
        button_Navi = ttk.Button(page_frame, text = "Navigation -->", command = lambda: ctrl.show_frame(NaviPage))
        label_1 = ttk.Label(page_frame, text = "Injection Measurement -->")


        page_frame.grid(row = 3, column = 0, columnspan = 2, sticky = 's')
        button_Navi.grid(row = 0, column = 0)
        label_1.grid(row = 0, column = 1)

class DataAnalyPage(tk.Frame):
    def __init__(self, parent, ctrl):
        tk.Frame.__init__(self,parent)

        page_frame = tk.Frame(self)
        button_Navi = ttk.Button(page_frame, text = "Navigation -->", command = lambda: ctrl.show_frame(NaviPage))
        label_1 = ttk.Label(page_frame, text = "Data Analysis -->")

        page_frame.grid(row = 3, column = 0, columnspan = 2, sticky = 's')
        button_Navi.grid(row = 0, column = 0)
        label_1.grid(row = 0, column = 1)


class SetupPage(tk.Frame):
    def __init__(self, parent, ctrl):
        tk.Frame.__init__(self,parent)

        parameters = read_parameter(parameter_file)

        samp_rate_label = ttk.Label(self, text = 'Sampling rate (MS/s):', font = SMALL_FONT)
        samp_rate_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        samp_rate_entry.insert(0, parameters["samp_rate"])

        iteration_label = ttk.Label(self,text = 'Iteration:', font = SMALL_FONT)
        iteration_entry = ttk.Entry(self, font = SMALL_FONT, width = 3)
        iteration_entry.insert(0,parameters["iteration"])

        avg_label = ttk.Label(self,text = 'Average:', font = SMALL_FONT)
        avg_entry = ttk.Entry(self, font = SMALL_FONT, width = 3)
        avg_entry.insert(0,parameters["average"])

        pulse_channel_label = ttk.Label(self,text = 'Pulse Channel:', font = SMALL_FONT)
        pulse_channel_entry = ttk.Entry(self, font = SMALL_FONT, width = 8)
        pulse_channel_entry.insert(0,parameters["pulse_channel"])

        nmr_channel_label = ttk.Label(self,text = 'NMR Channel:', font = SMALL_FONT)
        nmr_channel_entry = ttk.Entry(self, font = SMALL_FONT, width = 8)
        nmr_channel_entry.insert(0,parameters["nmr_channel"])

        nsor_channel_label = ttk.Label(self,text = 'NSOR Channel:', font = SMALL_FONT)
        nsor_channel_entry = ttk.Entry(self, font = SMALL_FONT, width = 8)
        nsor_channel_entry.insert(0,parameters["nsor_channel"])

        laser_intensity_channel_label = ttk.Label(self,text = 'Laser Intensity Channel:', font = SMALL_FONT)
        laser_intensity_channel_entry = ttk.Entry(self, font = SMALL_FONT, width = 8)
        laser_intensity_channel_entry.insert(0,parameters["laser_intensity_channel"])

        samp_rate_label.grid(row = 0, column = 0, sticky = "W")
        samp_rate_entry.grid(row = 0, column = 1, sticky = "W")
        iteration_label.grid(row = 0, column = 2, sticky = "W")
        iteration_entry.grid(row = 0, column = 3, sticky = "W")
        avg_label.grid(row = 0, column = 4, sticky = "W")
        avg_entry.grid(row = 0, column = 5, sticky = "W")
        pulse_channel_label.grid(row = 1, column = 0, sticky = "W")
        pulse_channel_entry.grid(row = 1, column = 1, sticky = "W")
        nmr_channel_label.grid(row = 1, column = 2, sticky = "W")
        nmr_channel_entry.grid(row = 1, column = 3, sticky = "W")
        nsor_channel_label.grid(row = 2, column = 0, sticky = "W")
        nsor_channel_entry.grid(row = 2, column = 1, sticky = "W")
        laser_intensity_channel_label.grid(row = 2, column = 2, sticky = "W")
        laser_intensity_channel_entry.grid(row = 2, column = 3, sticky = "W")

        button_sp = ttk.Button(self, text = "Save Parameters",
                                     command = lambda: save_parameter(parameter_file,
                                     **{"samp_rate": samp_rate_entry.get(),
                                    "iteration": iteration_entry.get(),
                                    "average": avg_entry.get(),
                                    "pulse_channel": pulse_channel_entry.get(),
                                    "nmr_channel": nmr_channel_entry.get(),
                                    "nsor_channel": nsor_channel_entry.get(),
                                    "laser_intensity_channel": laser_intensity_channel_entry.get()}))

        button_sp.grid(row = 3, column = 0)

        page_frame = tk.Frame(self)
        button_Navi = ttk.Button(page_frame, text = "Navigation -->", command = lambda: ctrl.show_frame(NaviPage))
        button_1 = ttk.Button(page_frame, text = "Static Measurement -->", command = lambda: ctrl.show_frame(StatMeasPage))
        label_1 = ttk.Label(page_frame, text = "Basic setup -->")
        button_2 = ttk.Button(page_frame, text = 'Start Experiment -->', command = lambda: ctrl.show_frame(StatMeasMoniPage))

        page_frame.grid(row = 4, column = 0, columnspan = 6, sticky = 's')
        button_Navi.grid(row = 0, column = 0)
        button_1.grid(row = 0, column = 1)
        label_1.grid(row = 0, column = 2)
        button_2.grid(row = 0, column = 3)

class StatMeasMoniPage(tk.Frame):
    def __init__(self, parent, ctrl):
        tk.Frame.__init__(self,parent)
        run_button = ttk.Button(self, text = 'Start Acquisition', command = lambda: self.start_acquistion())

        self.current_iter_label = ttk.Label(self, text = 'Current Iteration: 0')
        self.current_avg_label = ttk.Label(self, text = 'Current Average: 0')

        '''
        figures configuration
        '''
        signal_figures = Figure(figsize = (14,6), dpi = 100, tight_layout=True)
        self.nmr_time_ax  = signal_figures.add_subplot(221)
        self.nmr_freq_ax = signal_figures.add_subplot(222)

        self.nsor_time_ax = signal_figures.add_subplot(223, sharex = self.nmr_time_ax)
        self.nsor_freq_ax = signal_figures.add_subplot(224, sharex = self.nmr_freq_ax)

        self.figs_canvas = FigureCanvasTkAgg(signal_figures ,master = self)
        self.figs_canvas.show()
        tool_frame = tk.Frame(self)
        toolbar = NavigationToolbar2TkAgg(self.figs_canvas, tool_frame)
        toolbar.update()
        self.avg_intensity_label =  ttk.Label(self, text = 'Laser Intensity: 0', font = SMALL_FONT)
        '''
        axis limit setup
        '''
        self.var_tx = tk.IntVar()
        self.var_ty = tk.IntVar(value = 1)
        self.var_fx = tk.IntVar()
        self.var_fy = tk.IntVar(value = 1)
        auto_scale_check_tx = ttk.Checkbutton(self, text = 'Time auto scale x', variable = self.var_tx)
        auto_scale_check_ty = ttk.Checkbutton(self, text = 'Time auto scale y', variable = self.var_ty)
        auto_scale_check_fx = ttk.Checkbutton(self, text = 'Freq auto scale x', variable = self.var_fx)
        auto_scale_check_fy = ttk.Checkbutton(self, text = 'Freq auto scale y', variable = self.var_fy)
        txlim_label = ttk.Label(self, text = 'Time x limit:', font = SMALL_FONT)
        tylim_label = ttk.Label(self, text = 'Time y limit:', font = SMALL_FONT)
        fxlim_label = ttk.Label(self, text = 'Freq x limit:', font = SMALL_FONT)
        fylim_label = ttk.Label(self, text = 'Freq y limit:', font = SMALL_FONT)
        self.txliml_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        self.txliml_entry.insert(0,'0')
        self.txlimh_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        self.txlimh_entry.insert(0,'0.6')
        self.tyliml_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        self.tyliml_entry.insert(0,'-1')
        self.tylimh_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        self.tylimh_entry.insert(0,'1')
        self.fxliml_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        self.fxliml_entry.insert(0,'31100')
        self.fxlimh_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        self.fxlimh_entry.insert(0,'31300')
        self.fyliml_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        self.fyliml_entry.insert(0,'0')
        self.fylimh_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        self.fylimh_entry.insert(0,'1')

        '''
        cursor used for calculation
        '''
        time_cursor_label = ttk.Label(self, text = 'Time cursor:', font = SMALL_FONT)
        freq_cursor_label = ttk.Label(self, text = 'Freq cursor:', font = SMALL_FONT)
        self.tcl_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        self.tcl_entry.insert(0,'0')
        self.tch_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        self.tch_entry.insert(0,'1')
        self.fcl_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        self.fcl_entry.insert(0,'31150')
        self.fch_entry = ttk.Entry(self, font = SMALL_FONT, width = 5)
        self.fch_entry.insert(0,'31250')

        '''
        grid things
        '''
        self.figs_canvas.get_tk_widget().grid(row = 0,column = 0, columnspan = 12, sticky = 'NEWS')
        self.figs_canvas._tkcanvas.grid(row=0, column=0, columnspan = 12, sticky = 'NEWS')
        auto_scale_check_tx.grid(row = 1, column = 0, columnspan = 3, sticky = 'W')
        auto_scale_check_ty.grid(row = 1, column = 3, columnspan = 3, sticky = 'W')
        auto_scale_check_fx.grid(row = 1, column = 6, columnspan = 3, sticky = 'W')
        auto_scale_check_fy.grid(row = 1, column = 9, columnspan = 3, sticky = 'W')
        txlim_label.grid(row = 2, column = 0, sticky = 'W')
        self.txliml_entry.grid(row = 2, column = 1, sticky = 'W')
        self.txlimh_entry.grid(row = 2, column = 2, sticky = 'W')
        tylim_label.grid(row = 2, column = 3, sticky = 'W')
        self.tyliml_entry.grid(row = 2, column = 4, sticky = 'W')
        self.tylimh_entry.grid(row = 2, column = 5, sticky = 'W')
        fxlim_label.grid(row = 2, column = 6, sticky = 'W')
        self.fxliml_entry.grid(row = 2, column = 7, sticky = 'W')
        self.fxlimh_entry.grid(row = 2, column = 8, sticky = 'W')
        fylim_label.grid(row = 2, column = 9, sticky = 'W')
        self.fyliml_entry.grid(row = 2, column = 10, sticky = 'W')
        self.fylimh_entry.grid(row = 2, column = 11, sticky = 'W')
        time_cursor_label.grid(row = 3, column = 0, sticky = 'W')
        self.tcl_entry.grid(row = 3, column = 1, sticky = 'W')
        self.tch_entry.grid(row = 3, column = 2, sticky = 'W')
        freq_cursor_label.grid(row = 3, column = 6, sticky = 'W')
        self.fcl_entry.grid(row = 3, column = 7, sticky = 'W')
        self.fch_entry.grid(row = 3, column = 8, sticky = 'W')
        self.avg_intensity_label.grid(row = 4, column = 0, columnspan = 2, sticky = 'W')
        self.current_iter_label.grid(row = 4, column = 3, columnspan = 2, sticky = 'W')
        self.current_avg_label.grid(row = 4, column = 5, columnspan = 2, sticky = 'W')
        run_button.grid(row = 5, column = 0)

        '''
        page navigation
        '''
        page_frame = tk.Frame(self)
        button_Navi = ttk.Button(page_frame, text = "Navigation -->", command = lambda: ctrl.show_frame(NaviPage))
        button_1 = ttk.Button(page_frame, text = "Static Measurement -->", command = lambda: ctrl.show_frame(StatMeasPage))
        button_2 = ttk.Button(page_frame, text = "Basic setup -->", command = lambda: ctrl.show_frame(SetupPage))
        label_1 = ttk.Label(page_frame, text = 'Start Experiment -->')

        page_frame.grid(row = 5, column = 0, columnspan = 12)
        button_Navi.grid(row = 0, column = 0)
        button_1.grid(row = 0, column = 1)
        button_2.grid(row = 0, column = 2)
        label_1.grid(row = 0, column = 3)

    def start_acquistion(self):

        parameters = read_parameter(parameter_file)
        '''
        set necessary constants
        '''
        samp_rate = int(float(parameters['samp_rate'])*1000000)
        iteration = int(parameters['iteration'])
        average = int(parameters['average'])
        pulse_chan = parameters['pulse_channel']
        nmr_chan = parameters['nmr_channel']
        nsor_chan = parameters['nsor_channel']
        laser_intensity_chan = parameters['laser_intensity_channel']
        pulse_file_path = parameters['pulse_file']
        file_path = parameters['file_path']
        file_name = parameters['file_name']

        pulse_data = pulse_interpreter(pulse_file_path, samp_rate, iteration)
        samp_num = len(pulse_data)

        '''
        configure the ao/ai tasks
        '''
        for current_iter in range(iteration):
            # note: displayed iteration starts with index of 1 while the iteration used in program starts with index of 0
            '''
            run, display and stored files
            '''
            self.current_iter_label.config(text = f'Current Iteration: {current_iter+1}')

            with Task('signal_task') as sig_task, Task('pulse_task') as pulse_task:
                for sig_chan in [nmr_chan, nsor_chan, laser_intensity_chan]:
                    sig_task.ai_channels.add_ai_voltage_chan(physical_channel = sig_chan,
                            terminal_config = constants.TerminalConfiguration.DIFFERENTIAL)
                pulse_task.ao_channels.add_ao_voltage_chan(pulse_chan)
                pulse_task.timing.cfg_samp_clk_timing(rate =samp_rate,
                                samps_per_chan = samp_num,
                                sample_mode=constants.AcquisitionType.FINITE)
                sig_task.timing.cfg_samp_clk_timing(rate = samp_rate,
                             source = '/Dev1/ao/SampleClock',
                             samps_per_chan = samp_num,
                             sample_mode=constants.AcquisitionType.FINITE)
                pulse_task.write(pulse_data)
                time_data = np.linspace(0, (samp_num/samp_rate), samp_num)
                time_data = np.reshape(time_data,(1,samp_num))
                sig_data = np.zeros((3,samp_num))
                for current_avg in range(average):
                    self.current_avg_label.config(text = f'Current Iteration: {current_avg+1}')

                    sig_task.start()
                    pulse_task.start()
                    sig_task.wait_until_done()
                    pulse_task.wait_until_done()
                    sig_data =(current_avg*sig_data + np.array(sig_task.read(number_of_samples_per_channel  = samp_num)))/(current_avg+1)
                    sig_task.stop()
                    pulse_task.stop()

                    np.save(file_path+'\\'+file_name+str(current_iter), np.concatenate((time_data, sig_data)))
                    '''
                    plot the data
                    '''
                    tcl_v = float(self.tcl_entry.get())
                    tcl_i = np.argmin(np.abs(time_data-tcl_v))
                    tch_v = float(self.tch_entry.get())
                    tch_i = np.argmin(np.abs(time_data-tch_v))

                    nmr_freq_sig = zero_pad_sig(sig_data[0,tcl_i:tch_i], 1)
                    nsor_freq_sig = zero_pad_sig(sig_data[1,tcl_i:tch_i], 1)
                    freq_axis = time2freq(time_data[0,tcl_i:tch_i],1)

                    self.nmr_time_ax.clear()
                    self.nmr_time_ax.plot(time_data[0,:],sig_data[0,:])
                    self.nmr_freq_ax.clear()
                    self.nmr_freq_ax.plot(freq_axis,nmr_freq_sig)
                    self.nsor_time_ax.clear()
                    self.nsor_time_ax.plot(time_data[0,:],sig_data[1,:])
                    self.nsor_freq_ax.clear()
                    self.nsor_freq_ax.plot(freq_axis,nsor_freq_sig)

                    '''
                    set axis limit
                    '''
                    txlim = (float(self.txliml_entry.get()),float(self.txlimh_entry.get()))
                    tylim = (float(self.tyliml_entry.get()),float(self.tylimh_entry.get()))
                    fxlim = (float(self.fxliml_entry.get()),float(self.fxlimh_entry.get()))
                    fylim = (float(self.fyliml_entry.get()),float(self.fylimh_entry.get()))
                    self.nmr_time_ax.set_xlim(txlim)
                    self.nmr_time_ax.set_ylim(tylim)
                    self.nmr_freq_ax.set_xlim(fxlim)
                    self.nmr_freq_ax.set_ylim(fylim)
                    if self.var_tx.get():
                        self.nmr_time_ax.autoscale(axis = 'x')
                    if self.var_ty.get():
                        self.nmr_time_ax.autoscale(axis = 'y')
                    if self.var_fx.get():
                        self.nmr_freq_ax.autoscale(axis = 'x')
                    if self.var_fy.get():
                        self.nmr_freq_ax.autoscale(axis = 'y')

                    self.nmr_time_ax.axvline(float(self.tcl_entry.get()), c = 'red')
                    self.nmr_time_ax.axvline(float(self.tch_entry.get()), c = 'red')
                    self.nmr_freq_ax.axvline(float(self.fcl_entry.get()), c = 'red')
                    self.nmr_freq_ax.axvline(float(self.fch_entry.get()), c = 'red')

                    self.figs_canvas.draw()
                    self.avg_intensity_label.configure(text = f'Laser Intensity: {np.average(sig_data[2,:])}')




if __name__ == '__main__':
    app = CirculationNsor()
    app.mainloop()
