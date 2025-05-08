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

##    4. Set dict to contain stkobject interface for later use.
STKPropagators = {
    0: STKObjects.IAgVePropagatorHPOP,
    1: STKObjects.IAgVePropagatorJ2Perturbation,
    2: STKObjects.IAgVePropagatorJ4Perturbation,
    3: STKObjects.IAgVePropagatorLOP,
    4: STKObjects.IAgVePropagatorSGP4,
    5: STKObjects.IAgVePropagatorSPICE,
    6: STKObjects.IAgVePropagatorStkExternal,
    7: STKObjects.IAgVePropagatorTwoBody,
    8: STKObjects.IAgVePropagatorUserExternal,
    9: STKObjects.IAgVePropagatorGreatArc,
    10: STKObjects.IAgVePropagatorBallistic,
    11: STKObjects.IAgVePropagatorSimpleAscent,
    12: 0,
    13: STKObjects.IAgVePropagatorRealtime,
    14: 0,
    15: STKObjects.IAgVePropagatorAviator,
    16: STKObjects.IAgVePropagator11Param,
    17: STKObjects.IAgVePropagatorSP3
}

######################################
##    Task 3
##    Define functions to set stk objects  

##    1. Add a facility object to the scenario
def GroundStation(root,obj_type, name, unit, use_terrain, lat, lon, alt):
    groundStation = root.CurrentScenario.Children.New(obj_type, name)
    groundStation_QI = groundStation.QueryInterface(STKObjects.IAgFacility)
    root.UnitPreferences.Item('LatitudeUnit').SetCurrentUnit(unit)
    root.UnitPreferences.Item('LongitudeUnit').SetCurrentUnit(unit)
    groundStation_QI.UseTerrain = use_terrain
    groundStation_QI.Position.AssignGeodetic(lat, lon, alt)
    return groundStation

##    2. Add the Satellites objects to the scenario
def Satellite(root, obj_type, name, prop_type):
    sat = root.CurrentScenario.Children.New(obj_type, name)
    sat_QI = sat.QueryInterface(STKObjects.IAgSatellite)
    sat_QI.SetPropagatorType(prop_type)
    return sat

##    3. Set the Satellites propagator
def SetSatellitePropagator(root, sat_QI, prop_interface, scc_num, bool_file, file_name, auto_update):
    sat_propagator = sat_QI.Propagator
    sat_propagator_QI = sat_propagator.QueryInterface(STKPropagators[prop_interface])
    sat_propagator_QI.EphemerisInterval.SetImplicitInterval(root.CurrentScenario.Vgt.EventIntervals.Item("AnalysisInterval"))
    if(bool_file):
        sat_propagator_QI.CommonTasks.AddSegsFromFile(scc_num, file_name)
    else:
        sat_propagator_QI.CommonTasks.AddSegsFromOnlineSource(scc_num)
    sat_propagator_QI.AutoUpdateEnabled = auto_update
    sat_propagator_QI.Propagate()    
    return sat_propagator

##    4. Set the Satellites Attitude to basic
def SetSatelliteBasicAttitude(sat_qi):
    sat_attitude = sat_qi.Attitude
    sat_attitude_QI = sat_attitude.QueryInterface(STKObjects.IAgVeOrbitAttitudeStandard)
    sat_basic = sat_attitude_QI.Basic
    sat_basic.SetProfileType(6)
    sat_basic_profile = sat_basic.Profile

##    5. Add the Transmitters objects to the scenario
def SetTransmitter(stk_obj, obj_type, name, model, dem, auto_scale_bandwidth, freq, power, data_rate, antenna_control):
    transmitter = stk_obj.Children.New(obj_type, name)
    transmitter_QI = transmitter.QueryInterface(STKObjects.IAgTransmitter)
    transmitter_QI.SetModel(model)
    txModel = transmitter_QI.Model
    txModel_QI = txModel.QueryInterface(STKObjects.IAgTransmitterModelComplex)
    txModel_QI.SetModulator(dem)
    txModel_QI.Modulator.AutoScaleBandwidth = auto_scale_bandwidth
    txModel_QI.Frequency = freq
    txModel_QI.Power = power
    txModel_QI.DataRate = data_rate
    txModel_QI.AntennaControl.ReferenceType = antenna_control
    txModel_QI.AntennaControl.LinkedAntennaObject
    return transmitter

