from xml.etree import ElementTree as ET 
import pandas as pd
from adapt_and_manipulate_scenario.utils.opendrive_container_classes import Road, Junction
import random

## TODO differentiate the 3-way junction from the 4-way junction

def opendrive_extractor(filename):
    """
    Extract the road and junction details along with their id and length to give to the LLMs.
    """
    # TODO check for the lanes in the junction as it seems wrong
    road_details: list[Road] = []
    junction_details: list[Junction] = []

    root = ET.parse(filename).getroot()
    
    # parse the opendrive and separate the roads and junctions
    for xodr_element in root:

        if xodr_element.tag == "header":
            pass
        
        # Road Details
        elif xodr_element.tag == "road":
            # Retrieve Road Details from the Xodr format
            road_class = Road.from_xodr(xodr_road_element=xodr_element)
            road_details.append(road_class)

        # Junction Details
        elif xodr_element.tag == "junction":
            # Retrieve Junction Details from the Xodr format
            junction_class = Junction.from_xodr(xodr_junction_element=xodr_element)

            junction_details.append(junction_class)

    return road_details, junction_details

def choose_road_or_junction(road_details, junction_details, scenario_location):
    """
    Choose the junction or road id randomly based on the scenario_location. 

    Note: 
    1. road_id_list contains only the id of the roads that are not a part of a intersection
    """
    junction_id_list_3_way: list[str] = []
    junction_id_list_4_way: list[str] = []
    single_lane_road_id_list: list[str] = [] # contains only the road that are not part of a junction
    multi_lane_road_id_list: list[str] = []

    # a condiiton for the single lane and multi lane
    for road_detail in road_details:
        if not road_detail.is_in_junction: 
            if len(road_detail.left_driving_lane_ids) == 1 and len(road_detail.right_driving_lane_ids) == 1 and len(road_detail.left_sidewalk_lane_ids) == 1 and len(road_detail.right_sidewalk_lane_ids) == 1: 
                single_lane_road_id_list.append(road_detail.id)

            elif len(road_detail.left_driving_lane_ids) >= 2 and len(road_detail.right_driving_lane_ids) >= 2: 
                multi_lane_road_id_list.append(road_detail.id)
    
    for junction_detail in junction_details:
        # Note only 3-way is done as of now
        #TODO create a condition to separate the 3-way from 4-way junctions. 
        if len(junction_detail.junction_connect_list) == 6 or len(junction_detail.junction_connect_list) == 8:
            junction_id_list_3_way.append(junction_detail.id)
        
        if len(junction_detail.junction_connect_list) == 12:
            junction_id_list_4_way.append(junction_detail.id)
    
    if scenario_location == "3_way_intersection" and junction_id_list_3_way != []:
        chosen_junction_id = random.choice(junction_id_list_3_way)
        for junction in junction_details:
            if junction.id == chosen_junction_id:
                chosen_junction = junction
                return chosen_junction
    
    if scenario_location == "4_way_intersection" and junction_id_list_4_way != []:
        chosen_junction_id = "508"
        for junction in junction_details:
            if junction.id == chosen_junction_id:
                chosen_junction = junction
                return chosen_junction
            
    elif scenario_location == "single_lane":
        chosen_road_id = random.choice(single_lane_road_id_list)
        for road in road_details:
            if road.id == chosen_road_id:
                chosen_road = road
                return chosen_road
    
    elif scenario_location == "multi_lane":
        chosen_road_id = random.choice(multi_lane_road_id_list)
        for road in road_details:
            if road.id == chosen_road_id:
                chosen_road = road
                return chosen_road
    return None

def generate_vehicle_lane_position(filename, scenario_location):
    # Carla Map Details
    # https://carla.readthedocs.io/en/0.9.11/core_map/

    road_details, junction_details = opendrive_extractor(filename)

    ### Uncomment to visulize the details of road and junction of the specified map.
    # for road in road_details:
    #     print(f"id: {road.id} || length: {road.length} || left_lane_id: {road.left_driving_lane_ids} || right_lane_id: {road.right_driving_lane_ids} || is_in_junction: {road.is_in_junction} || is_in_junction_id: {road.is_in_junction_id}") 
    
    # for junction in junction_details:
    #     print(f"Junction id: {junction.id}")
    #     for connection_road in junction.junction_connect_list:
    #         print(f"Connection id {connection_road.connecting_id}, Incoming road id {connection_road.incoming_road}, Connection road id {connection_road.connecting_road}")
    
    # choose a road or junction based on the scenario location chosen by the user
    chosen_road_or_junction = choose_road_or_junction(road_details, junction_details, scenario_location=scenario_location)

    return chosen_road_or_junction, road_details, junction_details

if __name__ == "__main__":
    
    filename =r"C:\Users\johnp\Desktop\John - University of Stuttgart\Robo-Test Thesis\Test_Code\Opendrive Carla Town\karlsruhe.xodr"
        
    # filename =r"/home/students/Desktop/MT_Carla/karlshuhe.xodr"

    chosen_road_or_junction, road_details, junction_details = generate_vehicle_lane_position(filename, "single_lane") #"single_lane" "multi_lane" ,"3_way_intersection" ,"4_way_intersection"
 
    # print(f"id: {chosen_road_or_junction.id} || length: {chosen_road_or_junction.length} || left_lane_id: {chosen_road_or_junction.left_driving_lane_ids} || right_lane_id: {chosen_road_or_junction.right_driving_lane_ids} || left_sidewalk_lane_id: {chosen_road_or_junction.left_sidewalk_lane_ids} || right_sidewalk_lane_id: {chosen_road_or_junction.right_sidewalk_lane_ids} || is_in_junction: {chosen_road_or_junction.is_in_junction} || is_in_junction_id: {chosen_road_or_junction.is_in_junction_id}") 

    # print(f"Chosen Junction id: {chosen_road_or_junction.name}")
    # for connection_road in chosen_road_or_junction.junction_connect_list:
    #     print(f"Connection id {connection_road.connecting_id}, Incoming road id {connection_road.incoming_road}, Connection road id {connection_road.connecting_road}, {type(connection_road.lane_link[0])}")
