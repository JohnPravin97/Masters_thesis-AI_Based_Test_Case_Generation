from lxml import etree
import json
from scenariogeneration import xosc

## TODO it doesnt work on the pedestriantwo
class ScenarioManipulate:
    def __init__(self, parameter_json, map_name, vehicle_types, scenario_location, scenario_information):
        self.map_name = map_name
        self.scenario_location = scenario_location
        self.scenario_information = scenario_information
        self.vehicle_types = vehicle_types
        self.parameter_json = parameter_json
        
        # load the json file - uncomment if the path is given instead of the file itself
        # with open(parameter_file) as f:
            # self.parameter_json = json.load(f)

        # remove the route from the list
        if "route" in vehicle_types:
            self.vehicle_types.remove("route")
        
        elif "weather" in vehicle_types:
            self.vehicle_types.remove("weather")
        
    def _manipulate_entities_scenario(self, entities_elements):
        # parse the entities in scenarioobject
        for so_element in entities_elements.iter("ScenarioObject"):
            if so_element.attrib["name"] in self.vehicle_types:
                if so_element.find("Vehicle") is not None:
                    veh_element = so_element.find("Vehicle") 
                    # manipulate the vehicle performance.
                    veh_performance_element = veh_element.find("Performance")
                    veh_performance_element.attrib["maxSpeed"] = self.parameter_json[so_element.attrib["name"]]["Performance"]["maxSpeed"]
                    veh_performance_element.attrib["maxAcceleration"] = self.parameter_json[so_element.attrib["name"]]["Performance"]["maxAcceleration"]
                    veh_performance_element.attrib["maxDeceleration"] = self.parameter_json[so_element.attrib["name"]]["Performance"]["maxDeceleration"]
    
    def _manipulate_weather_scenario(self, environment_elements):
        for environment_element in environment_elements.iter("Environment"):
            if environment_element.find("Weather") is not None:
                weather_element = environment_element.find("Weather")
                # manipulate the sun element
                if (weather_element.find("Sun") is not None) and (self.parameter_json["weather"].get("Sun",0)!=0):
                    sun_element = weather_element.find("Sun")
                    sun_element.attrib["azimuth"] = self.parameter_json["weather"]["Sun"]["azimuth"]
                    sun_element.attrib["intensity"] = self.parameter_json["weather"]["Sun"]["intensity"]
                    sun_element.attrib["elevation"] = self.parameter_json["weather"]["Sun"]["elevation"]

                # manipulate the fog element
                if weather_element.find("Fog") is not None and (self.parameter_json["weather"].get("Fog",0) !=0):
                    fog_element = weather_element.find("Fog")
                    if "Fog" in self.parameter_json["weather"]:
                        fog_element.attrib["visualRange"] = self.parameter_json["weather"]["Fog"]["visualRange"]
                
                # manipulate the precipitation element
                if weather_element.find("Precipitation") is not None and (self.parameter_json["weather"].get("Precipitation",0) !=0):
                    precipitation_element = weather_element.find("Precipitation")
                    if "Precipitation" in self.parameter_json["weather"]:
                        precipitation_element.attrib["precipitationType"] = self.parameter_json["weather"]["Precipitation"]["precipitationType"]
                        precipitation_element.attrib["intensity"] = self.parameter_json["weather"]["Precipitation"]["intensity"]
                        
            # manipulate the roadcondition element
            if environment_element.find("RoadCondition") is not None: 
                road_cond_element = environment_element.find("RoadCondition")
                road_cond_element.attrib["frictionScaleFactor"] = self.parameter_json["weather"]["RoadCondition"]["frictionScaleFactor"]

    def _manipulate_private_details_scenario(self, private_elements):
        for private_element in private_elements.iter("Private"):
            if private_element.attrib["entityRef"] in self.vehicle_types and private_element.attrib["entityRef"] != "hero":
                for private_action_element in private_element.iter("PrivateAction"):
                    if private_action_element.find("TeleportAction") is not None:
                        teleport_action_element = private_action_element.find("TeleportAction")
                        if teleport_action_element.find("Position") is not None:
                            position_element = teleport_action_element.find("Position")
                            if position_element.find("LanePosition") is not None:
                                lane_position_element = position_element.find("LanePosition")
                                lane_position_element.attrib["s"] = self.parameter_json[private_element.attrib["entityRef"]]["LanePosition"]["s"]

                    if private_action_element.find("LongitudinalAction") is not None:
                        longitudinal_action_element = private_action_element.find("LongitudinalAction")
                        for speed_action_element in longitudinal_action_element.iter("SpeedAction"):
                            if speed_action_element.find("SpeedActionTarget") is not None:
                                speed_action_target_element = speed_action_element.find("SpeedActionTarget")
                                absolute_target_element = speed_action_target_element.find("AbsoluteTargetSpeed")
                                absolute_target_element.attrib["value"] = self.parameter_json[private_element.attrib["entityRef"]]["SpeedActionTarget"]["AbsoluteTargetSpeed"]

    def _manipulate_hero_event_scenario(self, hero_event_element):
        # check if the event belongs to hero vehicle
        if hero_event_element.find("Maneuver") is not None:
            for maneuver_element in hero_event_element.iter("Maneuver"):
                for routing_action_element in maneuver_element.iter("RoutingAction"):
                    acquire_position_element = routing_action_element.find("AcquirePositionAction")
                    position_elememt = acquire_position_element.find("Position")
                    if position_elememt.find("LanePosition") is not None:
                            lane_pos_element = position_elememt.find("LanePosition")
                            if self.parameter_json["hero"].get("RoutingAction", 0) !=0:
                                lane_pos_element.attrib["s"] = self.parameter_json["hero"]["RoutingAction"]["s"]

    def _manipulate_actor_event_scenario(self, actor_event_element):
        if actor_event_element.find("Maneuver") is not None:
            maneuver_element = actor_event_element.find("Maneuver")
            if maneuver_element.find('Event') is not None:
                for event_element in maneuver_element.iter("Event"):
                    # Event 1 - Actor starts
                    if "ActorStarts" in event_element.attrib["name"]:
                        for longi_action_element in event_element.iter("LongitudinalAction"):
                            for speed_action_element in longi_action_element.iter("SpeedAction"):
            
                                if speed_action_element.find("SpeedActionTarget") is not None:
                                    speed_action_target_element = speed_action_element.find("SpeedActionTarget")
                                    absolute_target_element = speed_action_target_element.find("AbsoluteTargetSpeed")
                                    absolute_target_element.attrib["value"] = self.parameter_json["adversary"]["Events"]["ActorStarts"]["SpeedActionTarget"]["AbsoluteTargetSpeed"]
                                
                                if speed_action_element.find("SpeedActionDynamics") is not None:
                                    speed_action_dynamics = speed_action_element.find("SpeedActionDynamics")
                                    speed_action_dynamics.attrib["value"] = self.parameter_json["adversary"]["Events"]["ActorStarts"]["SpeedActionDynamics"]["value"]
                                    
                    
                    # Event 2 - Actor Stops And Waits
                    if "ActorStopsAndWaits" in event_element.attrib["name"]:
                        for longi_action_element in event_element.iter("LongitudinalAction"):
                            for speed_action_element in longi_action_element.iter("SpeedAction"):
                                if speed_action_element.find("SpeedActionDynamics") is not None:
                                        speed_action_dynamics = speed_action_element.find("SpeedActionDynamics")
                                        speed_action_dynamics.attrib["value"] = self.parameter_json["adversary"]["Events"]["ActorStopsAndWaits"]["SpeedActionDynamics"]["value"]

                    # Event 3 - Actor Drives Away
                    if "ActorDrivesAway" in event_element.attrib["name"]:
                        for longi_action_element in event_element.iter("LongitudinalAction"):
                            for speed_action_element in longi_action_element.iter("SpeedAction"):
            
                                if speed_action_element.find("SpeedActionTarget") is not None:
                                    speed_action_target_element = speed_action_element.find("SpeedActionTarget")
                                    absolute_target_element = speed_action_target_element.find("AbsoluteTargetSpeed")
                                    absolute_target_element.attrib["value"] = self.parameter_json["adversary"]["Events"]["ActorDrivesAway"]["SpeedActionTarget"]["AbsoluteTargetSpeed"]
                                
                                if speed_action_element.find("SpeedActionDynamics") is not None:
                                    speed_action_dynamics = speed_action_element.find("SpeedActionDynamics")
                                    speed_action_dynamics.attrib["value"] = self.parameter_json["adversary"]["Events"]["ActorDrivesAway"]["SpeedActionDynamics"]["value"]
                                            
    def _manipulate_bicycle_event_scenario(self, bicycle_event_element, crossing=False):
        if bicycle_event_element.find("Maneuver") is not None:
            maneuver_element = bicycle_event_element.find("Maneuver")
            if maneuver_element.find('Event') is not None:
                for event_element in maneuver_element.iter("Event"):
                    
                    # Event 1 - Bicycle starts
                    if "BicycleStarts" in event_element.attrib["name"]:
                        for longi_action_element in event_element.iter("LongitudinalAction"):
                            for speed_action_element in longi_action_element.iter("SpeedAction"):
            
                                if speed_action_element.find("SpeedActionTarget") is not None:
                                    speed_action_target_element = speed_action_element.find("SpeedActionTarget")
                                    absolute_target_element = speed_action_target_element.find("AbsoluteTargetSpeed")
                                    absolute_target_element.attrib["value"] = self.parameter_json["bicycle"]["Events"]["BicycleStarts"]["SpeedActionTarget"]["AbsoluteTargetSpeed"]
                                
                                if speed_action_element.find("SpeedActionDynamics") is not None:
                                    speed_action_dynamics = speed_action_element.find("SpeedActionDynamics")
                                    speed_action_dynamics.attrib["value"] = self.parameter_json["bicycle"]["Events"]["BicycleStarts"]["SpeedActionDynamics"]["value"]
                            
                            if crossing == True:
                                for start_trigger_element in event_element.iter("StartTrigger"):
                                    for reach_position_element in start_trigger_element.iter("ReachPositionCondition"):
                                        if reach_position_element.find("Position") is not None:
                                            position_elememt = reach_position_element.find("Position")
                                            if position_elememt.find("LanePosition") is not None:
                                                lane_pos_element = position_elememt.find("LanePosition")
                                                lane_pos_element.attrib["s"] = self.parameter_json["bicycle"]["Events"]["BicycleStarts"]["ReachPositionCondition"]["s"]
                    
                    # Event 2 - Bicycle Stops And Waits
                    if "BicycleStopsAndWaits" in event_element.attrib["name"]:
                        for longi_action_element in event_element.iter("LongitudinalAction"):
                            for speed_action_element in longi_action_element.iter("SpeedAction"):
                                if speed_action_element.find("SpeedActionDynamics") is not None:
                                        speed_action_dynamics = speed_action_element.find("SpeedActionDynamics")
                                        speed_action_dynamics.attrib["value"] = self.parameter_json["bicycle"]["Events"]["BicycleStopsAndWaits"]["SpeedActionDynamics"]["value"]

                    # Event 3 - Bicycle Drives Away
                    if "BicycleDrivesAway" in event_element.attrib["name"]:
                        for longi_action_element in event_element.iter("LongitudinalAction"):
                            for speed_action_element in longi_action_element.iter("SpeedAction"):
            
                                if speed_action_element.find("SpeedActionTarget") is not None:
                                    speed_action_target_element = speed_action_element.find("SpeedActionTarget")
                                    absolute_target_element = speed_action_target_element.find("AbsoluteTargetSpeed")
                                    absolute_target_element.attrib["value"] = self.parameter_json["bicycle"]["Events"]["BicycleDrivesAway"]["SpeedActionTarget"]["AbsoluteTargetSpeed"]
                                
                                if speed_action_element.find("SpeedActionDynamics") is not None:
                                    speed_action_dynamics = speed_action_element.find("SpeedActionDynamics")
                                    speed_action_dynamics.attrib["value"] = self.parameter_json["bicycle"]["Events"]["BicycleDrivesAway"]["SpeedActionDynamics"]["value"]


    def _manipulate_pedestrian_event_scenario(self, pedestrian_event_element):
        # TODO check the orientation
        if pedestrian_event_element.find("Maneuver") is not None:
            maneuver_element = pedestrian_event_element.find("Maneuver")
            if maneuver_element.find('Event') is not None:
                for event_element in maneuver_element.iter("Event"):
                
                    # Event 1 - Pedestrian starts
                    if "PedestrianStartsWalking" in event_element.attrib["name"]:
                        for longi_action_element in event_element.iter("LongitudinalAction"):
                            for speed_action_element in longi_action_element.iter("SpeedAction"):
            
                                if speed_action_element.find("SpeedActionTarget") is not None:
                                    speed_action_target_element = speed_action_element.find("SpeedActionTarget")
                                    absolute_target_element = speed_action_target_element.find("AbsoluteTargetSpeed")
                                    absolute_target_element.attrib["value"] = self.parameter_json["pedestrian"]["Events"]["PedestrianStarts"]["SpeedActionTarget"]["AbsoluteTargetSpeed"]
                                
                                if speed_action_element.find("SpeedActionDynamics") is not None:
                                    speed_action_dynamics = speed_action_element.find("SpeedActionDynamics")
                                    speed_action_dynamics.attrib["value"] = self.parameter_json["pedestrian"]["Events"]["PedestrianStarts"]["SpeedActionDynamics"]["value"]
                            
                        for start_trigger_element in event_element.iter("StartTrigger"):
                            for reach_position_element in start_trigger_element.iter("ReachPositionCondition"):
                                if reach_position_element.find("Position") is not None:
                                    position_elememt = reach_position_element.find("Position")
                                    if position_elememt.find("LanePosition") is not None:
                                        lane_pos_element = position_elememt.find("LanePosition")
                                        lane_pos_element.attrib["s"] = self.parameter_json["pedestrian"]["Events"]["PedestrianStarts"]["ReachPositionCondition"]["s"]


                    # Event 2 - Pedestrian Stops And Waits
                    if "PedestrianStopsAndWaits" in event_element.attrib["name"]:
                        for longi_action_element in event_element.iter("LongitudinalAction"):
                            for speed_action_element in longi_action_element.iter("SpeedAction"):
                                if speed_action_element.find("SpeedActionDynamics") is not None:
                                        speed_action_dynamics = speed_action_element.find("SpeedActionDynamics")
                                        speed_action_dynamics.attrib["value"] = self.parameter_json["pedestrian"]["Events"]["PedestrianStopsAndWaits"]["SpeedActionDynamics"]["value"]

                    # Event 3 - Pedestrian Drives Away
                    if "PedestrianWalksAway" in event_element.attrib["name"]:
                        for longi_action_element in event_element.iter("LongitudinalAction"):
                            for speed_action_element in longi_action_element.iter("SpeedAction"):
            
                                if speed_action_element.find("SpeedActionTarget") is not None:
                                    speed_action_target_element = speed_action_element.find("SpeedActionTarget")
                                    absolute_target_element = speed_action_target_element.find("AbsoluteTargetSpeed")
                                    absolute_target_element.attrib["value"] = self.parameter_json["pedestrian"]["Events"]["PedestrianWalksAway"]["SpeedActionTarget"]["AbsoluteTargetSpeed"]
                                
                                if speed_action_element.find("SpeedActionDynamics") is not None:
                                    speed_action_dynamics = speed_action_element.find("SpeedActionDynamics")
                                    speed_action_dynamics.attrib["value"] = self.parameter_json["pedestrian"]["Events"]["PedestrianWalksAway"]["SpeedActionDynamics"]["value"]
                            
    def scenario_manipulate(self, in_scenario_file, out_scenario_file):
        
        # parse the openscenario file
        root = etree.parse(in_scenario_file).getroot()

        for xosc_element in root:
            # Add the Vehicle name of N1 and Ego to carla compatible one 
            if xosc_element.tag == "Entities":
                self._manipulate_entities_scenario(xosc_element)

            if xosc_element.tag == "Storyboard":
                # manipulate the weather element
                self._manipulate_weather_scenario(xosc_element)

                # manipulate the private information of the actor element
                self._manipulate_private_details_scenario(xosc_element)

                # manipulate the private information of the actor element
                story_element = xosc_element.find("Story")
                act_element = story_element.find("Act")
                for maneuver_group_element in act_element.iter("ManeuverGroup"):
                    if maneuver_group_element.find("Actors") is not None:
                        actors_element = maneuver_group_element.find("Actors")
                        if "hero" in actors_element.find("EntityRef").attrib["entityRef"]:
                            self._manipulate_hero_event_scenario(maneuver_group_element)

                        elif "adversary" in actors_element.find("EntityRef").attrib["entityRef"]:
                            self._manipulate_actor_event_scenario(maneuver_group_element)
                        
                        elif "bicycle" in actors_element.find("EntityRef").attrib["entityRef"]:
                            if "crossing" in self.scenario_information:
                                self._manipulate_bicycle_event_scenario(maneuver_group_element, crossing=True)
                            else:
                                self._manipulate_bicycle_event_scenario(maneuver_group_element, crossing=False)
                        
                        elif "pedestrian" in actors_element.find("EntityRef").attrib["entityRef"]:
                            self._manipulate_pedestrian_event_scenario(maneuver_group_element)

        # save the manipulated files
        with open(out_scenario_file, 'wb') as f:
            f.write(
            etree.tostring(
                root, pretty_print=True, xml_declaration=True
            )
        )

if __name__ == "__main__":
    vehicle_types = ["hero", "route", "pedestrian", "pedestriantwo"]
    in_scenario_file = r"C:\Users\johnp\Desktop\John - University of Stuttgart\Robo-Test Thesis\Test_Code\JohnArockiasamy-MasterThesis3646\out\test_01\1.xosc"
    out_scenario_file = r"C:\Users\johnp\Desktop\John - University of Stuttgart\Robo-Test Thesis\Test_Code\JohnArockiasamy-MasterThesis3646\out\test_01\iteration_1\1_editted.xosc"
    parameter_file = r"C:\Users\johnp\Desktop\John - University of Stuttgart\Robo-Test Thesis\Test_Code\JohnArockiasamy-MasterThesis3646\out\test_01\iteration_1\concrete_scenario.json"
    
    sm = ScenarioManipulate(parameter_file=parameter_file, map_name = "Karlsruhe", vehicle_types=vehicle_types, scenario_location="4_way_intersection", scenario_information="hero_and_2_pedestrians_crossing_in_front")
    
    sm.scenario_manipulate(in_scenario_file=in_scenario_file, out_scenario_file=out_scenario_file)