from comtypes.gen import STKObjects

class STKAntenna():
    def __init__(self, name, parent, model, diameter, computer_diameter, freq):
        self.antenna = parent.Children.New(31, name)
        antenna_QI = self.antenna.QueryInterface(STKObjects.IAgAntenna)
        antenna_QI.SetModel(model)
        antennaModel = antenna_QI.Model
        antennaModel_QI = antennaModel.QueryInterface(STKObjects.IAgAntennaModelParabolic)
        antennaModel_QI.Diameter = diameter
        antennaModel_QI.ComputerDiameter = computer_diameter
        antennaModel_QI.DesignFrequency = freq
        self.antennaOrientation = antenna_QI.Orientation

        
    def set_azelorientation(self, az, elv, boresight_rotate):
        self.antennaOrientation.AssignAzEl(az, elv, boresight_rotate)

    def get_azelorientation(self):
        return self.antennaOrientation.QueryAzEl()