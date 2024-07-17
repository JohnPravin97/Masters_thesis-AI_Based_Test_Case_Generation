import json
from pathlib import Path
from scenariogeneration import xosc, prettyprint
from utils.opendrive_parser import generate_vehicle_lane_position
from mycfg import TOWN01, TOWN02, KARLSRUHE
import random
from collections import defaultdict

class metadata_class:
    def __init__(self, vehicle_details, walker_details, vehicle_parameters, walker_parameters, environment_parameters, carla_auto_pilot, simple_control, adas_evaluation_metrics, carla_autopilot_evaluation_metrics):
        self.vehicle_details = vehicle_details
        self.walker_details = walker_details
        self.vehicle_parameters = vehicle_parameters
        self.walker_parameters=walker_parameters
        self.environment_parameters = environment_parameters
        self.carla_auto_pilot = carla_auto_pilot
        self.simple_control = simple_control
        self.adas_evaluation_metrics = adas_evaluation_metrics
        self.carla_autopilot_evaluation_metrics = carla_autopilot_evaluation_metrics

        self.orientation_pedestrian = None

        if self.vehicle_details["CarDetails"]["VehicleType"] == "car":
            self.vehicle_details["CarDetails"]["VehicleType"] = xosc.VehicleCategory.car
        
        if self.vehicle_details["CarDetails"]["VehicleType"] == "bicycle":
            self.vehicle_details["CarDetails"]["VehicleType"] = xosc.VehicleCategory.bicycle
        
        if self.walker_details["PedestrianDetails"]["WalkerType"] == "pedestrian":
            self.walker_details["PedestrianDetails"]["WalkerType"] = xosc.PedestrianCategory.pedestrian

        if self.environment_parameters["Precipitation"][0] == "dry":
           self.environment_parameters["Precipitation"][0] = xosc.PrecipitationType.dry
        
        if self.environment_parameters["Weather"] == "free":
            self.environment_parameters["Weather"] == xosc.CloudState.free
        
        if self.environment_parameters["TimeofDay"][0] == 0:
            self.environment_parameters["TimeofDay"][0] = False
    
    def _map_location(self, map_name):
        if map_name == "Town01":
            map_location = TOWN01
        
        elif map_name == "Town02":
            map_location = TOWN02
        
        elif map_name == "Karlsruhe":
            map_location = KARLSRUHE

        return map_location

    def _derive_details_from_junction_details(self, chosen_road_or_junction, road_details):
        incoming_road_id_dic = defaultdict(list)

        for junction_connect in chosen_road_or_junction.junction_connect_list:
            for roads in road_details:
                if roads.id == junction_connect.incoming_road:
                    if junction_connect.lane_link[0] in roads.right_driving_lane_ids or junction_connect.lane_link[0] in roads.left_driving_lane_ids:
                        incoming_road_id_dic[junction_connect.incoming_road].append(junction_connect.lane_link[0])

        incoming_road_id_dic = {key: list(set(value)) for key, value in incoming_road_id_dic.items()}# remove duplicates from the incoming_road_id_list

        return incoming_road_id_dic
    
    def _choose_junction_left_or_right_lane(self, chosen_road_or_junction, road_details):
        # derive all the incoming road to the junction (where the vehicle will be spawned)
        
        incoming_road_id_dic = self._derive_details_from_junction_details(chosen_road_or_junction, road_details)
        
        # choose if the vehicle should be spawned on left or right lane
        chosen_left_or_right_lane = random.choice(["left_lane", "right_lane"])

        return chosen_left_or_right_lane, incoming_road_id_dic
    
    # assign individual methods for single lane intersection
    def _choose_road_left_or_right_lane(self, chosen_road_or_junction):
        
        # choose if the vehicle should be spawned on left or right lane
        chosen_left_or_right_lane = random.choice(["left_lane", "right_lane"])
    
        return chosen_left_or_right_lane

    def _assign_hero_single_lane(self, chosen_road_or_junction, chosen_left_or_right_lane):
        if chosen_left_or_right_lane == "left_lane":
            return int(float(chosen_road_or_junction.length)), 0, random.choice(chosen_road_or_junction.left_driving_lane_ids), chosen_road_or_junction.id
        
        elif chosen_left_or_right_lane == "right_lane":
            return 0, 0, random.choice(chosen_road_or_junction.right_driving_lane_ids), chosen_road_or_junction.id
        
    def _assign_route_single_lane(self, assign_veh_lane_pos_dic, chosen_road_or_junction, chosen_left_or_right_lane):
        # same lane as the hero spawn
        _, _, lane_id, _ = assign_veh_lane_pos_dic["hero"]

        if chosen_left_or_right_lane == "left_lane":
            return 0, 0, lane_id, chosen_road_or_junction.id
        
        elif chosen_left_or_right_lane == "right_lane":
            return int(float(chosen_road_or_junction.length)), 0, lane_id, chosen_road_or_junction.id
       
    def _assign_other_single_lane(self, vehicle_type, chosen_road_or_junction, chosen_left_or_right_lane):
        distance_gap = 20 # determine the distance between the car, bicycle, actor and pedestrian while spawning

        # TODO check the scenario information and make the pedestrian spawn on the same lane
        if chosen_left_or_right_lane == "left_lane":
            # condition to make the pedestrian spawn on the sidewalk instead of driving area
            if "pedestrian" in vehicle_type:
                self.orientation_pedestrian = "left"
                if chosen_road_or_junction.left_sidewalk_lane_ids != []:
                    return random.randint(0, int(float(chosen_road_or_junction.length))-distance_gap), 0, random.choice(chosen_road_or_junction.left_sidewalk_lane_ids), chosen_road_or_junction.id
                elif chosen_road_or_junction.right_sidewalk_lane_ids != []:
                    return random.randint(0, int(float(chosen_road_or_junction.length))-distance_gap), 0, random.choice(chosen_road_or_junction.right_sidewalk_lane_ids), chosen_road_or_junction.id
                else:
                    return random.randint(0, int(float(chosen_road_or_junction.length))-distance_gap), 0, random.choice(chosen_road_or_junction.left_driving_lane_ids), chosen_road_or_junction.id
            else:
                return random.randint(0, int(float(chosen_road_or_junction.length))-distance_gap), 0, random.choice(chosen_road_or_junction.left_driving_lane_ids), chosen_road_or_junction.id
        
        elif chosen_left_or_right_lane == "right_lane":
            # condition to make the pedestrian spawn on the sidewalk instead of driving area
            if "pedestrian" in vehicle_type:
                self.orientation_pedestrian = "right"
                if chosen_road_or_junction.right_sidewalk_lane_ids != []:
                    return random.randint(distance_gap, int(float(chosen_road_or_junction.length))), 0, random.choice(chosen_road_or_junction.right_sidewalk_lane_ids), chosen_road_or_junction.id
                elif chosen_road_or_junction.left_sidewalk_lane_ids != []:
                    return random.randint(distance_gap, int(float(chosen_road_or_junction.length))), 0, random.choice(chosen_road_or_junction.left_sidewalk_lane_ids), chosen_road_or_junction.id
                else:
                    return random.randint(distance_gap, int(float(chosen_road_or_junction.length))), 0, random.choice(chosen_road_or_junction.right_driving_lane_ids), chosen_road_or_junction.id
            else:
                return random.randint(distance_gap, int(float(chosen_road_or_junction.length))), 0, random.choice(chosen_road_or_junction.right_driving_lane_ids), chosen_road_or_junction.id
    
    def _assign_bicycle_crossing_single_lane(self, vehicle_type, chosen_road_or_junction, chosen_left_or_right_lane):
        distance_gap = 20 # determine the distance between the car, bicycle, actor and pedestrian while spawning

        # TODO check the scenario information and make the pedestrian spawn on the same lane
        if chosen_left_or_right_lane == "left_lane":
            # condition to make the pedestrian spawn on the sidewalk instead of driving area
            if "bicycle" in vehicle_type:
                self.orientation_pedestrian = "left"
                if chosen_road_or_junction.left_sidewalk_lane_ids != []:
                    return random.randint(0, int(float(chosen_road_or_junction.length))-distance_gap), 0, random.choice(chosen_road_or_junction.left_sidewalk_lane_ids), chosen_road_or_junction.id
                
                elif chosen_road_or_junction.right_sidewalk_lane_ids != []:
                    return random.randint(0, int(float(chosen_road_or_junction.length))-distance_gap), 0, random.choice(chosen_road_or_junction.right_sidewalk_lane_ids), chosen_road_or_junction.id
                else:
                    return random.randint(0, int(float(chosen_road_or_junction.length))-distance_gap), 0, random.choice(chosen_road_or_junction.left_driving_lane_ids), chosen_road_or_junction.id
            
            else:
                return random.randint(0, int(float(chosen_road_or_junction.length))-distance_gap), 0, random.choice(chosen_road_or_junction.left_driving_lane_ids), chosen_road_or_junction.id
        
        elif chosen_left_or_right_lane == "right_lane":
            # condition to make the pedestrian spawn on the sidewalk instead of driving area
            if "bicycle" in vehicle_type:
                self.orientation_pedestrian = "right"
                if chosen_road_or_junction.right_sidewalk_lane_ids != []:
                    return random.randint(0, int(float(chosen_road_or_junction.length))-distance_gap), 0, random.choice(chosen_road_or_junction.right_sidewalk_lane_ids), chosen_road_or_junction.id
                
                elif chosen_road_or_junction.left_sidewalk_lane_ids != []:
                    return random.randint(0, int(float(chosen_road_or_junction.length))-distance_gap), 0, random.choice(chosen_road_or_junction.left_sidewalk_lane_ids), chosen_road_or_junction.id
                else:
                    return random.randint(0, int(float(chosen_road_or_junction.length))-distance_gap), 0, random.choice(chosen_road_or_junction.right_driving_lane_ids), chosen_road_or_junction.id
            
            else:
                return random.randint(0, int(float(chosen_road_or_junction.length))-distance_gap), 0, random.choice(chosen_road_or_junction.right_driving_lane_ids), chosen_road_or_junction.id

    # assign individual methods for 3-way intersection
    def _assign_hero_3_way_intersection_lane(self, chosen_incoming_road, incoming_road_id_dic, road_details):
        # loop over all the roads to find the chosen_incoming_road information
        if "-" in incoming_road_id_dic[chosen_incoming_road][0]:
            chosen_left_or_right_lane = "right"

        else: 
            chosen_left_or_right_lane = "left"

        for road in road_details:
            if road.id == chosen_incoming_road: 
                # this will make sure the route is always the end of the lane
                if chosen_left_or_right_lane == "left":
                    return int(float(road.length)), 0, random.choice(road.left_driving_lane_ids), road.id
                
                # this will ensure that the vehicle is at the start of the lane
                elif chosen_left_or_right_lane == "right":
                    return 0, 0, random.choice(road.right_driving_lane_ids), road.id
    
    def _assign_route_3_way_intersection_lane(self, chosen_incoming_road, incoming_road_id_dic, road_details):
        
        if "-" in incoming_road_id_dic[chosen_incoming_road][0]:
            chosen_left_or_right_lane = "left"

        else: 
            chosen_left_or_right_lane = "right"

        for road in road_details:
            if road.id == chosen_incoming_road: 
                # this will make sure the route is always the end of the lane
                if chosen_left_or_right_lane == "left":
                    return 0, 0, random.choice(road.left_driving_lane_ids), road.id
                
                # this will ensure that the vehicle is at the start of the lane
                elif chosen_left_or_right_lane == "right":
                    return int(float(road.length)), 0, random.choice(road.right_driving_lane_ids), road.id
    
    def _assign_other_opposite_direction_3_way_intersection_lane(self, route_lane_position, road_details):
        # assign the pedestrian in the same lane as the hero or the route completion
        s, offset, lane_id, road_id = route_lane_position

        if "-" in lane_id:
            chosen_left_or_right_lane = "left"

        else: 
            chosen_left_or_right_lane = "right"

        for road in road_details:
            if road.id == road_id: 
                # this will make sure the route is always the end of the lane - TODO make it spawn anywhere in that same - done
                if chosen_left_or_right_lane == "left":
                    return random.randint(0, int(float(road.length))), 0, random.choice(road.left_driving_lane_ids), road.id
                
                # this will ensure that the vehicle is at the start of the lane
                elif chosen_left_or_right_lane == "right":
                    return random.randint(0,int(float(road.length))), 0, random.choice(road.right_driving_lane_ids), road.id

    def _assign_other_same_direction_3_way_intersection_lane(self, chosen_incoming_road, incoming_road_id_dic, road_details):
        # loop over all the roads to find the chosen_incoming_road information
        if "-" in incoming_road_id_dic[chosen_incoming_road][0]:
            chosen_left_or_right_lane = "right"

        else: 
            chosen_left_or_right_lane = "left"

        for road in road_details:
            if road.id == chosen_incoming_road: 
                distance_gap = 20
                # this will make sure the route is always the end of the lane
                if chosen_left_or_right_lane == "left":
                    return random.randint(0, int(float(road.length))- distance_gap), 0, random.choice(road.left_driving_lane_ids), road.id
                
                # this will ensure that the vehicle is at the start of the lane
                elif chosen_left_or_right_lane == "right":
                    return random.randint(distance_gap, int(float(road.length))), 0, random.choice(road.right_driving_lane_ids), road.id
    
    def _assign_pedestrian_3_way_intersection_lane(self, hero_or_route_lane, hero_or_route_lane_position, chosen_left_or_right_lane, road_details):
        # assign the pedestrian in the same lane as the hero or the route completion
        s, offset, lane_id, road_id = hero_or_route_lane_position

        if "-" in lane_id:
            chosen_left_or_right_lane = "left"

        else: 
            chosen_left_or_right_lane = "right"

        for road in road_details:
            if road.id == road_id:
                self.orientation_pedestrian = "right"
                 # this will make sure the pedestrian is spawned always infront of the car with a distance_gap of 10
                distance_gap = 10
                if hero_or_route_lane == "hero":    
                    if chosen_left_or_right_lane == "left":
                        if road.right_sidewalk_lane_ids != []:
                            return random.randint(0, int(float(road.length))-distance_gap), 0, random.choice(road.right_sidewalk_lane_ids), road.id
                        
                        elif road.left_sidewalk_lane_ids != []:
                            return random.randint(0, int(float(road.length))-distance_gap), 0, random.choice(road.left_sidewalk_lane_ids), road.id

                        else:
                            return random.randint(0, int(float(road.length))-distance_gap), 0, random.choice(road.right_driving_lane_ids), road.id
                        
                    elif chosen_left_or_right_lane == "right":
                        if road.right_sidewalk_lane_ids != []:
                            return random.randint(distance_gap, int(float(road.length))), 0, random.choice(road.right_sidewalk_lane_ids), road.id
                        
                        elif road.left_sidewalk_lane_ids != []:
                            return random.randint(distance_gap, int(float(road.length))), 0, random.choice(road.left_sidewalk_lane_ids), road.id
                        
                        else:
                            return random.randint(0, int(float(road.length))-distance_gap), 0, random.choice(road.left_driving_lane_ids), road.id
                        
                else:
                    if road.right_sidewalk_lane_ids != []:
                        return random.randint(0, int(float(road.length))), 0, random.choice(road.right_sidewalk_lane_ids), road.id
                    
                    elif road.left_sidewalk_lane_ids != []:
                        return random.randint(0, int(float(road.length))), 0, random.choice(road.left_sidewalk_lane_ids), road.id
                    
                    else:
                            return random.randint(0, int(float(road.length))-distance_gap), 0, random.choice(road.right_driving_lane_ids), road.id
            
    # Assign vehicle based on the scenario information
    # 3-way Lane Scenarios
    def _assign_actor_or_bicycle_same_direction_scenarios(self, vehicle_types, chosen_road_or_junction, road_details):
        assign_veh_lane_pos_dic= {}

        # choose the left or right lane - it is a junction for sure
        _, incoming_road_id_dic = self._choose_junction_left_or_right_lane(chosen_road_or_junction, road_details)

        # choose a incoming road to spawn the vehicle type
        incoming_road_id_list = list(incoming_road_id_dic.keys())

        for vehicle_type in vehicle_types:

            if "bicycle" in vehicle_type or "adversary" in vehicle_type:
                # drop the bicycle and actor on the different lane from the route
                # chose a incoming roads
                chosen_incoming_road = random.choice(incoming_road_id_list)

                s, offset, lane_id, road_id = self._assign_other_same_direction_3_way_intersection_lane(chosen_incoming_road, incoming_road_id_dic, road_details)
            
            else:                 
                # chose a incoming roads
                chosen_incoming_road = random.choice(incoming_road_id_list)

                # remove the chosen_incoming_road from the incoming_road_id_list to make the new road in the junction for other vehicle
                incoming_road_id_list.remove(chosen_incoming_road)

                if vehicle_type == "hero":
                    # assign the vehicle_type to that chosen_incoming_road
                    s, offset, lane_id, road_id = self._assign_hero_3_way_intersection_lane(chosen_incoming_road, incoming_road_id_dic, road_details)
                
                elif vehicle_type == "route":
                    s, offset, lane_id, road_id = self._assign_route_3_way_intersection_lane(chosen_incoming_road, incoming_road_id_dic, road_details)

            assign_veh_lane_pos_dic[vehicle_type] = [s, offset, lane_id, road_id]    

        return assign_veh_lane_pos_dic
    
    def _assign_actor_or_bicycle_opposite_direction_scenarios(self, vehicle_types, chosen_road_or_junction, road_details):
        assign_veh_lane_pos_dic= {}

        # choose the left or right lane - it is a junction for sure
        _, incoming_road_id_dic = self._choose_junction_left_or_right_lane(chosen_road_or_junction, road_details)

        # choose a incoming road to spawn the vehicle type
        incoming_road_id_list = list(incoming_road_id_dic.keys())

        for vehicle_type in vehicle_types:

            if "bicycle" in vehicle_type or "adversary" in vehicle_type:
                # drop the bicycle and actor on the different lane from the route
                route_lane_position = assign_veh_lane_pos_dic["route"]
                s, offset, lane_id, road_id = self._assign_other_opposite_direction_3_way_intersection_lane(route_lane_position, road_details)
            
            else:                 
                # chose a incoming roads
                chosen_incoming_road = random.choice(incoming_road_id_list)

                # remove the chosen_incoming_road from the incoming_road_id_list to make the new road in the junction for other vehicle
                incoming_road_id_list.remove(chosen_incoming_road)

                if vehicle_type == "hero":
                    # assign the vehicle_type to that chosen_incoming_road
                    s, offset, lane_id, road_id = self._assign_hero_3_way_intersection_lane(chosen_incoming_road, incoming_road_id_dic, road_details)
                
                elif vehicle_type == "route":
                    s, offset, lane_id, road_id = self._assign_route_3_way_intersection_lane(chosen_incoming_road, incoming_road_id_dic, road_details)

            assign_veh_lane_pos_dic[vehicle_type] = [s, offset, lane_id, road_id]    

        return assign_veh_lane_pos_dic

    def _assign_actor_opposite_and_bicycle_same_direction_scenarios(self, vehicle_types, chosen_road_or_junction, road_details):
        assign_veh_lane_pos_dic= {}

        # choose the left or right lane - it is a junction for sure
        _, incoming_road_id_dic = self._choose_junction_left_or_right_lane(chosen_road_or_junction, road_details)

        # choose a incoming road to spawn the vehicle type
        incoming_road_id_list = list(incoming_road_id_dic.keys())

        for vehicle_type in vehicle_types:

            if "adversary" in vehicle_type:
                # drop the bicycle and actor on the different lane from the route
                route_lane_position = assign_veh_lane_pos_dic["route"]
                s, offset, lane_id, road_id = self._assign_other_opposite_direction_3_way_intersection_lane(route_lane_position, road_details)
            
            elif "bicycle" in vehicle_type:
                # drop the bicycle and actor on the different lane from the route
                _, _, _, chosen_incoming_road = assign_veh_lane_pos_dic["hero"]
                s, offset, lane_id, road_id = self._assign_other_same_direction_3_way_intersection_lane(chosen_incoming_road, incoming_road_id_dic, road_details)

            else:                 
                # chose a incoming roads
                chosen_incoming_road = random.choice(incoming_road_id_list)

                # remove the chosen_incoming_road from the incoming_road_id_list to make the new road in the junction for other vehicle
                incoming_road_id_list.remove(chosen_incoming_road)

                if vehicle_type == "hero":
                    # assign the vehicle_type to that chosen_incoming_road
                    s, offset, lane_id, road_id = self._assign_hero_3_way_intersection_lane(chosen_incoming_road, incoming_road_id_dic, road_details)
                
                elif vehicle_type == "route":
                    s, offset, lane_id, road_id = self._assign_route_3_way_intersection_lane(chosen_incoming_road, incoming_road_id_dic, road_details)

            assign_veh_lane_pos_dic[vehicle_type] = [s, offset, lane_id, road_id]    

        return assign_veh_lane_pos_dic
    
    def _assign_pedestrian_crossing_in_front_3_way_scenarios(self, vehicle_types, chosen_road_or_junction, road_details):
        assign_veh_lane_pos_dic= {}

        # choose the left or right lane - it is a junction for sure
        chosen_left_or_right_lane, incoming_road_id_dic = self._choose_junction_left_or_right_lane(chosen_road_or_junction, road_details)
        # choose a incoming road to spawn the vehicle type
        incoming_road_id_list = list(incoming_road_id_dic.keys())

        for vehicle_type in vehicle_types:

            if "pedestrian" in vehicle_type:
                # assign pedestrian only on the lane of the car or on the lane of route completion
                hero_or_route_lane = random.choice(["hero", "route"])
                hero_or_route_lane_position = assign_veh_lane_pos_dic[hero_or_route_lane]
                s, offset, lane_id, road_id = self._assign_pedestrian_3_way_intersection_lane(hero_or_route_lane, hero_or_route_lane_position, chosen_left_or_right_lane, road_details)
            
            elif "bicycle" in vehicle_type or "adversary" in vehicle_type:
                # drop the bicycle and actor on the different lane from the route

                route_lane_position = assign_veh_lane_pos_dic["route"]
                s, offset, lane_id, road_id = self._assign_other_opposite_direction_3_way_intersection_lane(route_lane_position, road_details)
            
            else:                 
                # chose a incoming roads
                chosen_incoming_road = random.choice(incoming_road_id_list)

                if vehicle_type == "hero":
                    # assign the vehicle_type to that chosen_incoming_road
                    s, offset, lane_id, road_id = self._assign_hero_3_way_intersection_lane(chosen_incoming_road, incoming_road_id_dic, road_details)
                
                elif vehicle_type == "route":
                    s, offset, lane_id, road_id = self._assign_route_3_way_intersection_lane(chosen_incoming_road, incoming_road_id_dic, road_details)

                # remove the chosen_incoming_road from the incoming_road_id_list to make the new road in the junction for other vehicle
                incoming_road_id_list.remove(chosen_incoming_road)

            assign_veh_lane_pos_dic[vehicle_type] = [s, offset, lane_id, road_id]    

        return assign_veh_lane_pos_dic
    
    # Single Lane Scenarios
    def _assign_single_lane_scenarios(self, vehicle_types, chosen_road_or_junction):
        assign_veh_lane_pos_dic= {}

        # choose the left or right lane - it is a junction for sure
        chosen_left_or_right_lane = self._choose_road_left_or_right_lane(chosen_road_or_junction)

        for vehicle_type in vehicle_types:
            # make the bicycle, pedestrian, actor spawn on the same lane of the ego (hero) car all the time
            if "pedestrian" in vehicle_type or "bicycle" in vehicle_type or "adversary" in vehicle_type:
                s, offset, lane_id, road_id = self._assign_other_single_lane(vehicle_type, chosen_road_or_junction, chosen_left_or_right_lane)

            elif "route" in vehicle_type:
                s, offset, lane_id, road_id = self._assign_route_single_lane(assign_veh_lane_pos_dic, chosen_road_or_junction, chosen_left_or_right_lane)

            else:
                s, offset, lane_id, road_id = self._assign_hero_single_lane(chosen_road_or_junction, chosen_left_or_right_lane)
        
            assign_veh_lane_pos_dic[vehicle_type] = [s, offset, lane_id, road_id] 

        return assign_veh_lane_pos_dic

    def _assign_bicycle_crossing_single_lane_scenarios(self, vehicle_types, chosen_road_or_junction):
        assign_veh_lane_pos_dic= {}

        # choose the left or right lane - it is a junction for sure
        chosen_left_or_right_lane = self._choose_road_left_or_right_lane(chosen_road_or_junction)

        for vehicle_type in vehicle_types:
            # make the bicycle, pedestrian, actor spawn on the same lane of the ego (hero) car all the time
            if "bicycle" in vehicle_type:
                s, offset, lane_id, road_id = self._assign_bicycle_crossing_single_lane(vehicle_type, chosen_road_or_junction, chosen_left_or_right_lane)

            elif "route" in vehicle_type:
                s, offset, lane_id, road_id = self._assign_route_single_lane(assign_veh_lane_pos_dic, chosen_road_or_junction, chosen_left_or_right_lane)

            else:
                s, offset, lane_id, road_id = self._assign_hero_single_lane(chosen_road_or_junction, chosen_left_or_right_lane)
        
            assign_veh_lane_pos_dic[vehicle_type] = [s, offset, lane_id, road_id] 

        return assign_veh_lane_pos_dic
    
    def _assign_bicycle_actor_infront_single_lane_scenarios(self, vehicle_types, chosen_road_or_junction):
        assign_veh_lane_pos_dic= {}

        # choose the left or right lane - it is a junction for sure
        chosen_left_or_right_lane = self._choose_road_left_or_right_lane(chosen_road_or_junction)

        offset = 10
        bicycle_distance_gap = 25
        actor_distance_gap = 40
        total_length = int(float(chosen_road_or_junction.length))

        for vehicle_type in vehicle_types:
            # make the bicycle, pedestrian, actor spawn on the same lane of the ego (hero) car all the time
            if "bicycle" in vehicle_type:
                if chosen_left_or_right_lane == "left_lane":
                    s, offset, lane_id, road_id = random.randint(total_length-bicycle_distance_gap, total_length-offset), 0, random.choice(chosen_road_or_junction.left_driving_lane_ids), chosen_road_or_junction.id
                
                elif chosen_left_or_right_lane == "right_lane":
                    # condition to make the pedestrian spawn on the sidewalk instead of driving area
                    s, offset, lane_id, road_id = random.randint(offset, bicycle_distance_gap), 0, random.choice(chosen_road_or_junction.right_driving_lane_ids), chosen_road_or_junction.id
            
            elif "adversary" in vehicle_type: 
                if chosen_left_or_right_lane == "left_lane":
                    s, offset, lane_id, road_id = random.randint(total_length-actor_distance_gap, total_length-bicycle_distance_gap), 0, random.choice(chosen_road_or_junction.left_driving_lane_ids), chosen_road_or_junction.id
                
                elif chosen_left_or_right_lane == "right_lane":
                    # condition to make the pedestrian spawn on the sidewalk instead of driving area
                    s, offset, lane_id, road_id = random.randint(bicycle_distance_gap, actor_distance_gap), 0, random.choice(chosen_road_or_junction.right_driving_lane_ids), chosen_road_or_junction.id
            
            elif "route" in vehicle_type:
                s, offset, lane_id, road_id = self._assign_route_single_lane(assign_veh_lane_pos_dic, chosen_road_or_junction, chosen_left_or_right_lane)

            else:
                s, offset, lane_id, road_id = self._assign_hero_single_lane(chosen_road_or_junction, chosen_left_or_right_lane)
        
            assign_veh_lane_pos_dic[vehicle_type] = [s, offset, lane_id, road_id] 

        return assign_veh_lane_pos_dic
    
    def assign_vehicle_lane_position(self, map_name, vehicle_types, scenario_location, scenario_information):
        """
        Note: the vehicle type is a list containing hero, route, actor, pedestrian, cyclist.

        """
       
        # convert the map name (str) to the map path location
        map_location = self._map_location(map_name)
        
        # Scenario Description and Lane Position Info.
        # 3-way Intersection
        if scenario_information in ["hero_and_adversary_same_direction_route", "hero_and_bicycle_same_direction_route"] and scenario_location in [ "3_way_intersection", "4_way_intersection"]:
            # generate the road class, junction class, and a random chosen road or junection based on scenario location details
            chosen_road_or_junction, road_details, _ = generate_vehicle_lane_position(map_location, scenario_location)
            assign_veh_lane_pos_dic = self._assign_actor_or_bicycle_same_direction_scenarios(vehicle_types, chosen_road_or_junction, road_details)
        
        elif scenario_information in ["hero_and_adversary_different_direction_route", "hero_and_bicycle_opposite_direction_route"] and scenario_location in [ "3_way_intersection", "4_way_intersection"]:
            # generate the road class, junction class, and a random chosen road or junection based on scenario location details
            chosen_road_or_junction, road_details, _ = generate_vehicle_lane_position(map_location, scenario_location)
            assign_veh_lane_pos_dic = self._assign_actor_or_bicycle_opposite_direction_scenarios(vehicle_types, chosen_road_or_junction, road_details)

        elif scenario_information in ["hero_and_bicycle_same_direction_adversary_opposite_route"] and scenario_location in [ "3_way_intersection", "4_way_intersection"]:
            # generate the road class, junction class, and a random chosen road or junection based on scenario location details
            chosen_road_or_junction, road_details, _ = generate_vehicle_lane_position(map_location, scenario_location)
            assign_veh_lane_pos_dic = self._assign_actor_opposite_and_bicycle_same_direction_scenarios(vehicle_types, chosen_road_or_junction, road_details)

        elif scenario_information in ["hero_and_pedestrian_crossing_in_front", "hero_adversary_and_pedestrian_crossing_in_front", "hero_bicycle_and_pedestrian_crossing_in_front", "hero_and_2_pedestrians_crossing_in_front", "hero_adversary_and_2_pedestrians_crossing_in_front"] and scenario_location in ["3_way_intersection", "4_way_intersection"]: 
            # generate the road class, junction class, and a random chosen road or junection based on scenario location details
            chosen_road_or_junction, road_details, _ = generate_vehicle_lane_position(map_location, scenario_location)

            assign_veh_lane_pos_dic = self._assign_pedestrian_crossing_in_front_3_way_scenarios(vehicle_types, chosen_road_or_junction, road_details)
        

        # Single Lane
        elif scenario_information in ["hero_and_adversary_on_the_same_lane", "hero_and_bicycle_on_the_same_lane", "hero_and_pedestrian_crossing_in_front"] and scenario_location in ["single_lane", "multi_lane"]:
            # generate the road class, junction class, and a random chosen road or junection based on scenario location details
            while True:
                chosen_road_or_junction, road_details, junction_details = generate_vehicle_lane_position(map_location, scenario_location)

                # choose the road with more than 50 meters in length for the single lane scenarios
                if int(float(chosen_road_or_junction.length)) >= 50:
                    break
                
            assign_veh_lane_pos_dic = self._assign_single_lane_scenarios(vehicle_types, chosen_road_or_junction)

        elif scenario_information in ["hero_adversary_and_bicycle_on_the_same_lane"] and scenario_location in ["single_lane", "multi_lane"]:
             # generate the road class, junction class, and a random chosen road or junection based on scenario location details
            while True:
                chosen_road_or_junction, road_details, _ = generate_vehicle_lane_position(map_location, scenario_location)

                # choose the road with more than 50 meters in length for the single lane scenarios
                if int(float(chosen_road_or_junction.length)) >= 50:
                    break
                
            assign_veh_lane_pos_dic = self._assign_bicycle_actor_infront_single_lane_scenarios(vehicle_types, chosen_road_or_junction)

        elif scenario_information in ["hero_and_bicycle_crossing_in_front"] and scenario_location in ["single_lane", "multi_lane"]:
             # generate the road class, junction class, and a random chosen road or junection based on scenario location details
            while True:
                chosen_road_or_junction, road_details, junction_details = generate_vehicle_lane_position(map_location, scenario_location)

                # choose the road with more than 50 meters in length for the single lane scenarios
                if int(float(chosen_road_or_junction.length)) >= 50:
                    break
                
            assign_veh_lane_pos_dic = self._assign_bicycle_crossing_single_lane_scenarios(vehicle_types, chosen_road_or_junction)

        return assign_veh_lane_pos_dic, chosen_road_or_junction

    # TODO a method which takes in the opendrive details and provide relevant lane position parameters in a json file
    @classmethod
    def setup_data(cls):
        metafile = Path("generate_scenario/metadata_container/metadata.json").resolve()
        
        with open(metafile) as f:
            raw_dmeta = json.load(f)

        dmeta = cls(vehicle_details=raw_dmeta["VehicleDetails"], walker_details=raw_dmeta["WalkerDetails"], vehicle_parameters=raw_dmeta["VehicleParameters"], walker_parameters=raw_dmeta["WalkerParameters"], environment_parameters=raw_dmeta["EnviromentParameters"], carla_auto_pilot= raw_dmeta["CarlaAutoPilot"], simple_control= raw_dmeta["SimpleControl"], adas_evaluation_metrics = raw_dmeta["ADASEvaluationMetrics"], carla_autopilot_evaluation_metrics= raw_dmeta["CarlaAutoPilotEvaluationMetrics"])

        return dmeta


"""

            #         # # spawn only in the hero or route lane
            # # if "bicycle" in vehicle_type or "adversary" in vehicle_type:
            # #     hero_or_route_lane = random.choice(["hero", "route"])
            # #     hero_or_route_lane_position  = assign_veh_lane_pos_dic[hero_or_route_lane]
            # #     s, offset, lane_id, road_id = self._assign_other_3_way_intersection_lane(hero_or_route_lane, hero_or_route_lane_position, chosen_left_or_right_lane, road_details)

            # # spawn anywhere
            # if "bicycle" in vehicle_type or "adversary" in vehicle_type:
            #     # choose a incoming road to spawn the vehicle type
            #     incoming_road_id_list = list(incoming_road_id_dic.keys())

            #     chosen_incoming_road = random.choice(incoming_road_id_list)
            #     # assign the vehicle_type to that chosen_incoming_road
            #     s, offset, lane_id, road_id = self._assign_other_anywhere_3_way_intersection_lane(chosen_incoming_road, road_details)
"""