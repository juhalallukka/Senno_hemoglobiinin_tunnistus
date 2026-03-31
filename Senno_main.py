#import tkinter
#from tkinter import *
import tkinter as tk
import threading
import time
import asyncio
from bleak import BleakClient
from bleak import BleakGATTCharacteristic
import json
import time
import pathlib
import binascii
import datetime
import sys

from inference import GiveResult
from senno_measurement_class import SennoMeasurement


from tkinter import * 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
import matplotlib.animation as animation
import random


def get_current_file_path():     
    file_path = str(pathlib.Path(__file__).parent.resolve())  +'\\'   
    return file_path


#The bluetooth connection often fails to disconnect when program exits and causes then problems when restarting the program. 
#We tried many things to solve this within the code, but it still does that
#The most consistent way is to turn the laptop's bluetooth connection off and back on when restarting the program

program_is_running = True
connection_status = False
number_of_timeslots = 4

#This object is used to store measured values that are read from senno
measurement = SennoMeasurement(number_of_timeslots)


def get_classname_string(class_number):

    classname_string = ''

    match class_number:
        
        case 0:
            classname_string = 'Water'
                    
        case 1:
            classname_string = 'Hb 12,5'
            
        case 2:
            classname_string = 'Hb 25'
            
        case 3: 
            classname_string = 'Hb 50'

        case 4: 
            classname_string = 'Hb 100'

                         
    return classname_string

#BLEAK
#GitHub: https://github.com/hbldh/bleak
#dokumentaatio: https://bleak.readthedocs.io/en/latest/index.html

address = "F2:7E:9F:27:67:26"
#MODEL_NBR_UUID = "2A24"
MEASUREMENT_UUID = "ec4ff406-43e0-49d5-9d2f-5552ca9981be"





#CALLBACK
#https://bleak.readthedocs.io/en/latest/api/client.html#gatt-client-operations
#tehty BleakClient.start_notify-esimerkin pohjalta
def measurement_callback(sender: BleakGATTCharacteristic, data: bytearray):
    #currentpath

    
    data_hex = binascii.hexlify(data)
    #print(data_hex)


    #DATE
    date_int = int(data_hex[0:8], 16)/1000
    #print(date_int)

    realtime_stamp_int = int(data_hex[0:8], 16) #running int, ms from 1.1.1970?

    date_string = datetime.datetime.fromtimestamp(date_int).strftime('%Y-%m-%d %H:%M:%S')
    #print("DATE: "+ date_string)

    #SLOT
    slot_int = int(data_hex[8:10], 16)
    slot_string = str(slot_int)

    #FLAGS
    flag_int = int(data_hex[10:14], 16)
    flag_string = str(flag_int)

    #DATA SIZE
    data_size_int = int(data_hex[14:16], 16)
    data_size_string = str(data_size_int)

    #MEASUREMENT VALUES
    measurement_value0_int = int(data_hex[16:24], 16)
    measurement_value1_int = int(data_hex[24:32], 16)
    measurement_value2_int = int(data_hex[32:40], 16)
    measurement_value3_int = int(data_hex[40:48], 16)

    measurement_value0_string = str(measurement_value0_int)
    measurement_value1_string = str(measurement_value1_int)
    measurement_value2_string = str(measurement_value2_int)
    measurement_value3_string = str(measurement_value3_int)
    
    
    #ADD MEASURED VALUE TO MEASUREMENT OBJECT
    measurement.add_value(slot_int, realtime_stamp_int, measurement_value0_int)

    plotdata.add_value(slot_int,realtime_stamp_int, measurement_value0_int)



