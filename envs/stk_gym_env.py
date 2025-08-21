import gymnasium as gym

from win32api import GetSystemMetrics
from comtypes.client import CreateObject
import pandas as pd
import json
from numpy import sqrt, power
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from comtypes.gen import STKObjects
from comtypes.gen import STKUtil
import STKEntities

import STKAPI as stk_api
import STKEntities
import Secrecy_Rates as sr
import Channel

class StkEnv(gym.Env):
    
    def __init__(self, scenario_file_path = "Scenarios/Spy_Sat_noantennareceptor.json"):
        
        self.scenario_file_path = scenario_file_path
        self.b_b = 0.005
        self.m_b = 26
        self.omega_b = 0.515
        self.beta_b = 0.5
        self.b_e = 0.005
        self.m_e = 26
        self.omega_e = 0.515
        self.beta_e = 0.5

        #Target reliability for the bob
        self.eb = 10e-3
        #Secrecy constraint (or information leakage to the eve)
        self.delta = 10e-3
        #Channel blocklenght
        self.n = 500

        ##    2. Get reference to running STK instance
        self.uiApplication = CreateObject('STK11.Application')
        self.uiApplication.Visible = False
        self.uiApplication.UsarControl=True

        ##    3. Get our IAgStkObjectRoot interface
        self.root = self.uiApplication.Personality2

        path_to_tle = "TLE/"
        f_idx = open(scenario_file_path)
        scenario_metadata = json.load(f_idx)

        self.ScenarioName  = scenario_metadata["Scenario"]["name"]
        StartTime   = scenario_metadata["time constraints"]["start time"]
        StopTime     = scenario_metadata["time constraints"]["stop time"]
        StepTime      = scenario_metadata["time constraints"]["step"]

        ######################################
        ##    Task 2
        ##    1. Create a new scenario

        self.root.NewScenario(self.ScenarioName)
        scenario      = self.root.CurrentScenario

        ##    2. Set the analytical time period.

        scenario2     = scenario.QueryInterface(STKObjects.IAgScenario)
        scenario2.SetTimePeriod(StartTime,StopTime)
        scenario2.Animation.AnimStepValue = StepTime

        ##    3. Reset the animation time.
        self.root.Rewind()

        # Get the entity parameters from the scenario file and initialize the entities.
        self.Satellites = {}
        sat_idx = 0
        for sat in scenario_metadata['satellites']:  
            sat_idx += 1
            sat_name = scenario_metadata["satellites"][sat]["name"]
            sat_scc = scenario_metadata["satellites"][sat]["propagator_params"]["scc"]
            tle_file_path = scenario_metadata["satellites"][sat]["propagator_params"]["tle_file"]
            self.Satellites[sat_name] = STKEntities.Stk_Satellite(self.root, sat_name)
            self.Satellites[sat_name].SetSatellitePropagator_and_BasicAttitude(self.root, sat_scc, True, tle_file_path, True)

        self.GroundStations = {}
        gs_idx = 0
        for gs in scenario_metadata['ground_stations']:  
            gs_idx += 1
            gs_name = scenario_metadata["ground_stations"][gs]["name"]
            unit = scenario_metadata["ground_stations"][gs]["lat_long_unit"]
            use_terrain = scenario_metadata["ground_stations"][gs]["use_terrain"]
            lat = scenario_metadata["ground_stations"][gs]["lat"]
            long = scenario_metadata["ground_stations"][gs]["long"]
            alt = scenario_metadata["ground_stations"][gs]["alt"]
            self.GroundStations[gs_name] = STKEntities.STKGroundStation(self.root, gs_name, unit, use_terrain, lat, long, alt)

        self.Antennas = {}
        an_idx = 0
        for an in scenario_metadata["antennas"]:
            an_idx += 1
            an_name = scenario_metadata["antennas"][an]["name"]
            parent_name = scenario_metadata["antennas"][an]["antenna_parent"]
            model = scenario_metadata["antennas"][an]["model"]
            diameter = scenario_metadata["antennas"][an]["diameter"]
            computer_diameter = scenario_metadata["antennas"][an]["computer_diameter"]
            freq = scenario_metadata["antennas"][an]["freq"]
            Elv = scenario_metadata["antennas"][an]["Elv"]
            sensor_bool = scenario_metadata["antennas"][an]["sensor_bool"]
            self.Antennas[an_name] = STKEntities.STKAntenna(an_name, self.GroundStations[parent_name].groundStation, model, diameter, computer_diameter, freq) 
            if not sensor_bool:
                self.Antennas[an_name].set_azelorientation(0, Elv, 0) 


        self.Transmitters = {}
        ts_idx = 0
        for ts in scenario_metadata['transmitters']:
            ts_idx += 1  
            ts_name = scenario_metadata["transmitters"][ts]["name"]
            parent_name = scenario_metadata["transmitters"][ts]["transmitter_parent"]
            model = scenario_metadata["transmitters"][ts]["model"]
            dem = scenario_metadata["transmitters"][ts]["dem"]
            auto_scale_bandwidth = scenario_metadata["transmitters"][ts]["auto_scale_bandwidth"]
            freq = scenario_metadata["transmitters"][ts]["freq"]
            power = scenario_metadata["transmitters"][ts]["power"]
            data_rate = scenario_metadata["transmitters"][ts]["data_rate"]
            antenna_control = scenario_metadata["transmitters"][ts]["antenna_control"]
            self.Transmitters[ts_name] = STKEntities.STKTransmitter(self.root, ts_name, self.GroundStations[parent_name].groundStation, model, dem, auto_scale_bandwidth, freq, power, data_rate, antenna_control)

        self.Receivers = {}
        rs_idx = 0
        for rs in scenario_metadata['receivers']:  
            rs_idx += 1
            rs_name = scenario_metadata["receivers"][rs]["name"]
            parent_name = scenario_metadata["receivers"][rs]["receiver_parent"]
            model = scenario_metadata["receivers"][rs]["receiver_type"]
            auto_select_modulator = scenario_metadata["receivers"][rs]["auto_select_modulator"]
            dem = scenario_metadata["receivers"][rs]["dem"]
            antenna_control = scenario_metadata["receivers"][rs]["antenna_control"]
            self.Receivers[rs_name] = STKEntities.STKReceptor(rs_name, self.Satellites[parent_name].sat, model, auto_select_modulator, dem, antenna_control)


        self.Access = {}
        
        self.acces_name_sc1a = scenario_metadata["receivers"]["saocom1a_receiver"]["receiver_parent"] + "_acces_" + scenario_metadata["receivers"]["saocom1a_receiver"]["link_transmitters"][0]
        report_name = scenario_metadata["receivers"]["saocom1a_receiver"]["receiver_parent"] + "_" + scenario_metadata["receivers"]["saocom1a_receiver"]["link_transmitters"][0]
        ts_name_sc1a = scenario_metadata["receivers"]["saocom1a_receiver"]["link_transmitters"][0]
        dem = scenario_metadata["receivers"]["saocom1a_receiver"]["dem"]
        rs_name = scenario_metadata["receivers"]["saocom1a_receiver"]["name"]
        rs_sat_name_sc1a = scenario_metadata["receivers"]["saocom1a_receiver"]["receiver_parent"]
        ts_gs_name = scenario_metadata["receivers"]["saocom1a_receiver"]["link_transmitters"][0]
        self.ts_an_name_sc1a = scenario_metadata["receivers"]["saocom1a_receiver"]["link_antennas"][0]
        self.Access[self.acces_name_sc1a] = self.Transmitters[ts_name_sc1a].transmitter.GetAccessToObject(self.Receivers[rs_name].receptor)
        self.Access[self.acces_name_sc1a].ComputeAccess()
        
        accessStartTime, accessStopTime, duration_1 = stk_api.get_access_times(self.Access[self.acces_name_sc1a], scenario2)
        self.acces_name = scenario_metadata["receivers"]["eve_receiver"]["receiver_parent"] + "_acces_" + scenario_metadata["receivers"]["eve_receiver"]["link_transmitters"][0]
        report_name = scenario_metadata["receivers"]["eve_receiver"]["receiver_parent"] + "_" + scenario_metadata["receivers"]["eve_receiver"]["link_transmitters"][0]
        ts_name = scenario_metadata["receivers"]["eve_receiver"]["link_transmitters"][0]
        dem = scenario_metadata["receivers"]["eve_receiver"]["dem"]
        rs_name = scenario_metadata["receivers"]["eve_receiver"]["name"]
        rs_sat_name = scenario_metadata["receivers"]["eve_receiver"]["receiver_parent"]
        ts_gs_name = scenario_metadata["receivers"]["eve_receiver"]["link_transmitters"][0]
        self.Access[self.acces_name] = self.Transmitters[ts_name].transmitter.GetAccessToObject(self.Receivers[rs_name].receptor)
        self.Access[self.acces_name].ComputeAccess()

        longest_access_start_time, longest_access_stop_time = stk_api.get_access_time(self.Access[self.acces_name_sc1a], 0, scenario2, True)
        self.new_start_time, self.new_stop_time, self.new_access_times = stk_api.get_access_within_access(longest_access_start_time, longest_access_stop_time, self.Access[self.acces_name], scenario2, StepTime)
        eve_channel = Channel.Short_Packed_Channel(self.b_e, self.m_e, self.omega_e, self.beta_e, len(self.new_access_times))
        bob_channel = Channel.Short_Packed_Channel(self.b_b, self.m_b, self.omega_b, self.beta_b, len(self.new_access_times))
        self.h_t_bob = bob_channel.shadowed_rician(0,len(self.new_access_times))[0]
        self.h_t_eve = eve_channel.shadowed_rician(0,len(self.new_access_times))[0]

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)

        self.info = {}
        self.info['step number'] = 0

    
    def _get_obs(self, link, time):

        aer_elements = ["Azimuth", "Elevation", "Range"]
        AER_data = stk_api.get_instantaneous_link_data(link, "AER Data", "Default", time, aer_elements, "List")

        pv_elements = ["x", "y", "z", "xVel", "yVel", "zVel", "RelSpeed"]
        LinkInfo_data = stk_api.get_instantaneous_link_data(link, "To Position Velocity", "J2000", time, pv_elements ,"List")

        obs = AER_data + LinkInfo_data
        return obs
    
    def step(self, action):

        current_step = self.info['step number']
        
        self.Antennas[self.ts_an_name_sc1a].set_azelorientation(action[0], action[1], 0)
        obs = self._get_obs(self.Access[self.acces_name_sc1a], self.new_access_times[current_step])
        C_No_bob = stk_api.get_instantaneous_link_data(self.Access[self.acces_name_sc1a], "Link Information", 0, self.new_access_times[current_step], ["C/No"], "List")
        C_No_eve = stk_api.get_instantaneous_link_data(self.Access[self.acces_name], "Link Information", 0, self.new_access_times[current_step], ["C/No"], "List")
        cn_bob = power(10, C_No_bob[0]/10)
        cn_eve = power(10, C_No_eve[0]/10)
        snr_b = cn_bob * (abs(self.h_t_bob[current_step]) ** 2) / (1**2)
        snr_e = cn_eve * (abs(self.h_t_eve[current_step]) ** 2) / (1**2)
        reward = sr.achievable_secrecy_rate(snr_b, snr_e, self.eb, self.delta, self.n)

        truncated = False

        self.info['step number'] += 1
        terminated = (self.info['step number'] == len(self.new_access_times))

        return obs, reward, terminated, truncated, self.info