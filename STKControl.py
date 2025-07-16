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
f_idx = open('Scenarios/EVE_SC1A_SC1B.json')
scenario_metadata = json.load(f_idx)

ScenarioName  = scenario_metadata["Scenario"]["name"]
StartTime   = scenario_metadata["time constraints"]["start time"]
StopTime     = scenario_metadata["time constraints"]["stop time"]
StepTime      = scenario_metadata["time constraints"]["step"]

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
    computer_main_lobe_gain = scenario_metadata["antennas"][an]["computer_main_lobe_gain"]
    freq = scenario_metadata["antennas"][an]["freq"]
    Elv = scenario_metadata["antennas"][an]["Elv"]
    Antennas[an_name] = STKEntities.STKAntenna(an_name, GroundStations[parent_name].groundStation, model, diameter, computer_main_lobe_gain, freq, Elv) 

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
    Receivers[rs_name] = STKEntities.STKReceptor(rs_name, Satellites[parent_name].sat, model, auto_select_modulator, dem)

Sensors = {}
ss_idx = 0
for ss in scenario_metadata['sensors']:
    ss_idx += 1
    ss_name = scenario_metadata["sensors"][ss]["name"]
    ss_parent = scenario_metadata["sensors"][ss]["sensor_parent"]
    targets = scenario_metadata["sensors"][ss]["sensor_targets"]
    Sensors[ss_name] = STKEntities.STKTargetedSensor(ss_name, GroundStations[ss_parent].groundStation, Satellites[targets[0]].sat.Path)
    for i in range(1, len(targets)):
        Sensors[ss_name].add_target(Satellites[targets[i]].sat)
    

######################################
##    Task 3
##    2. Retrive and view the altitud of the satellite during an access interval.

def commLinkInfoTable(link, StartTime, StopTime, Step, TableName):
    access_data = link.DataProviders.Item('Access Data')
    access_data_query  = access_data.QueryInterface(STKObjects.IAgDataPrvInterval)
    access_data_results = access_data_query.Exec(StartTime, StopTime)
    accessStartTime = access_data_results.DataSets.GetDataSetByName('Start Time').GetValues()
    accessStopTime  = access_data_results.DataSets.GetDataSetByName('Stop Time').GetValues()
    
    AER_data = link.DataProviders.Item("AER Data")
    AER_data_query = AER_data.QueryInterface(STKObjects.IAgDataProviderGroup)
    AERdata_Group           = AER_data_query.Group
    AERdata_Default         = AERdata_Group.Item('Default')
    AERdata_TimeVar         = AERdata_Default.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    AERrptElements    = ["Access Number", "Azimuth", "Elevation", "Range"]
    
    LinkInfo = link.DataProviders.Item("Link Information")
    LinkInfo_TimeVar        = LinkInfo.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    rptElements       = ["Time", 'C/No', 'Eb/No', "BER", "Range", "EIRP", "Free Space Loss", "Xmtr Elevation", "Xmtr Azimuth", "Xmtr Gain", "Xmtr Power"]
    
    PositionVelocityInfo = link.DataProviders.Item("To Position Velocity")
    PositionVelocityInfo_TimeVar = PositionVelocityInfo.QueryInterface(STKObjects.IAgDataProviderGroup)
    ToPositionVel_Group   = PositionVelocityInfo_TimeVar.Group
    ToPositionVel_ICRF      = ToPositionVel_Group.Item('J2000')
    ToPositionVel_TimeVar   = ToPositionVel_ICRF.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    PVrptElements     = ["x", "y", "z", "xVel", "yVel", "zVel", "RelSpeed"]
    
    tabla = defaultdict(list)

    access_data = {}

    for start_time, stop_time in zip(accessStartTime, accessStopTime):
        LinkInfo_results = LinkInfo_TimeVar.ExecElements(start_time, stop_time, Step, rptElements)
        PositionVelocityInfo_results = ToPositionVel_TimeVar.ExecElements(start_time, stop_time, Step, PVrptElements)
        AER_data_results = AERdata_TimeVar.ExecElements(start_time, stop_time, Step, AERrptElements)
        for element in AERrptElements:
            access_data[element] = list(AER_data_results.DataSets.GetDataSetByName(element).GetValues())
        
        for element in rptElements:
            access_data[element] = list(LinkInfo_results.DataSets.GetDataSetByName(element).GetValues())
            
        for element in PVrptElements:
            access_data[element] = list(PositionVelocityInfo_results.DataSets.GetDataSetByName(element).GetValues())

        for j in range(AER_data_results.DataSets.GetDataSetByName('Access Number').Count):
            for key, vals in access_data.items():
                tabla[key].append(vals[j])
    
    reporte = pd.DataFrame(tabla)
    reporte.to_excel("Reports/" + TableName+".xlsx")
    reporte.to_csv("Reports/" + TableName+".csv")
            
Access = {}    

for rec in scenario_metadata["receivers"]:
    if scenario_metadata["receivers"][rec]["link_bool"] == True:
        for ts in range(len(scenario_metadata["receivers"][rec]["link_transmitters"])):
            acces_name = scenario_metadata["receivers"][rec]["receiver_parent"] + "_acces_" + scenario_metadata["receivers"][rec]["link_transmitters"][ts]
            report_name = scenario_metadata["receivers"][rec]["receiver_parent"] + "_" + scenario_metadata["receivers"][rec]["link_transmitters"][ts]
            
            Access[acces_name] = Transmitters[scenario_metadata["receivers"][rec]["link_transmitters"][ts]].transmitter.GetAccessToObject(Receivers[scenario_metadata["receivers"][rec]["name"]].receptor)
            Access[acces_name].ComputeAccess()
            commLinkInfoTable(link=Access[acces_name], StartTime=scenario2.StartTime, StopTime=scenario2.StopTime, Step=StepTime, TableName=report_name)
        
            


