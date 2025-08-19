from comtypes.gen import STKObjects
from collections import defaultdict

def get_access_times(link, scenario_I):
    """
    Returns lists containing all start times, stop times and durations from all access

    Parameters
    ----------
    link : IAgStkAccess
        Access between two StkObjects
    
    scenario_I: IAgScenario Interface
        The interface of the Stk scenario
    
    """
    access_data = link.DataProviders.Item('Access Data')
    access_data_I = access_data.QueryInterface(STKObjects.IAgDataPrvInterval)
    access_data_R = access_data_I.Exec(scenario_I.StartTime, scenario_I.StopTime)
    accessStartTimes = access_data_R.DataSets.GetDataSetByName('Start Time').GetValues()
    accessStopTimes  = access_data_R.DataSets.GetDataSetByName('Stop Time').GetValues()
    accessDurations = access_data_R.DataSets.GetDataSetByName('Duration').GetValues()

    return accessStartTimes, accessStopTimes, accessDurations

def get_access_time(link, access_idx, scenario_I, longest = False):
    """
    Returns the start time and stop time of a single access

    Parameters
    ----------
    link : IAgStkAccess
        Access between two StkObjects
    
    access_idx: int
        Index of the access
    
    scenario_I: IAgScenario Interface
        The interface of the Stk scenario
        
    longest: Bool
        If true return the start time and stop time of the longest duration access (default is False)
             
    """
    access_data = link.DataProviders.Item('Access Data')
    access_data_I = access_data.QueryInterface(STKObjects.IAgDataPrvInterval)
    access_data_R = access_data_I.Exec(scenario_I.StartTime, scenario_I.StopTime)
    accessStartTimes = access_data_R.DataSets.GetDataSetByName('Start Time').GetValues()
    accessStopTimes  = access_data_R.DataSets.GetDataSetByName('Stop Time').GetValues()
    accessDurations = access_data_R.DataSets.GetDataSetByName('Duration').GetValues()

    accessStartTime = 0
    accessStopTime = 0

    if longest == True:
        new_duration = 0
        longest_duration_idx = 0
        for i, duration in enumerate(accessDurations):
            if i==0:
                new_duration = duration
            else:
                if duration > new_duration:
                    new_duration = duration
                    longest_duration_idx = i
        accessStartTime = accessStartTimes[longest_duration_idx]
        accessStopTime = accessStopTimes[longest_duration_idx]
    else:
        accessStartTime = accessStartTimes[access_idx]
        accessStopTime = accessStopTimes[access_idx]

    return accessStartTime, accessStopTime

def get_link_data(link, item, group, start_time, stop_time, step, elements):
    """
    Returns a dictionary containing the data corresponding to the elements in a time interval

    Parameters
    ----------
    link : IAgStkAccess
        Access between two StkObjects

    item : String
        Item whose data will be returned

    group : String
        Item group in case it has one

    start_time: String
        start of the time interval
    
    stop_time: String
        stop of the time interval

    step: String
        definition of the interval

    elements : list
        list containing the elements of the item whose data will be returned
    
    """
    link_data = link.DataProviders.Item(item)
    is_group = link_data.IsGroup()
    if is_group == True:
        link_data_I = link_data.QueryInterface(STKObjects.IAgDataProviderGroup)
        link_data_Group = link_data_I.Group.Item(group)
        link_data_I = link_data_Group.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    else:
        link_data_I = link_data.QueryInterface(STKObjects.IAgDataPrvTimeVar)

    link_data = defaultdict(list)
    link_current_data = {}
    
    link_data_results = link_data_I.ExecElements(start_time, stop_time, step, elements)
    for element in elements:
        link_current_data[element] = list(link_data_results.DataSets.GetDataSetByName(element).GetValues())
    for j in range(link_data_results.DataSets.GetDataSetByName(elements[0]).Count):
        for key, vals in link_current_data.items():
            link_data[key].append(vals[j])
    
    return link_data

def get_all_access_link_data(link, item, group, start_time, stop_time, step, elements):
    """
    Returns a dictionary containing all data corresponding to the elements through all access

    Parameters
    ----------
    link : IAgStkAccess
        Access between two StkObjects

    item : String
        Item whose data will be returned

    group : String
        Item group in case it has one

    start_time: list
        list containing all start times the access
    
    stop_time: list
        list containing all stop times the access

    step: String
        definition of the interval

    elements : list
        list containing the elements of the item whose data will be returned
    
    """    
    link_data = defaultdict(list)
    current_link_data = defaultdict(list)
    for start, stop in zip(start_time, stop_time):
        current_link_data = get_link_data(link, item, group, start, stop, step, elements)
        for j in range(len(current_link_data[elements[0]])):
            for key, vals in current_link_data.items():
                link_data[key].append(vals[j])
    
    return link_data

def get_instantaneous_link_data(link, item, group, time, elements, format="Dict"):
    """
    Returns a dictionary or list containing data corresponding to the elements at the specified time

    Parameters
    ----------
    link : IAgStkAccess
        Access between two StkObjects

    item : String
        Item whose data will be returned

    group : String
        Item group in case it has one

    time: String
    
    elements : list
        list containing the elements of the item whose data will be returned
    
    format : String
        format of the return (default is Dict)
    """    
    link_data = link.DataProviders.Item(item)
    is_group = link_data.IsGroup()
    if is_group == True:
        link_data_I = link_data.QueryInterface(STKObjects.IAgDataProviderGroup)
        link_data_Group = link_data_I.Group.Item(group)
        link_data_I = link_data_Group.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    else:
        link_data_I = link_data.QueryInterface(STKObjects.IAgDataPrvTimeVar)

    link_data = defaultdict(list)
    link_current_data = {}

    link_data_results = link_data_I.ExecSingleElements(time, elements)
    for element in elements:
        link_current_data[element] = list(link_data_results.DataSets.GetDataSetByName(element).GetValues())
    
    for key, vals in link_current_data.items():
        link_data[key].append(vals[0])

    if format == "List":
        link_data_list = []
        for key, vals in link_current_data.items():
            link_data_list.append(vals[0])
        return link_data_list
    if format == "Dict":
        return link_data



