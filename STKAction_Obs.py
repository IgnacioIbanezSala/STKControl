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
import STKAPI as stk_api

##    2. Get reference to running STK instance
uiApplication = CreateObject('STK11.Application')
uiApplication.Visible = True
uiApplication.UsarControl=True

##    3. Get our IAgStkObjectRoot interface
root = uiApplication.Personality2

# Note: When 'root=uiApplication.Personality2' is executed, the comtypes library automatically creates a gen folder that contains STKUtil and STK Objects. 
# After running this at least once on your computer, the following two lines should be moved before the 'uiApplication=CreateObject("STK12.Application")'
# line for improved performance. 

from comtypes.gen import STKObjects
from comtypes.gen import STKUtil
import STKEntities


path_to_tle = "TLE/"
f_idx = open('Scenarios/Spy_Sat_noantennareceptor.json')
scenario_metadata = json.load(f_idx)

ScenarioName    = scenario_metadata["Scenario"]["name"]
StartTime       = scenario_metadata["time constraints"]["start time"]
StopTime        = scenario_metadata["time constraints"]["stop time"]
StepTime        = scenario_metadata["time constraints"]["step"]
SpyRs           = scenario_metadata["Scenario"]["SpyRs"]
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

Sensors = {}
ss_idx = 0
for ss in scenario_metadata['sensors']:
    ss_idx += 1
    ss_name = scenario_metadata["sensors"][ss]["name"]
    ss_parent = scenario_metadata["sensors"][ss]["sensor_parent"]
    targets = scenario_metadata["sensors"][ss]["sensor_targets"]
    Sensors[ss_name] = STKEntities.STKTargetedSensor(ss_name, GroundStations[ss_parent].groundStation, Satellites[targets[0]].sat.Path)
    for i in range(0, len(targets)):
        Sensors[ss_name].add_target(Satellites[targets[i]].sat)

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
    if not sensor_bool:
        Antennas[an_name] = STKEntities.STKAntenna(an_name, Satellites[parent_name].sat, model, diameter, computer_diameter, freq)
        Antennas[an_name].set_azelorientation(0, Elv, 0)  
    else:
        Antennas[an_name] = STKEntities.STKAntenna(an_name, Sensors[parent_name].sensor, model, diameter, computer_diameter, freq)


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


    
root.SaveScenario()

######################################
##    Task 3
##    2. Retrive and view the altitud of the satellite during an access interval.

def TimeSync(accessStartTime_1, accessStopTime_1, duration_1, link, StartTime, StopTime, StepTime):

    access_data = link.DataProviders.Item('Access Data')
    access_data_query  = access_data.QueryInterface(STKObjects.IAgDataPrvInterval)
    access_data_results = access_data_query.Exec(StartTime, StopTime)
    accessStartTime_2 = access_data_results.DataSets.GetDataSetByName('Start Time').GetValues()
    accessStopTime_2  = access_data_results.DataSets.GetDataSetByName('Stop Time').GetValues()

    new_duration = 0
    longest_duration_idx = 0
    for i, duration in enumerate(duration_1):
        if i==0:
            new_duration = duration
        else:
            if duration > new_duration:
                new_duration = duration
                longest_duration_idx = i

    new_start_time = 0
    new_stop_time = 0
    new_access_times = []

    for start_time, stop_time in zip(accessStartTime_2, accessStopTime_2):
        if start_time > accessStartTime_1[longest_duration_idx] and start_time<accessStopTime_1[longest_duration_idx]:
            new_start_time = start_time
        if stop_time < accessStopTime_1[longest_duration_idx]:
            new_stop_time = stop_time
        if stop_time > accessStopTime_1[longest_duration_idx]:
            new_stop_time = accessStopTime_1[longest_duration_idx]
    
    
    step = timedelta(seconds = StepTime)
    new_start_time = new_start_time[0:20]
    new_stop_time = new_stop_time[0:20]
    format_with_time = "%d %b %Y %H:%M:%S"
    datetime_object = datetime.strptime(new_start_time, format_with_time)
    datetime_object = datetime_object + step
    new_time = datetime_object.strftime('%d %b %Y %H:%M:%S.%f')
    while (new_time < new_stop_time):
        new_access_times.append(new_time)
        datetime_object = datetime_object + step
        new_time = datetime_object.strftime('%d %b %Y %H:%M:%S.%f')

    return new_start_time, new_stop_time, new_access_times
    
    
Access = {}  
tabla = defaultdict(list) 
new_start_time = 0
new_stop_time = 0