##    6. Add the Receptors objects to the scenario
def SetReceptor(stk_object, obj_type, name, model, auto_select_modulator, dem):
    receptor = stk_object.Children.New(obj_type, name)
    receptor_QI = receptor.QueryInterface(STKObjects.IAgReceiver)
    receptor_QI.SetModel(model)
    receptor_model = receptor_QI.Model
    receptor_model_QI = receptor_model.QueryInterface(STKObjects.IAgReceiverModelSimple)
    receptor_model_QI.AutoSelectDemodulator = auto_select_modulator
    receptor_model_QI.SetDemodulator(dem)
    return receptor

##    6. Add the Antenna objects to the scenario
def SetAntenna(stk_obj, obj_type, name, model, diameter, computer_main_lobe_gain, freq, Elv):
    antenna = stk_obj.Children.New(obj_type, name)
    antenna_QI = antenna.QueryInterface(STKObjects.IAgAntenna)
    antenna_QI.SetModel(model)
    antennaModel = antenna_QI.Model
    antennaModel_QI = antennaModel.QueryInterface(STKObjects.IAgAntennaModelApertureCircularBessel)
    antennaModel_QI.Diameter = diameter
    antennaModel_QI.ComputerMainlobeGain = computer_main_lobe_gain
    antennaModel_QI.DesignFrequency = freq
    antennaOrientation = antenna_QI.Orientation
    antennaOrientation.AssignAzEl(0, Elv, 1)
    return antenna


        
# Get the entity parameters from the scenario file and initialize the entities.
Satellites = {}
Propagators = {}
sat_idx = 0
for sat in scenario_metadata['satellites']:  
    sat_idx += 1
    Satellites[scenario_metadata["satellites"][sat]["name"]] = Satellite(root, 18, scenario_metadata["satellites"][sat]["name"], scenario_metadata["satellites"][sat]["propagator_type"])
    Propagators[scenario_metadata["satellites"][sat]["name"]] = SetSatellitePropagator(root, Satellites[scenario_metadata["satellites"][sat]["name"]].QueryInterface(STKObjects.IAgSatellite), scenario_metadata["satellites"][sat]["propagator_type"],
                                                                                       scenario_metadata["satellites"][sat]["propagator_params"]["scc"],
                                                                                       scenario_metadata["satellites"][sat]["propagator_params"]["tle_from_file"],
                                                                                       scenario_metadata["satellites"][sat]["propagator_params"]["tle_file"],
                                                                                        True)
    SetSatelliteBasicAttitude(Satellites[scenario_metadata["satellites"][sat]["name"]].QueryInterface(STKObjects.IAgSatellite))


GroundStations = {}
gs_idx = 0
for gs in scenario_metadata['ground_stations']:  
    gs_idx += 1
    GroundStations[scenario_metadata["ground_stations"][gs]["name"]] = GroundStation(root, 8, scenario_metadata["ground_stations"][gs]["name"], scenario_metadata["ground_stations"][gs]["lat_long_unit"], 
                                                                                     scenario_metadata["ground_stations"][gs]["use_terrain"], scenario_metadata["ground_stations"][gs]["lat"],
                                                                                     scenario_metadata["ground_stations"][gs]["long"], scenario_metadata["ground_stations"][gs]["alt"])

Antennas = {}
an_idx = 0
for an in scenario_metadata["antennas"]:
    an_idx += 1
    Antennas[scenario_metadata["antennas"][an]["name"]] = SetAntenna(GroundStations[scenario_metadata["antennas"][an]["antenna_parent"]], 31, scenario_metadata["antennas"][an]["name"],
                                                                     scenario_metadata["antennas"][an]["model"], scenario_metadata["antennas"][an]["diameter"],
                                                                     scenario_metadata["antennas"][an]["computer_main_lobe_gain"], scenario_metadata["antennas"][an]["freq"],
                                                                     scenario_metadata["antennas"][an]["Elv"])

