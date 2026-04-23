#   Antenna Properties
XantPosition  = 50
YantPosition  = -100
ZantPosition  = 0

###############################################################################
##    Task 1
##    1. Set up your phyton workspace
from win32api import GetSystemMetrics
from comtypes.client import CreateObject
import pandas as pd
import json
from numpy import sqrt
from collections import defaultdict
from datetime import datetime, timedelta
import sys

##    2. Get reference to running STK instance
uiApplication = CreateObject('STK11.Application')
uiApplication.Visible = False
uiApplication.UsarControl=True

##    3. Get our IAgStkObjectRoot interface
root = uiApplication.Personality2

# Note: When 'root=uiApplication.Personality2' is executed, the comtypes library automatically creates a gen folder that contains STKUtil and STK Objects. 
# After running this at least once on your computer, the following two lines should be moved before the 'uiApplication=CreateObject("STK12.Application")'
# line for improved performance. 

from comtypes.gen import STKObjects
from comtypes.gen import STKUtil
import STKEntities
import STKAPI as stk_api


path_to_tle = "TLE/"
f_idx = open('Scenarios/Spy_Sat_manualpointing.json')
scenario_metadata = json.load(f_idx)

ScenarioName  = scenario_metadata["Scenario"]["name"]
StartTime   = scenario_metadata["time constraints"]["start time"]
StopTime     = scenario_metadata["time constraints"]["stop time"]
StepTime      = scenario_metadata["time constraints"]["step"]

step = timedelta(seconds = StepTime)

######################################
##    Task 2
##    1. Create a new scenario

root.NewScenario(ScenarioName)
scenario      = root.CurrentScenario

##    2. Set the analytical time period.

scenario2     = scenario.QueryInterface(STKObjects.IAgScenario)
scenario2.SetTimePeriod(StartTime,StopTime)
scenario2.Animation.AnimStepValue = StepTime

##    3. Reset the animation time.
root.Rewind()

# Get the entity parameters from the scenario file and initialize the entities.
Satellites = {}
sat_idx = 0
for sat in scenario_metadata['satellites']:  
    sat_idx += 1
    sat_name = scenario_metadata["satellites"][sat]["name"]
    sat_scc = scenario_metadata["satellites"][sat]["propagator_params"]["scc"]
    tle_file_path = scenario_metadata["satellites"][sat]["propagator_params"]["tle_file"]
    Satellites[sat_name] = STKEntities.Stk_Satellite(root, sat_name)
    Satellites[sat_name].SetSatellitePropagator_and_BasicAttitude(root, sat_scc, True, tle_file_path, True)

GroundStations = {}
gs_idx = 0
for gs in scenario_metadata['ground_stations']:  
    gs_idx += 1
    gs_name = scenario_metadata["ground_stations"][gs]["name"]
    unit = scenario_metadata["ground_stations"][gs]["lat_long_unit"]
    use_terrain = scenario_metadata["ground_stations"][gs]["use_terrain"]
    lat = scenario_metadata["ground_stations"][gs]["lat"]
    long = scenario_metadata["ground_stations"][gs]["long"]
    alt = scenario_metadata["ground_stations"][gs]["alt"]
    GroundStations[gs_name] = STKEntities.STKGroundStation(root, gs_name, unit, use_terrain, lat, long, alt)

Antennas = {}
an_idx = 0
for an in scenario_metadata["antennas"]:
    an_idx += 1
    an_name = scenario_metadata["antennas"][an]["name"]
    parent_name = scenario_metadata["antennas"][an]["antenna_parent"]
    model = scenario_metadata["antennas"][an]["model"]
    diameter = scenario_metadata["antennas"][an]["diameter"]
    computer_diameter = scenario_metadata["antennas"][an]["computer_diameter"]
    freq = scenario_metadata["antennas"][an]["freq"]
    Elv = scenario_metadata["antennas"][an]["Elv"]
    sensor_bool = scenario_metadata["antennas"][an]["sensor_bool"]
    Antennas[an_name] = STKEntities.STKAntenna(an_name, GroundStations[parent_name].groundStation, model, diameter, computer_diameter, freq) 
    if not sensor_bool:
        Antennas[an_name].set_azelorientation(0, Elv, 0) 

