from comtypes.gen import STKObjects

class STKReceptor():
    def __init__(self, name, parent, model, auto_select_modulator, dem, antenna_control):
        self.receptor = parent.Children.New(17, name)
        receptor_QI = self.receptor.QueryInterface(STKObjects.IAgReceiver)
        receptor_QI.SetModel(model)
        receptor_model = receptor_QI.Model
        receptor_model_QI = receptor_model.QueryInterface(STKObjects.IAgReceiverModelSimple)
        receptor_model_QI.AutoSelectDemodulator = auto_select_modulator
        receptor_model_QI.SetDemodulator(dem)
        #receptor_model_QI.AntennaControl.ReferenceType = antenna_control
        