from lxml import etree
from adapt_and_manipulate_scenario.utils.opendrive_parser import opendrive_extractor
from adapt_and_manipulate_scenario.mycfg import TOWN01, KARLSRUHE

## TODO change the filename under _find_road_max_length

class RoadLenCalculate:
    def __init__(self, scenario_file, scenario_information):
        self.scenario_file = scenario_file
        self.vehicle_types = ["hero", "adversary", "bicycle", "pedestrian", "pedestriantwo"]
        self.scenario_information = scenario_information    
        self.final_dic = {}
        # self.run()  
          
    def _lane_position(self, private_element):
        # other vehicle and pedestrian initial roadid position details
        for private_element in private_element.iter("Private"):
            if private_element.attrib["entityRef"] in self.vehicle_types and private_element.attrib["entityRef"] != "hero":
                self.final_dic[private_element.attrib["entityRef"]] = {}
                for private_action_element in private_element.iter("PrivateAction"):
                    if private_action_element.find("TeleportAction") is not None:
                        teleport_action_element = private_action_element.find("TeleportAction")
                        if teleport_action_element.find("Position") is not None:
                            position_element = teleport_action_element.find("Position")
                            if position_element.find("LanePosition") is not None:
                                lane_position_element = position_element.find("LanePosition")
                                self.final_dic[private_element.attrib["entityRef"]]["LanePosition"] = {}
                                self.final_dic[private_element.attrib["entityRef"]]["LanePosition"]["id"] = lane_position_element.attrib["roadId"]

    def _hero_route_position(self, hero_event_element):
        # hero route roadid details
        if hero_event_element.find("Maneuver") is not None:
            for maneuver_element in hero_event_element.iter("Maneuver"):
                for routing_action_element in maneuver_element.iter("RoutingAction"):
                    self.final_dic["hero"] = {}
                    acquire_position_element = routing_action_element.find("AcquirePositionAction")
                    position_elememt = acquire_position_element.find("Position")
                    if position_elememt.find("LanePosition") is not None:
                        lane_pos_element = position_elememt.find("LanePosition")
                        self.final_dic["hero"]["RoutingAction"] = {}
                        self.final_dic["hero"]["RoutingAction"]["id"] = lane_pos_element.attrib["roadId"]
    
    def _pedestrian_reach_position(self, pedestrian_event_element, actor_name):
        if pedestrian_event_element.find("Maneuver") is not None:
            maneuver_element = pedestrian_event_element.find("Maneuver")
            if maneuver_element.find('Event') is not None:
                for event_element in maneuver_element.iter("Event"):
                    # Event 1 - Pedestrian starts
                    if "PedestrianStartsWalking" in event_element.attrib["name"]:
                        for start_trigger_element in event_element.iter("StartTrigger"):
                            for reach_position_element in start_trigger_element.iter("ReachPositionCondition"):
                                if reach_position_element.find("Position") is not None:
                                    position_elememt = reach_position_element.find("Position")
                                    if position_elememt.find("LanePosition") is not None:
                                        lane_pos_element = position_elememt.find("LanePosition")
                                        self.final_dic[actor_name]["ReachPosition"] = {}
                                        self.final_dic[actor_name]["ReachPosition"]["id"] = lane_pos_element.attrib["roadId"]

    def _bicycle_reach_position(self, bicycle_event_element, actor_name):
        if bicycle_event_element.find("Maneuver") is not None:
            maneuver_element = bicycle_event_element.find("Maneuver")
            if maneuver_element.find('Event') is not None:
                for event_element in maneuver_element.iter("Event"):
                    for start_trigger_element in event_element.iter("StartTrigger"):
                        for reach_position_element in start_trigger_element.iter("ReachPositionCondition"):
                            if reach_position_element.find("Position") is not None:
                                position_elememt = reach_position_element.find("Position")
                                if position_elememt.find("LanePosition") is not None:
                                    lane_pos_element = position_elememt.find("LanePosition")
                                    self.final_dic[actor_name]["ReachPosition"] = {}
                                    self.final_dic[actor_name]["ReachPosition"]["id"] = lane_pos_element.attrib["roadId"]
    
    def _find_road_max_length(self):

        if "Town01" in self.scenario_information:
            filename = TOWN01
            road_details, junction_details = opendrive_extractor(filename=filename)
        
        elif "Karlsruhe" in self.scenario_information:
            filename = KARLSRUHE
            road_details, junction_details = opendrive_extractor(filename=filename)
        
        for road in road_details:
            for actor_key, actor_dic in self.final_dic.items():
                if "hero" in actor_key:
                    if road.id == self.final_dic[actor_key]["RoutingAction"]["id"]:
                        self.final_dic[actor_key]["RoutingAction"]["max_length"] = road.length
                
                if "hero" not in actor_key:
                    if road.id == self.final_dic[actor_key]["LanePosition"]["id"]:
                        self.final_dic[actor_key]["LanePosition"]["max_length"] = road.length
                
                if "pedestrian" in actor_key:
                    if road.id == self.final_dic[actor_key]["ReachPosition"]["id"]:
                        self.final_dic[actor_key]["ReachPosition"]["max_length"] = road.length
                                
                if "bicycle" in actor_key and "crossing" in self.scenario_information:
                    if self.final_dic[actor_key].get("ReachPosition", 0) !=0:
                        self.final_dic[actor_key]["ReachPosition"]["max_length"] = road.length
                
    def run(self):
        root = etree.parse(self.scenario_file).getroot()
        
        # lane position details
        for xosc_element in root:
            # get road position from init element
            if xosc_element.tag == "Storyboard":
                self._lane_position(xosc_element)

                story_element = xosc_element.find("Story")
                act_element = story_element.find("Act")
                for maneuver_group_element in act_element.iter("ManeuverGroup"):
                    if maneuver_group_element.find("Actors") is not None:
                        actors_element = maneuver_group_element.find("Actors")
                        actor_name = actors_element.find("EntityRef").attrib["entityRef"]

                        if "hero" in actor_name:
                            self._hero_route_position(maneuver_group_element)
                        
                        elif "pedestrian" in actor_name:
                            self._pedestrian_reach_position(maneuver_group_element, actor_name)
                        
                        elif "bicycle" in actor_name:
                            if "crossing" in self.scenario_information:
                                self._bicycle_reach_position(maneuver_group_element, actor_name)
        
        self._find_road_max_length() 

        return self.final_dic
    
if __name__ == "__main__":
    in_scenario_file = r"C:\Users\johnp\Desktop\John - University of Stuttgart\Robo-Test Thesis\Test_Code\JohnArockiasamy-MasterThesis3646\out\test_01\1.xosc"
    rlc =  RoadLenCalculate(in_scenario_file, scenario_information="Karlsruhe__hero_and_2_pedestrians_crossing_in_front__4_way_intersection")
    final_dic = rlc.run()
    print(final_dic)


