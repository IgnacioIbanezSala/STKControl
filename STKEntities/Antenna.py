from comtypes.gen import STKObjects

class STKAntenna():
    def __init__(self, name, parent, model, diameter, computer_main_lobe_gain, freq, Elv):
        self.antenna = parent.Children.New(31, name)
        antenna_QI = self.antenna.QueryInterface(STKObjects.IAgAntenna)
        antenna_QI.SetModel(model)
        antennaModel = antenna_QI.Model
        antennaModel_QI = antennaModel.QueryInterface(STKObjects.IAgAntennaModelParabolic)
        antennaModel_QI.Diameter = diameter
        antennaModel_QI.ComputerMainlobeGain = computer_main_lobe_gain
        antennaModel_QI.DesignFrequency = freq
        antennaOrientation = antenna_QI.Orientation
        antennaOrientation.AssignAzEl(0, Elv, 1)
        