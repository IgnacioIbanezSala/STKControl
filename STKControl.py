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

######################################
##    Task 3
##    Define functions to set stk objects  

def SetSensor(stk_obj, obj_type, name, target_name):
    sensor = stk_obj.Children.New(obj_type, name)
    sensor_QI = sensor.QueryInterface(STKObjects.IAgSensor)
    targeted_sensor = sensor_QI.CommonTasks.SetPointingTargetedTracking(0x2, 0x1, "E:/Celina/STKControl/AreaTarget1")
    targeted_sensor_QI = targeted_sensor.QueryInterface(STKObjects.IAgSnPtTargeted)
    targets = targeted_sensor_QI.Targets
    targets_QI = targets.QueryInterface(STKObjects.IAgSnTargetCollection)
    for tg in range(len(target_name)):
        targets_QI.Add(target_name[tg])
        
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
    #Sensors[scenario_metadata["sensors"][ss]["name"]] = SetSensor(Satellites[scenario_metadata["sensors"][ss]["sensor_parent"]], 20, scenario_metadata["sensors"][ss]["name"],
    #                                                              scenario_metadata["sensors"][ss]["sensor_targets"])

######################################
##    Task 4
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
    #, "Azymuth", "Elevation", "Range"
    AERrptElements    = ["Access Number", "Azimuth", "Elevation", "Range"]
    
    LinkInfo = link.DataProviders.Item("Link Information")
    LinkInfo_TimeVar        = LinkInfo.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    rptElements       = ["Time", 'C/No', 'Eb/No', "BER", "Range", "Xmtr Elevation", "Xmtr Azimuth"]
    
    PositionVelocityInfo = link.DataProviders.Item("To Position Velocity")
    PositionVelocityInfo_TimeVar = PositionVelocityInfo.QueryInterface(STKObjects.IAgDataProviderGroup)
    ToPositionVel_Group   = PositionVelocityInfo_TimeVar.Group
    ToPositionVel_ICRF      = ToPositionVel_Group.Item('ICRF')
    ToPositionVel_TimeVar   = ToPositionVel_ICRF.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    PVrptElements     = ["x", "y", "z", "xVel", "yVel", "zVel", "RelSpeed"]
    
    accessNumber            = []
    accessAzimuth           = []
    accessElevation         = []
    accessRangeAER          = []
    accessTime              = []
    accessCNo               = []
    accessEbNo              = []
    accessBER               = []
    accessRange             = []
    accessXmtrElevation     = []
    accessXmtrAzimuth       = []
    accessx                 = []
    accessy                 = []
    accessz                 = []
    accessVx                = []
    accessVy                = []
    accessVz                = []
    accessRelSpeed          = []
    for i in range(len(accessStartTime)):
        LinkInfo_results = LinkInfo_TimeVar.ExecElements( accessStartTime[i], accessStopTime[i], Step, rptElements)
        PositionVelocityInfo_results = ToPositionVel_TimeVar.ExecElements(accessStartTime[i], accessStopTime[i], Step, PVrptElements)
        AER_data_results = AERdata_TimeVar.ExecElements(accessStartTime[i], accessStopTime[i], Step, AERrptElements)
        AccessNumber = AER_data_results.DataSets.GetDataSetByName('Access Number').GetValues()
        Azimuth = list(AER_data_results.DataSets.GetDataSetByName('Azimuth').GetValues())
        
        Elevation = list(AER_data_results.DataSets.GetDataSetByName('Elevation').GetValues())
        RangeAER = list(AER_data_results.DataSets.GetDataSetByName('Range').GetValues())
        Time = list(LinkInfo_results.DataSets.GetDataSetByName('Time').GetValues())
        CNo = list(LinkInfo_results.DataSets.GetDataSetByName('C/No').GetValues())
        EbNo = list(LinkInfo_results.DataSets.GetDataSetByName('Eb/No').GetValues())
        BER = list(LinkInfo_results.DataSets.GetDataSetByName('BER').GetValues())
        Range = list(LinkInfo_results.DataSets.GetDataSetByName('Range').GetValues())
        XmtrElevation = list(LinkInfo_results.DataSets.GetDataSetByName('Xmtr Elevation').GetValues())
        XmtrAzimuth = list(LinkInfo_results.DataSets.GetDataSetByName('Xmtr Azimuth').GetValues())
        x = list(PositionVelocityInfo_results.DataSets.GetDataSetByName('x').GetValues())
        y = list(PositionVelocityInfo_results.DataSets.GetDataSetByName('y').GetValues())
        z = list(PositionVelocityInfo_results.DataSets.GetDataSetByName('z').GetValues())
        Vx = list(PositionVelocityInfo_results.DataSets.GetDataSetByName('xVel').GetValues())
        Vy = list(PositionVelocityInfo_results.DataSets.GetDataSetByName('yVel').GetValues())
        Vz = list(PositionVelocityInfo_results.DataSets.GetDataSetByName('zVel').GetValues())
        RelSpeed = list(PositionVelocityInfo_results.DataSets.GetDataSetByName('RelSpeed').GetValues())
        for j in range(len(CNo)):
            accessAzimuth.append(Azimuth[j])
            accessElevation.append(Elevation[j])
            accessRangeAER.append(RangeAER[j])
            accessTime.append(Time[j])
            accessCNo.append(CNo[j])
            accessEbNo.append(EbNo[j])
            accessBER.append(BER[j])
            accessRange.append(Range[j])
            accessXmtrElevation.append(XmtrElevation[j])
            accessXmtrAzimuth.append(XmtrAzimuth)
            accessx.append(x[j])
            accessy.append(y[j])
            accessz.append(z[j])
            accessVx.append(Vx[j])
            accessVy.append(Vy[j])
            accessVz.append(Vz[j])
            accessRelSpeed.append(RelSpeed[j])
            accessNumber.append(i)
    tabla = {
            "Acces Number": accessNumber,
            "Time": accessTime,
            "C_No": accessCNo,
            "EB_NO": accessEbNo,
            "BER": accessBER,
            "Azimuth": accessAzimuth,
            "Elevation": accessElevation,
            "Range AER": accessRangeAER,
            "Range": accessRange,
            "Xmtr Elevation": accessXmtrElevation,
            "Xmtr Azimuth": accessXmtrAzimuth,
            "X": accessx,
            "y": accessy,
            "z": accessz,
            "Vx": accessVx,
            "Vy": accessVy,
            "Vz": accessVz,
            "RelSpeed": accessRelSpeed 
            }
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
        
            


