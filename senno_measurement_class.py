import numpy as np
import pathlib

def get_current_file_path():     
    file_path = str(pathlib.Path(__file__).parent.resolve())  +'\\'   
    return file_path



class SennoMeasurement():

    class SennoTimeslot():
        def __init__(self, number):
            self.number  = number
            self.current_index = 0

            #these are used always to store the last added value 
            self.last_timestamp = 0
            self.last_value = 0

            #these are used only when save is on and values are appended to arrays
            self.saved_timestamps = []
            self.saved_values = []




    def __init__(self, number_of_timeslots):
        self.number_of_timeslots = number_of_timeslots
        self.timeslots = [] #active timeslots only

        self.save_measurements_is_on = False
        self.filename = ''
       
        #CREATE TIMESLOTS
        for i in range(self.number_of_timeslots):

            timeslot = self.SennoTimeslot(i)
            self.timeslots.append(timeslot)
            #self.timeslots.append(self.__all_active_and_nonactive_timeslots[i])       


    #ADD VALUE
    #this adds a value to the chosen timeslots last_value always
    #if save is on, it also adds it to saved array and increments current index by 1 in that slot
    def add_value(self, timeslot_number, timestamp, value):

        self.timeslots[timeslot_number].last_timestamp = timestamp
        self.timeslots[timeslot_number].last_value = value

        if self.save_measurements_is_on:
            self.timeslots[timeslot_number].saved_timestamps.append(timestamp)
            self.timeslots[timeslot_number].saved_values.append(value)

            self.timeslots[timeslot_number].current_index +=1
            #if timeslot_number == 0:
            #    self.current_index +=1


    #RETURN VALUES AS AN ARRAY
    #this returns values from all timeslots from chosen index in same form as the tensorflow model input uses.
    def get_values_as_array(self, index):

        values = []
        for i in range(self.number_of_timeslots):
            values.append(self.timeslots[i].saved_values[index])
        values = [values]
        #values = np.array([[4503,20149,8761,3384]])
        return values
    
    #same as abow but returns the last values added
    def get_last_values_as_array(self):
        values = []
        for i in range(self.number_of_timeslots):
            values.append(self.timeslots[i].last_value)
        values = [values]
        #values = np.array([[4503,20149,8761,3384]])
        return values
     
    #SAVE MEASUREMENT TO FILE  
    #this saves all measurements in active timeslots to separate files
    #files are saved in same folder the main python file is
    #last values in arrays are ignored, to prevent uneven amout of values between different timeslots  
    def save_measurement_to_file(self, filename):

        currentpath = get_current_file_path()
        

        for current_timeslot_number in range(self.number_of_timeslots):

            full_filename_and_path_with_timeslot_numbers = currentpath +filename+ "_SLOT_"+ str(current_timeslot_number) + ".txt"


            with open(full_filename_and_path_with_timeslot_numbers, 'a') as output:
                for i in range(self.timeslots[0].current_index-1): #this uses timeslot 0 current_index-1 to ignore last values in arrays, to prevent uneven amouts of values between different timeslots

                    timestamp_string = str(self.timeslots[current_timeslot_number].saved_timestamps[i])
                    value_string = str(self.timeslots[current_timeslot_number].saved_values[i])

                    output.write(timestamp_string+';'+value_string+ ';' + '\n')





def measurement_test_function():

    measurement = SennoMeasurement(4)
    measurement.save_measurements_is_on = True

    #print("current index: "+str(measurement.current_index))
    #measurement.add_value(0, 123)
    #print("current index: "+str(measurement.current_index))
    #measurement.add_value(0, 234)
    #print("current index: "+str(measurement.current_index))
    #measurement.add_value(0, 345)

    #TIMESLOT NUMBERS
    for i in range(measurement.number_of_timeslots):
        print('timeslot number: '+str(measurement.timeslots[i].number))


    measurement.add_value(0,100, 0)
    measurement.add_value(0,110, 1)
    measurement.add_value(0,120, 2)

    print("current index: "+str(measurement.timeslots[0].current_index))

    measurement.add_value(1,101, 10)
    measurement.add_value(1,111, 11)
    measurement.add_value(1,121, 12)

    measurement.add_value(2,102, 20)
    measurement.add_value(2,112, 21)
    measurement.add_value(2,122, 22)

    measurement.add_value(3,103, 30)
    measurement.add_value(3,113, 31)
    measurement.add_value(3,123, 32)


    values = measurement.get_values_as_array(0)
    print(values)

    values = measurement.get_values_as_array(1)
    print(values)

    values = measurement.get_values_as_array(2)
    print(values)

    measurement.save_measurement_to_file("testihomma1")

    print(measurement.get_last_values_as_array())

    

#measurement_test_function()