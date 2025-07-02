from comtypes.gen import STKObjects

class STKGroundStation():
    def __init__(self, root, name, unit, use_terrain, lat, lon, alt):
        self.groundStation = root.CurrentScenario.Children.New(8, name)
        groundStation_QI = self.groundStation.QueryInterface(STKObjects.IAgFacility)
        root.UnitPreferences.Item('LatitudeUnit').SetCurrentUnit(unit)
        root.UnitPreferences.Item('LongitudeUnit').SetCurrentUnit(unit)
        groundStation_QI.UseTerrain = use_terrain
        groundStation_QI.Position.AssignGeodetic(lat, lon, alt)
        pass