def get_prediction_from_model():
    global program_is_running
    global measurement

    while program_is_running:

        
        values = measurement.get_last_values_as_array()
        print(values)


        result1, result4_as_percentage = GiveResult(values) # result1 = predicted class, reslut4 = predicted consentration
        result4_as_percentage = round(result4_as_percentage, 2)

        #add the prediction to UI element
        txt_prediction_color.config(state=tk.NORMAL)
        txt_prediction_color.delete('1.0', tk.END)     
        #txt_prediction_color.insert(tk.END, get_classname_string(result1)) #show predicted class, model 1
        txt_prediction_color.insert(tk.END, result4_as_percentage) #show predicted percentage, model 4
        txt_prediction_color.config(state=tk.DISABLED)  #set  response text field back to read-only
        time.sleep(1) 



async def async_main(address):

    global connection_status
    async with BleakClient(address) as client:

        await client.start_notify(MEASUREMENT_UUID, measurement_callback)

        global program_is_running

        while client.is_connected & program_is_running:
            rawdata = await client.read_gatt_char(MEASUREMENT_UUID) #Tämä piti jostain syystä olla mukana ja nyt lukee ilmeisesti kaikki datat kokoajan, vaikka luuppi pyörii vain kerran 5 sekunnissa

            #set_connection_status_to_UI(client.is_connected)
            connection_status = client.is_connected

            await asyncio.sleep(5)
        #set_connection_status_to_UI(client.is_connected)
        connection_status = client.is_connected
        print("out from measurement loop")

        await client.stop_notify(MEASUREMENT_UUID)

        await client.disconnect()
        print("connection status: ")
        print(client.is_connected)     

        return


#*****************************************************************************


#FUNCTIONS********************************************************************
def init_program():
    Button_start_measurement.config(state=tk.NORMAL)
    Button_stop_measurement.config(state=tk.DISABLED)
    set_connection_status_to_UI(False)
    #plot()

def set_connection_status_to_UI(status):   
    if status == True:    
        txt_connection_status.config(state=tk.NORMAL, fg="green")
        txt_connection_status.delete('1.0', tk.END)
        txt_connection_status.insert(tk.END, "Connected")
        txt_connection_status.config(state=tk.DISABLED)
    else:      
        txt_connection_status.config(state=tk.NORMAL, fg="red")
        txt_connection_status.delete('1.0', tk.END)
        txt_connection_status.insert(tk.END, "Not connected")
        txt_connection_status.config(state=tk.DISABLED)  


def update_connection_status():
    global connection_status
    global program_is_running

    while program_is_running:
        set_connection_status_to_UI(connection_status)
        #root.update()
        time.sleep(1)

def read_data_from_senno():  
    asyncio.run(async_main(address))


def run_measurement_loop():
    handle_measurement = threading.Thread(target=read_data_from_senno, daemon=True)
    handle_measurement.start()  

def run_prediction_from_model():
    handle_prediction_fom_model = threading.Thread(target=get_prediction_from_model, daemon=True)
    handle_prediction_fom_model.start()

def run_update_connection_status():
    handle_update_connection_status = threading.Thread(target=update_connection_status, daemon=True)
    handle_update_connection_status.start()



root = tk.Tk()
root.geometry("1200x750")
root.title(" Senno ")


def start_saving_measurement():   
    print("start_saving_measurement")
    inputtxt_filename.config(state=tk.DISABLED)
    Button_start_measurement.config(state=tk.DISABLED)
    Button_stop_measurement.config(state=tk.NORMAL)

    global measurement
    measurement = SennoMeasurement(number_of_timeslots) #new empty measurements object
    measurement.save_measurements_is_on = True
    measurement.filename = inputtxt_filename.get("1.0", "end-1c")


def stop_saving_measurement():   
    print("stop_saving_measurement")
    inputtxt_filename.config(state=tk.NORMAL)
    Button_start_measurement.config(state=tk.NORMAL)
    Button_stop_measurement.config(state=tk.DISABLED)

    global measurement
    measurement.save_measurements_is_on = False
    measurement.save_measurement_to_file(measurement.filename)


