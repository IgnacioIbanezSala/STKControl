from comtypes.gen import STKObjects

class STKTargetedSensor():
    def __init__(self, name, parent, target_path):
        self.sensor = parent.Children.New(20, name)
        sensor_QI = self.sensor.QueryInterface(STKObjects.IAgSensor)
        sensor_QI.SetPointingType(0x5)    
        targeted_sensor = sensor_QI.CommonTasks.SetPointingTargetedTracking(0x2, 0x1, target_path)
        targeted_sensor_QI = targeted_sensor.QueryInterface(STKObjects.IAgSnPtTargeted)
        self.targets = targeted_sensor_QI.Targets

    def add_target(self, target_path):
        targets_QI = self.targets.QueryInterface(STKObjects.IAgSnTargetCollection)
        targets_QI.AddObject(target_path)
        
    