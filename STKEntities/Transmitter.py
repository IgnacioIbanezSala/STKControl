from comtypes.gen import STKObjects

class STKTransmitter():
    def __init__(self, root, name, parent, model, dem, auto_scale_bandwidth, freq, power, data_rate, antenna_control):
        self.transmitter = parent.Children.New(24, name)
        transmitter_QI = self.transmitter.QueryInterface(STKObjects.IAgTransmitter)
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
    