Transmitters = {}
ts_idx = 0
for ts in scenario_metadata['transmitters']:
    ts_idx += 1  
    ts_name = scenario_metadata["transmitters"][ts]["name"]
    parent_name = scenario_metadata["transmitters"][ts]["transmitter_parent"]
    model = scenario_metadata["transmitters"][ts]["model"]
    dem = scenario_metadata["transmitters"][ts]["dem"]
    auto_scale_bandwidth = scenario_metadata["transmitters"][ts]["auto_scale_bandwidth"]
    freq = scenario_metadata["transmitters"][ts]["freq"]
    power = scenario_metadata["transmitters"][ts]["power"]
    data_rate = scenario_metadata["transmitters"][ts]["data_rate"]
    antenna_control = scenario_metadata["transmitters"][ts]["antenna_control"]
    Transmitters[ts_name] = STKEntities.STKTransmitter(root, ts_name, GroundStations[parent_name].groundStation, model, dem, auto_scale_bandwidth, freq, power, data_rate, antenna_control)

Receivers = {}
rs_idx = 0
for rs in scenario_metadata['receivers']:  
    rs_idx += 1
    rs_name = scenario_metadata["receivers"][rs]["name"]
    parent_name = scenario_metadata["receivers"][rs]["receiver_parent"]
    model = scenario_metadata["receivers"][rs]["receiver_type"]
    auto_select_modulator = scenario_metadata["receivers"][rs]["auto_select_modulator"]
    dem = scenario_metadata["receivers"][rs]["dem"]
    antenna_control = scenario_metadata["receivers"][rs]["antenna_control"]
    Receivers[rs_name] = STKEntities.STKReceptor(rs_name, Satellites[parent_name].sat, model, auto_select_modulator, dem, antenna_control)
  
######################################
##    Task 3
##    2. Retrive and view the altitud of the satellite during an access interval.

sat_list = []
allowed_inputs = []
sat_names = []
satellites_to_log = []
i = 1
for key, vals in Satellites.items():
    menu_option = str(i) + "\t-\t" + key
    sat_list.append(menu_option)
    allowed_inputs.append(i)
    sat_names.append(key)
    i += 1


print("Select Satellite for manual tracking from the following options: ")
for i, val in enumerate(sat_list):
    print(val)
while(True):
    choice = input()
    choice = int(choice)
    if choice in allowed_inputs:
        choice -= 1
        target_sat_name = sat_names[choice]
        break

print(target_sat_name)

print("Select wich Satellite is considered the Spy: ")
for i, val in enumerate(sat_list):
    print(val)
while(True):
    choice = input()
    choice = int(choice)
    if choice in allowed_inputs:
        choice -= 1
        spy_sat_name = sat_names[choice]
        break

print(spy_sat_name)

sat_list.append("Input 0 to continue")

print("To generate log tables select Satellites from the following options: ")
for i, val in enumerate(sat_list):
    print(val)
while(True):
    choice = input()
    choice = int(choice)
    if choice == 0:
        break
    if choice in allowed_inputs:
        choice -= 1
        satellites_to_log.append(sat_names[choice])
    


print(satellites_to_log)




Access = {}    
tabla = defaultdict(list)
access_times = []
Az = 0
Elev = 0
index = 0
current_size = 1000

#4.6km