Transmitters = {}
ts_idx = 0
for ts in scenario_metadata['transmitters']:
    ts_idx += 1  
    Transmitters[scenario_metadata["transmitters"][ts]["name"]] = SetTransmitter(GroundStations[scenario_metadata["transmitters"][ts]["transmitter_parent"]], 24, scenario_metadata["transmitters"][ts]["name"],
                                                                                 scenario_metadata["transmitters"][ts]["model"],
                                                                                 scenario_metadata["transmitters"][ts]["dem"],
                                                                                 scenario_metadata["transmitters"][ts]["auto_scale_bandwidth"],
                                                                                 scenario_metadata["transmitters"][ts]["freq"], scenario_metadata["transmitters"][ts]["power"],
                                                                                 scenario_metadata["transmitters"][ts]["data_rate"], scenario_metadata["transmitters"][ts]["antenna_control"])

Receivers = {}
rs_idx = 0
for rs in scenario_metadata['receivers']:  
    rs_idx += 1
    Receivers[scenario_metadata["receivers"][rs]["name"]] = SetReceptor(Satellites[scenario_metadata["receivers"][rs]["receiver_parent"]], 17, scenario_metadata["receivers"][rs]["name"],
                                                                        scenario_metadata["receivers"][rs]["receiver_type"], 
                                                                        scenario_metadata["receivers"][rs]["auto_select_modulator"], scenario_metadata["receivers"][rs]["dem"])


######################################
##    Task 4
##    2. Retrive and view the altitud of the satellite during an access interval.

def commLinkInfoTable(link, StartTime, StopTime, Step, TableName):
    access_data = link.DataProviders.Item("Access Data")
    access_data_query  = access_data.QueryInterface(STKObjects.IAgDataPrvInterval)
    access_data_results = access_data_query.Exec(StartTime, StopTime)
    accessStartTime = access_data_results.DataSets.GetDataSetByName('Start Time').GetValues()
    accessStopTime  = access_data_results.DataSets.GetDataSetByName('Stop Time').GetValues()
    LinkInfo = link.DataProviders.Item("Link Information")
    LinkInfo_TimeVar        = LinkInfo.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    rptElements       = ['C/No', 'Eb/No', "BER"]
    accessCNo               = []
    accessEbNo              = []
    accessBER               = []
    for i in range(len(accessStartTime)):
        LinkInfo_results = LinkInfo_TimeVar.ExecElements( accessStartTime[i], accessStopTime[i], Step, rptElements)
        CNo = list(LinkInfo_results.DataSets.GetDataSetByName('C/No').GetValues())
        EbNo = list(LinkInfo_results.DataSets.GetDataSetByName('Eb/No').GetValues())
        BER = list(LinkInfo_results.DataSets.GetDataSetByName('BER').GetValues())
        for j in range(len(CNo)):
            accessCNo.append(CNo[j])
            accessEbNo.append(EbNo[j])
            accessBER.append(BER[j])
        
    tabla = {
            "C_No": accessCNo,
            "EB_NO": accessEbNo,
            "BER": accessBER
            }
    
    reporte = pd.DataFrame(tabla)
    reporte.to_excel(TableName+".xlsx")
            
Access = {}    

for rec in scenario_metadata["receivers"]:
    if scenario_metadata["receivers"][rec]["link_bool"] == True:
        for ts in range(len(scenario_metadata["receivers"][rec]["link_transmitters"])):
            acces_name = scenario_metadata["receivers"][rec]["receiver_parent"] + "_acces_" + scenario_metadata["receivers"][rec]["link_transmitters"][ts]
            report_name = scenario_metadata["receivers"][rec]["receiver_parent"] + "_" + scenario_metadata["receivers"][rec]["link_transmitters"][ts]
            Access[acces_name] = Receivers[scenario_metadata["receivers"][rs]["name"]].GetAccessToObject(Transmitters[scenario_metadata["receivers"][rec]["link_transmitters"][ts]])
            Access[acces_name].ComputeAccess()
            commLinkInfoTable(link=Access[acces_name], StartTime=scenario2.StartTime, StopTime=scenario2.StopTime, Step=StepTime, TableName=report_name)
        



