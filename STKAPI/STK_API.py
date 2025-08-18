from comtypes.gen import STKObjects
from collections import defaultdict

def get_access_times(link, scenario_I):
    access_data = link.DataProviders.Item('Access Data')
    access_data_I = access_data.QueryInterface(STKObjects.IAgDataPrvInterval)
    access_data_R = access_data_I.Exec(scenario_I.StartTime, scenario_I.StopTime)
    accessStartTimes = access_data_R.DataSets.GetDataSetByName('Start Time').GetValues()
    accessStopTimes  = access_data_R.DataSets.GetDataSetByName('Stop Time').GetValues()
    accessDurations = access_data_R.DataSets.GetDataSetByName('Duration').GetValues()

    return accessStartTimes, accessStopTimes, accessDurations

def get_access_time(link, access_idx, longest, scenario_I):
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
    link_data = defaultdict(list)
    current_link_data = defaultdict(list)
    for start, stop in zip(start_time, stop_time):
        current_link_data = get_link_data(link, item, group, start, stop, step, elements)
        for j in range(len(current_link_data[elements[0]])):
            for key, vals in current_link_data.items():
                link_data[key].append(vals[j])
    
    return link_data

def get_instantaneous_link_data(link, item, group, time, elements, format):
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
    else:
        return link_data



