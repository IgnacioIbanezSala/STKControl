from comtypes.gen import STKObjects


class Stk_Satellite():
    def __init__(self, root, name):
        self.root = root
        self.name = name
        self.sat = root.CurrentScenario.Children.New(18, name)
        self.sat_QI = self.sat.QueryInterface(STKObjects.IAgSatellite)
        pass

    def SetSatellitePropagator_and_BasicAttitude(self, root, scc_num, bool_file, file_name, auto_update):
        self.sat_QI.SetPropagatorType(4)
        sat_propagator = self.sat_QI.Propagator
        sat_propagator_QI = sat_propagator.QueryInterface(STKObjects.IAgVePropagatorSGP4)
        sat_propagator_QI.EphemerisInterval.SetImplicitInterval(root.CurrentScenario.Vgt.EventIntervals.Item("AnalysisInterval"))
        if(bool_file):
            sat_propagator_QI.CommonTasks.AddSegsFromFile(scc_num, file_name)
        else:
            sat_propagator_QI.CommonTasks.AddSegsFromOnlineSource(scc_num)
        sat_propagator_QI.AutoUpdateEnabled = auto_update
        sat_propagator_QI.Propagate()    
        
        
        sat_attitude = self.sat_QI.Attitude
        sat_attitude_QI = sat_attitude.QueryInterface(STKObjects.IAgVeOrbitAttitudeStandard)
        sat_basic = sat_attitude_QI.Basic
        sat_basic.SetProfileType(6)
        sat_basic_profile = sat_basic.Profile