def press_button_start_saving_measurement():
    print("press button start")
    handle_start_saving_measurement = threading.Thread(target=start_saving_measurement)
    handle_start_saving_measurement.start() 

def press_button_stop_saving_measurement():
    print("press button stop")
    handle_stop_saving_measurement = threading.Thread(target=stop_saving_measurement)
    handle_stop_saving_measurement.start() 


#UI*****************************************************************************************************
#separate UI to left and right side 
frame_left = tk.Frame(root)
frame_right = tk.Frame(root)
frame_left.grid(row=0, column=0, sticky="nsew")
frame_right.grid(row=0, column=1, sticky="nsew")
root.grid_columnconfigure(0, weight=1, uniform="group1")
root.grid_columnconfigure(1, weight=1, uniform="group1")
root.grid_rowconfigure(0, weight=1)




#filename frame
frame_filename = tk.Frame(frame_left)
txt_connection_status = tk.Text(frame_filename, height = 1,
                width = 15,
                bg = "light grey")

label_filename = tk.Label(frame_filename, text = "Filename:")
inputtxt_filename = tk.Text(frame_filename, height = 1,
                width = 15,
                bg = "light yellow")



Button_start_measurement = tk.Button(frame_filename, height = 2,
                 width = 20, 
                 text ="Start",
                 command = lambda:press_button_start_saving_measurement())

Button_stop_measurement = tk.Button(frame_filename, height = 2,
                 width = 20, 
                 text ="stop",
                 command = lambda:press_button_stop_saving_measurement())

txt_connection_status.pack(side = tk.TOP, expand = False)
label_filename.pack(side = tk.TOP, expand = False)
inputtxt_filename.pack(side = tk.TOP, expand = False)
Button_start_measurement.pack(side = tk.TOP, expand = False)
Button_stop_measurement.pack(side = tk.TOP, expand = False)



frame_filename.pack(side = tk.TOP, expand = False)

#prediction
frame_prediction = tk.Frame(frame_right)

label_prediction = tk.Label(frame_prediction, text = "Prediction:")
txt_prediction_color = tk.Text(frame_prediction, height = 1,
                width = 15,
                bg = "light yellow")
frame_prediction.pack(side = tk.TOP, expand = False)
label_prediction.pack(side = tk.TOP, expand = False)
txt_prediction_color.pack(side = tk.TOP, expand = False)



#plot
fig_plot = Figure(figsize = (5, 5), dpi = 100)
canvas_plot = FigureCanvasTkAgg(fig_plot, master = frame_right)
canvas_plot.get_tk_widget().pack()
ax_plot = fig_plot.add_subplot(1,1,1)

canvas_plot.get_tk_widget().pack(side = tk.TOP, expand = False)

frame_plot_timeslot = tk.Frame(frame_right)
label_plot_timeslot = tk.Label(frame_plot_timeslot, text = "timeslot:")
inputtxt_plot_timeslot = tk.Text(frame_plot_timeslot, height = 1,
                width = 15,
                bg = "light yellow")


Button_plot_timeslot_minus = tk.Button(frame_plot_timeslot, height = 2,
                 width = 5, 
                 text ="-",
                 command = lambda:plotdata.timeslot_minus())
Button_plot_timeslot_plus = tk.Button(frame_plot_timeslot, height = 2,
                 width = 5, 
                 text ="+",
                 command = lambda:plotdata.timeslot_plus())


label_plot_timeslot.pack(side = tk.LEFT, expand = False)
inputtxt_plot_timeslot.pack(side = tk.LEFT, expand = False)
Button_plot_timeslot_minus.pack(side = tk.LEFT, expand = False)
Button_plot_timeslot_plus.pack(side = tk.LEFT, expand = False)
frame_plot_timeslot.pack(side = tk.TOP, expand = False)



#PLOT**********************************************************************************************************