for rec in scenario_metadata["receivers"]:
    if scenario_metadata["receivers"][rec]["link_bool"] == True:
        acces_name = scenario_metadata["receivers"][rec]["receiver_parent"] + "_acces_" + scenario_metadata["receivers"][rec]["link_transmitters"][0]
        report_name = scenario_metadata["receivers"][rec]["receiver_parent"] + "_" + scenario_metadata["receivers"][rec]["link_transmitters"][0] + "manual_antena_pointing"
        ts_name = scenario_metadata["receivers"][rec]["link_transmitters"][0]
        rs_name = scenario_metadata["receivers"][rec]["name"]
        rs_sat_name = scenario_metadata["receivers"][rec]["receiver_parent"]
        ts_an_name = scenario_metadata["receivers"][rec]["link_antennas"][0]
        if rs_sat_name == target_sat_name:
            Access[acces_name] = Transmitters[ts_name].transmitter.GetAccessToObject(Receivers[rs_name].receptor)
            Access[acces_name].ComputeAccess()
            
            new_access_times = []
            longest_access_start_time, longest_access_stop_time = stk_api.get_access_time(Access[acces_name], 0, scenario2, True)
            for spy_rec in scenario_metadata["receivers"]:
                rs_sat_name = scenario_metadata["receivers"][spy_rec]["receiver_parent"]
                if rs_sat_name == spy_sat_name:
                    print(rs_sat_name)
                    spy_acces_name = scenario_metadata["receivers"][spy_rec]["receiver_parent"] + "_acces_" + scenario_metadata["receivers"][spy_rec]["link_transmitters"][0]
                    spy_report_name = scenario_metadata["receivers"][spy_rec]["receiver_parent"] + "_" + scenario_metadata["receivers"][spy_rec]["link_transmitters"][0] + "manual_antena_pointing"
                    spy_ts_name = scenario_metadata["receivers"][spy_rec]["link_transmitters"][0]
                    spy_rs_name = scenario_metadata["receivers"][spy_rec]["name"]
                    spy_ts_an_name = scenario_metadata["receivers"][spy_rec]["link_antennas"][0]                        
                    Access[spy_acces_name] = Transmitters[spy_ts_name].transmitter.GetAccessToObject(Receivers[spy_rs_name].receptor)
                    Access[spy_acces_name].ComputeAccess()
                    new_start_time, new_stop_time, new_access_times = stk_api.get_access_within_access(longest_access_start_time, longest_access_stop_time, Access[spy_acces_name], scenario2, StepTime)
            
            
            aer_elements = ["Access Number", "Azimuth", "Elevation"]
            
            li_elements = ["Time", 'C/No', 'Eb/No', "BER", "Range", "EIRP", "Free Space Loss", "Xmtr Elevation", "Xmtr Azimuth", "Xmtr Gain", "Xmtr Power", "Rcvd. Iso. Power", "Carrier Power at Rcvr Input"]
            
            pv_elements = ["x", "y", "z", "xVel", "yVel", "zVel", "RelSpeed"]
            
            lla_elements = ["Lat", "Lon", "Alt"]
            
            tabla =  defaultdict(lambda: defaultdict(list))
             
            for times in new_access_times:
                 
                AER_data = stk_api.get_instantaneous_link_data(Access[acces_name], "AER Data", "NorthEastDown", times, ["Elevation", "Azimuth"])
                
                azimuth = AER_data["Azimuth"][0]
                elevation = AER_data["Elevation"][0] 
                
                elevation = (elevation) 
                
                print(azimuth, elevation)    
                Antennas[ts_an_name].set_azelorientation(azimuth,elevation,0)               
                
                for key, access in Access.items():
                    AER_data = stk_api.get_instantaneous_link_data(access, "AER Data", "NorthEastDown", times, aer_elements)
                    LinkInfo = stk_api.get_instantaneous_link_data(access, "Link Information", 0, times, li_elements)
                    PositionVelocity = stk_api.get_instantaneous_link_data(access, "To Position Velocity", "J2000", times, pv_elements)
                    LLAState = stk_api.get_instantaneous_link_data(Satellites[rs_sat_name].sat, "LLA State", "Fixed", times, lla_elements)
                    orientation = Antennas[ts_an_name].get_azelorientation()    
                    to_join_dict = (AER_data, LinkInfo, PositionVelocity, LLAState)
                    
                    for dicts in to_join_dict:
                        for key_dict, vals in dicts.items():
                            tabla[key][key_dict].append(vals[0])

                    tabla[key]['Antenna Azimuth'].append(orientation[0])
                    tabla[key]['Antenna Elevation'].append(orientation[1])

            for key, tabla in tabla.items():
                reporte = pd.DataFrame(tabla)
                reporte.to_excel("Reports/" + key + "manual_antena_pointing.xlsx")
                reporte.to_csv("Reports/" + key + "manual_antena_pointing.csv")
        


