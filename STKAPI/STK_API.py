from comtypes.gen import STKObjects

def get_observation(link, time, tabla):
        
    AER_data = link.DataProviders.Item("AER Data")
    AER_data_query = AER_data.QueryInterface(STKObjects.IAgDataProviderGroup)
    AERdata_Group           = AER_data_query.Group
    AERdata_Default         = AERdata_Group.Item('Default')
    AERdata_TimeVar         = AERdata_Default.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    AERrptElements    = ["Access Number", "Azimuth", "Elevation", "Range"]

    LinkInfo = link.DataProviders.Item("Link Information")
    LinkInfo_TimeVar        = LinkInfo.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    rptElements       = ["Time", 'C/No', 'Eb/No', "BER", "Range", "EIRP", "Free Space Loss", "Xmtr Elevation", "Xmtr Azimuth", "Xmtr Gain", "Xmtr Power", "Rcvd. Iso. Power", "Carrier Power at Rcvr Input"]
    
    PositionVelocityInfo = link.DataProviders.Item("To Position Velocity")
    PositionVelocityInfo_TimeVar = PositionVelocityInfo.QueryInterface(STKObjects.IAgDataProviderGroup)
    ToPositionVel_Group   = PositionVelocityInfo_TimeVar.Group
    ToPositionVel_ICRF      = ToPositionVel_Group.Item('J2000')
    ToPositionVel_TimeVar   = ToPositionVel_ICRF.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    PVrptElements     = ["x", "y", "z", "xVel", "yVel", "zVel", "RelSpeed"]
    
    access_data = {}
    obs = []
    LinkInfo_results = LinkInfo_TimeVar.ExecSingleElements(time, rptElements)
    PositionVelocityInfo_results = ToPositionVel_TimeVar.ExecSingleElements(time, PVrptElements)
    AER_data_results = AERdata_TimeVar.ExecSingleElements(time, AERrptElements)
    for element in AERrptElements:
        access_data[element] = AER_data_results.DataSets.GetDataSetByName(element).GetValues()
        obs.append(access_data[element])
    for element in rptElements:
        access_data[element] = LinkInfo_results.DataSets.GetDataSetByName(element).GetValues()
        obs.append(access_data[element])
    for element in PVrptElements:
        access_data[element] = PositionVelocityInfo_results.DataSets.GetDataSetByName(element).GetValues()
        obs.append(access_data[element])
    for key, vals in access_data.items():
        tabla[key].append(vals[0])
        obs.append(access_data[element])
    current_size = AER_data_results.DataSets.GetDataSetByName('Access Number').Count 
    
    return access_data, obs