#SennoPlotData
#this class is similar to the SennoMmasurement class, but is tailored to be more suitable for the plotting
#currently this class doesn't save the real time stamps but uses an incremented index number as the x-axis of the plot
class SennoPlotData():
    class PlotDataTimeslot():
        def __init__(self, number):
            self.number  = number
            self.current_index = 0
          
            self.saved_timestamps = []
            self.saved_values = []


    def __init__(self, number_of_timeslots):
        self.number_of_timeslots = number_of_timeslots
        self.timeslots = [] #active timeslots only

        self.number_of_values_to_show_in_plot = 50
        self.timeslot_number_to_plot = 0
       
        #CREATE TIMESLOTS
        for i in range(self.number_of_timeslots):

            timeslot = self.PlotDataTimeslot(i)
            self.timeslots.append(timeslot)           

    #ADD VALUE
    #this adds value to the chosen timeslots value and timestamp array and increments current index by 1 in that slot
    #similar to the measurement class add-value() function
    #incrementing index number is used on x-axis instead of the timestamp. 
    #timestamp-parameter is currently only included to futureproof code, so if we need real timestamps later, code needs less tinkering             
    def add_value(self, timeslot_number, timestamp, value):
      
        self.timeslots[timeslot_number].saved_timestamps.append(self.timeslots[timeslot_number].current_index) #x-axis
        #self.timeslots[timeslot_number].saved_timestamps.append(timestamp) #alternate way to use real timestamps as x-axis, makes graph look messy
        self.timeslots[timeslot_number].saved_values.append(value) #y-axis

        self.timeslots[timeslot_number].current_index +=1

    #returns array, that contains the last values from x-axis array (=currently just index numbers) equal to the number_of_values_to_show_in_plot
    def get_x(self, timeslot_number):
        x_axis =   self.timeslots[timeslot_number].saved_timestamps[-self.number_of_values_to_show_in_plot:]  
        return x_axis
    
    #returns array, that contains the last values from y-axis array (=measured values) equal to the number_of_values_to_show_in_plot
    def get_y(self, timeslot_number):
        y_axis = self.timeslots[timeslot_number].saved_values[-self.number_of_values_to_show_in_plot:]
        return y_axis

    def timeslot_plus(self):
        if self.timeslot_number_to_plot < len(self.timeslots)-1:
            self.timeslot_number_to_plot +=1

    def timeslot_minus(self):
        if self.timeslot_number_to_plot > 0:
            self.timeslot_number_to_plot -=1    

plotdata = SennoPlotData(number_of_timeslots)

def update_timeslot_number_to_plot_to_UI():
    inputtxt_plot_timeslot.config(state=tk.NORMAL)
    inputtxt_plot_timeslot.delete('1.0', tk.END)
    timeslot_number =str(plotdata.timeslot_number_to_plot)
    inputtxt_plot_timeslot.insert(tk.END, timeslot_number)
    inputtxt_plot_timeslot.config(state=tk.DISABLED)


def plot():
    #print("PLOT*************************")

    while program_is_running:

        
        while connection_status == False:
            time.sleep(1) #wait if device isn't connected

        update_timeslot_number_to_plot_to_UI()    
        ax_plot.clear()
        ax_plot.plot(plotdata.get_x(plotdata.timeslot_number_to_plot),plotdata.get_y(plotdata.timeslot_number_to_plot))          
        canvas_plot.draw()

        time.sleep(1)


def run_plot_loop():
    handle_plot = threading.Thread(target=plot, daemon=True)
    handle_plot.start()






#MAIN**************************************************************************************************

init_program()
run_plot_loop()
run_prediction_from_model()
run_measurement_loop()
run_update_connection_status()

root.mainloop()
#tk.mainloop()

program_is_running = False
time.sleep(5)
exit()

#The bluetooth connection often fails to disconnect when program exits and causes then problems when restarting the program. 
#We tried many things to solve this within the code, but it still does that
#The most consistent way is to turn the laptop's bluetooth connection off and back on when restarting the program