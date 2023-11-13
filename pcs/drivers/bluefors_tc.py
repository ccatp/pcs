# bluefors_tc.py

import json
import requests

class BFTC:
    """
        Bluefors Temperature Controller (BFTC) class.

        Attributes:
            ip (str) - IP address of the BFTC
            port (str) - Port number at which the HTTP commands are 
            timeout (int) - number of seconds to wait for HTTP requests to go through
            http_root (str) - beginning of the path for any HTTP command for this device
            channels (list) - list of channel objects, index+1 corresponds to channel number
            mxc_heater (obj) - Heater class object for the MXC heater
            still_heater (obj) - Heater class object for the still heater

    """

    def __init__(self,ip,port='5001',timeout=10,num_channels=12):
        self.ip = ip
        self.timeout = timeout
        self.num_channels = num_channels
        self.http_root = 'http://' + str(self.ip) + ':' + str(port)

        # The BFTC supports 12 thermometer channels
        self.channels = []
        for i in range(1,num_channels+1):
            c = Channel(self,i)
            self.channels.append(c)
        # The BFTC supports four heaters, but heaters 1 and 2 are heat switches
        self.still_heater = Heater(self,3)
        self.mxc_heater = Heater(self,4)


    def msg(self,path,message):
        """
            Send message to the BF TC over HTTP via the requests package.

            Parameters:
            path (str) - the location in the BF TC API of the command you want
                        Ex.: "/heater" accesses commands for a heater
            message (dict) - a JSON dictionary containing the relevant keys for 
                             executing the desired command within the BF TC API.
                             If message is an empty dictionary, this function
                             will send a GET request. It sends POST requests for
                             a dictionary with keys.
        """
        url = self.http_root + path

        if len(list(message.keys())) != 0:
            # Try once - if we timeout, try again for post requests.
            # Aiming to avoid single glitches in return message.
            for attempt in range(2):
                try:
                    req = requests.post(url, json=message, timeout=self.timeout)
                except requests.Timeout:
                    print("Warning: Caught timeout waiting for response to {} at"
                          " {}, trying again before giving up".format(message,path))
                    if attempt == 1:
                        raise RuntimeError('Query response to BF TC timed out after'
                                           ' two attempts. Check connection.')
        else:
            req = requests.get(url, timeout=self.timeout)

        resp = req.json()
        return resp


    def get_serial(self):
        """Returns serial number of device (str)"""
        return self.msg('/system',{})['serial']

    def get_ip_address(self):
        """Returns IP address of device (str)"""
        return self.msg('/system/network',{})['ip_address']

    def get_mac_address(self):
        """Returns MAC address of device (str)"""
        return self.msg('/system/network',{})['mac_address']