acces_name_sc1a = scenario_metadata["receivers"]["saocom1a_receiver"]["receiver_parent"] + "_acces_" + scenario_metadata["receivers"]["saocom1a_receiver"]["link_transmitters"][0]
report_name = scenario_metadata["receivers"]["saocom1a_receiver"]["receiver_parent"] + "_" + scenario_metadata["receivers"]["saocom1a_receiver"]["link_transmitters"][0]
ts_name_sc1a = scenario_metadata["receivers"]["saocom1a_receiver"]["link_transmitters"][0]
dem = scenario_metadata["receivers"]["saocom1a_receiver"]["dem"]
rs_name = scenario_metadata["receivers"]["saocom1a_receiver"]["name"]
rs_sat_name_sc1a = scenario_metadata["receivers"]["saocom1a_receiver"]["receiver_parent"]
ts_gs_name = scenario_metadata["receivers"]["saocom1a_receiver"]["link_transmitters"][0]
ts_an_name = scenario_metadata["receivers"]["saocom1a_receiver"]["link_antennas"][0]
Access[acces_name_sc1a] = Transmitters[ts_name_sc1a].transmitter.GetAccessToObject(Receivers[rs_name].receptor)
Access[acces_name_sc1a].ComputeAccess()

accessStartTime, accessStopTime, duration_1 = stk_api.get_access_times(Access[acces_name_sc1a], scenario2)

acces_name = scenario_metadata["receivers"]["eve_receiver"]["receiver_parent"] + "_acces_" + scenario_metadata["receivers"]["eve_receiver"]["link_transmitters"][0]
report_name = scenario_metadata["receivers"]["eve_receiver"]["receiver_parent"] + "_" + scenario_metadata["receivers"]["eve_receiver"]["link_transmitters"][0]
ts_name = scenario_metadata["receivers"]["eve_receiver"]["link_transmitters"][0]
dem = scenario_metadata["receivers"]["eve_receiver"]["dem"]
rs_name = scenario_metadata["receivers"]["eve_receiver"]["name"]
rs_sat_name = scenario_metadata["receivers"]["eve_receiver"]["receiver_parent"]
ts_gs_name = scenario_metadata["receivers"]["eve_receiver"]["link_transmitters"][0]
Access[acces_name] = Transmitters[ts_name].transmitter.GetAccessToObject(Receivers[rs_name].receptor)
Access[acces_name].ComputeAccess()

new_start_time, new_stop_time, new_access_times = TimeSync(accessStartTime_1=accessStartTime, accessStopTime_1=accessStopTime,duration_1= duration_1, link=Access[acces_name], StartTime=scenario2.StartTime, StopTime=scenario2.StopTime, StepTime=StepTime)   

aer_elements = ["Access Number", "Azimuth", "Elevation", "Range"]
AER_data = stk_api.get_all_access_link_data(Access[acces_name_sc1a], "AER Data", "Default", accessStartTime, accessStopTime, StepTime, aer_elements)

li_elements = ["Time", 'C/No', 'Eb/No', "BER", "Range", "EIRP", "Free Space Loss", "Xmtr Elevation", "Xmtr Azimuth", "Xmtr Gain", "Xmtr Power", "Rcvd. Iso. Power", "Carrier Power at Rcvr Input"]
LinkInfo = stk_api.get_all_access_link_data(Access[acces_name_sc1a], "Link Information", 0, accessStartTime, accessStopTime, StepTime, li_elements)

pv_elements = ["x", "y", "z", "xVel", "yVel", "zVel", "RelSpeed"]
PositionVelocity = stk_api.get_all_access_link_data(Access[acces_name_sc1a], "To Position Velocity", "J2000", accessStartTime, accessStopTime, StepTime, pv_elements)

lla_elements = ["Lat", "Lon", "Alt"]
LLAState = stk_api.get_all_access_link_data(Satellites[rs_sat_name_sc1a].sat, "LLA State", "Fixed", accessStartTime, accessStopTime, StepTime, lla_elements)

to_join_dict = (AER_data, LinkInfo, PositionVelocity, LLAState)
tabla =  defaultdict(list) 

for dicts in to_join_dict:
    for key, vals in dicts.items():
        tabla[key] = vals

reporte = pd.DataFrame(tabla)

reporte.to_excel("Reports/PruebaAPI"".xlsx")
obs_table = defaultdict(list)

for i, times in enumerate(new_access_times):
    obs = stk_api.get_instantaneous_link_data(Access[acces_name_sc1a], "To Position Velocity", "J2000", times, pv_elements ,"List")
    print(obs)
    #for key, vals in obs.items():
    #    obs_table[key].append(vals[0])
    Antennas[ts_an_name].set_azelorientation(i*4, i*2, 0)
    if i>10:
        break

#obs_reporte = pd.DataFrame(obs_table)

#obs_reporte.to_excel("Reports/PruebaObs"".xlsx")