class Channel:
    """
        Class for thermometer channels on the BFTC.

        Attributes:
            bftc (obj) - BFTC object with which this Channel is associated
            channel_num (int) - the channel number on the BFTC
            curve_num (int) - the curve number that goes with this channel
                              (if one is present)

    """

    def __init__(self,bftc,channel_num):
        self.bftc = bftc
        self.channel_num = channel_num
        self.cal_curve_num = self.get_cal_curve_number()

    def get_state(self):
        """
           Returns the active state of the channel (bool)

           Possible outputs are True (channel is active) and False (not active).
        """
        return self.bftc.msg('/channel',{'channel_nr': self.channel_num})['active']

    def enable_channel(self):
        """
            Sets the state of the channel to active.
        """
        message = {'channel_nr': self.channel_num, 
                   'active': True}
        path = '/channel/update'
        
        resp = self.bftc.msg(path,message)
        
        if resp['active']:
            print("Channel {} successfully enabled.".format(self.channel_num))
        else:
            print("Channel {} failed to enable. Please investigate.".format(self.channel_num))

    def disable_channel(self):
        """
            Sets the state of the channel to inactive.
        """
        message = {'channel_nr': self.channel_num, 
                   'active': False}
        path = '/channel/update'
        
        resp = self.bftc.msg(path,message)
        
        if not resp['active']:
            print("Channel {} successfully disabled.".format(self.channel_num))
        else:
            print("Channel {} failed to disable. Please investigate.".format(self.channel_num))

    def get_excitation_mode(self):
        """
           Returns the excitation mode of the channel (int).
        
           Possible outputs are 0 (current excitation), 1 (VMAX), and 2 (CMN)
        """
        message = {'channel_nr': self.channel_num}

        return self.bftc.msg('/channel',message)['excitation_mode']

    def get_temperature(self):
        """
           Returns the most recent temperature of the channel in K (float).
        """
        message = {'channel_nr': self.channel_num}

        try:
            resp = self.bftc.msg('/channel/measurement/latest',message)['temperature']
            return resp
        except KeyError as ke:
            print('Key not found in /channel/measurement/latest: ', ke)
            return ""

    def get_resistance(self):
        """
           Returns the most recent resistance of the channel in ohms (float).
        """
        message = {'channel_nr': self.channel_num}
        
        try:
            resp = self.bftc.msg('/channel/measurement/latest',message)['resistance']
            return resp
        except KeyError as ke:
            print('Key not found in /channel/measurement/latest: ', ke)
            return ""

    def get_reactance(self):
        """
           Returns the most recent reactance of the channel in ohms (float).
        """
        message = {'channel_nr': self.channel_num}

        try:
            resp = self.bftc.msg('/channel/measurement/latest',message)['reactance']
            return resp
        except KeyError as ke:
            print('Key not found in /channel/measurement/latest: ', ke)
            return ""    
        
    def get_excitation_current_range(self):
        pass
    
    def set_excitation_current_range(self,cur_range):
        pass
    
    def get_excitation_cmn_range(self):
        pass
    
    def set_excitation_cmn_range(self,cmn_range):
        pass    

    def get_excitation_vmax_range(self):
        pass
    
    def set_excitation_vmax_range(self,vmax_range):
        pass
        
    def get_use_non_default_timecon(self):
        pass
    
    def enable_use_non_default_timecon(self):
        pass
    
    def disable_use_non_default_timecon(self):
        pass
    
    def get_wait_time(self):
        pass
        
    def set_wait_time(self,wait_time):
        # Only matters if not using default time constants - should check that
        # before allowing this method to go through
        pass

    def get_meas_time(self):
        pass
        
    def set_meas_time(self,meas_time):
        # Only matters if not using default time constants - should check that
        # before allowing this method to go through
        pass
        
    def get_cal_curve_number(self):
        """
           Returns the calibration curve number associated with the channel (int).
        
           The returned channel number will be between 1 and 100. 
           
           If no curve has been specially set, the curve number will just be the
           channel number - there may be no curve uploaded to this number though!
        """
        message = {'channel_nr': self.channel_num}

        return self.bftc.msg('/channel',message)['calib_curve_nr']
        
    def set_cal_curve_number(self,cal_curve_num):
        pass        

class Heater:
    """
        Class for heaters on the BFTC.

        Attributes:
            bftc (obj) - BFTC object with which this Channel is associated
            heater_num (int) - the heater number on the BFTC
        
    """

    def __init__(self,bftc,heater_num):
        self.bftc = bftc
        self.heater_num = heater_num
        
        # Should we make more parameters object variables?
        
    def get_state(self):
        pass
    
    def enable_heater(self):
        pass
    
    def disable_heater(self):
        pass
        
    def get_pid_mode(self):
        pass
    
    def set_pid_mode(self,mode):
        pass
    
    def get_resistance(self):
        pass
        
    def set_resistance(self,res):
        pass
    
    def get_power(self):
        pass
    
    def set_power(self,power):
        pass
        
    def get_max_power(self):
        pass
        
    def set_max_power(self,max_power):
        pass
    
    def get_target_temperature(self):
        pass
        
    def set_target_temperature(self):
        # Believe this is for manual mode only
        pass
    
    def get_setpoint(self):
        pass
    
    def set_setpoint(self,setpoint):
        # Should be setpoint for standard PID mode
        pass
    
    def get_pid_settings(self):
        # Return P, I, and D
        pass
    
    def set_pid_settings(self,p,i,d):
        # Set them all every time? Options to only update one?
        pass

class Curve:
    """
        Class to handle thermometer calibration curves on the BFTC.
        
        Attributes:
        bftc (obj) - BFTC object with which this Curve is associated
        curve_num (int) - the curve number on the BFTC
    """
    def __init__(self,bftc,curve_num):
        self.bftc = bftc
        self.curve_number = curve_num
        
        self.name = None
        self.sensor_model = None
        self.type = None
        self.num_points = None
        
    # Need to examine how the BFTC handles curves and how it is the same
    # or different compared to the way the Lakeshore does before sketching
    # out functions.
    
    def get_name(self):
        pass

    def get_sensor_model(self):
        pass

    def get_type(self):
        """Should be 1 for a standard R->T curve"""
        pass

    def num_points(self):
        pass

    def get_impedances(self):
        pass

    def get_temperatures(self):
        pass
        
    def upload_curve(self,input_file):
        """This is the more complicated one to define - we need to look at how to parse
           a standard Lakeshore calibration curve file into the correct name,
           resistances (impedances), temperatures, number of points, sensor
           model, and anything else that it might need. Those things can be
           loaded in with a single POST command after parsing the input file.
           Probably want to make helper functions to do each step in case we
           ever want to manually adjust those things remotely.
           
           It looks like there may be a way to upload the whole calibration
           curve file as a string, but we'd have to test that."""
        pass
    
    def remove_curve(self):
        pass


