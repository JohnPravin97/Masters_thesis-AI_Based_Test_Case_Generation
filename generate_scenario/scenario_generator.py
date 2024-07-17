from scenariogeneration import xosc, prettyprint
from metadata_container.metadata import metadata_class
import random
import random
import json
from pathlib import Path

# Important TODO pedestrian sidewalk details in opendrive parser. - Done
# Important TODO add act and manuever etc..
# TODO assign route to ego if there is no actor car. Acquire Position Action is actor is provided

# Issues
# TODO Pedestrian Orientation is always a problem
# TODO check ways to make carla autopilot run - it is working when i changed a small thing in actor_control.py
# TODO Commission 3_way lane. 
# TODO look for 4_way lane and check if it can be run like 3_way
# TODO change the name of the scenarios as per the explaination

class Scenario: 
    def __init__(self, map_name, vehicle_types, scenario_location, scenario_information, osc_controller, minor_version=0):
        self.open_scenario_version = minor_version
        self.map_name = map_name
        self.vehicle_types = vehicle_types
        self.scenario_location = scenario_location
        self.scenario_information = scenario_information
        self.osc_controller = osc_controller

        self.dmeta = metadata_class.setup_data()
        
        # TODO lane position
        self.lane_position_parameters, self.chosen_road_details = self.dmeta.assign_vehicle_lane_position(self.map_name, self.vehicle_types, self.scenario_location, self.scenario_information)

    def _create_vehicle(self, vehicle_type):

        # Initialize the parameters
        if vehicle_type == "hero":
            veh_name, category = random.choice(self.dmeta.vehicle_details["CarDetails"]["VehicleName"]), self.dmeta.vehicle_details["CarDetails"]["VehicleType"]
            veh_property = "ego_vehicle"
        
        elif "adversary" in vehicle_type:
            veh_name, category = random.choice(self.dmeta.vehicle_details["CarDetails"]["VehicleName"]), self.dmeta.vehicle_details["CarDetails"]["VehicleType"]
            veh_property = "simulation"
            
        elif "bicycle" in vehicle_type:
            veh_name, category = random.choice(self.dmeta.vehicle_details["CyclistDetails"]["VehicleName"]), self.dmeta.vehicle_details["CyclistDetails"]["VehicleType"]
            veh_property = "simulation"

        width, length, height, center_x, center_y, center_z = self.dmeta.vehicle_parameters["BoundingBox"]
        front_maxSteering, front_wheelDiameter, front_trackWidth, front_positionX, front_positionZ = self.dmeta.vehicle_parameters["FrontAxle"]
        rear_maxSteering, rear_wheelDiameter, rear_trackWidth, rear_positionX, rear_positionZ = self.dmeta.vehicle_parameters["RearAxle"]
        max_speed, max_acceleration, max_deceleration = self.dmeta.vehicle_parameters["MaxDetails"]

        # declare the parameter
        bounding_box = xosc.BoundingBox(width, length, height, center_x, center_y, center_z)
        front_axle = xosc.Axle(front_maxSteering, front_wheelDiameter, front_trackWidth, front_positionX, front_positionZ)
        rear_axle = xosc.Axle(rear_maxSteering, rear_wheelDiameter, rear_trackWidth, rear_positionX, rear_positionZ)

        # declare the vehicle
        vehicle = xosc.Vehicle(veh_name, category, bounding_box, front_axle, rear_axle, max_speed, max_acceleration, max_deceleration) 
        vehicle.add_property("type", veh_property)

        return vehicle

        # def _create_walker(self):
    
    def _create_walker(self):
        # Initialize the parameters
        walker_name, walker_mass, category, = random.choice(self.dmeta.walker_details["PedestrianDetails"]["WalkerName"]), self.dmeta.walker_details["PedestrianDetails"]["WalkerMass"], self.dmeta.walker_details["PedestrianDetails"]["WalkerType"]
        width, length, height, center_x, center_y, center_z = self.dmeta.walker_parameters["BoundingBox"]
    
        # declare the parameter
        bounding_box = xosc.BoundingBox(width, length, height, center_x, center_y, center_z)

        # declare the vehicle
        category = "pedestrian"
        walker =  xosc.Pedestrian(walker_name, walker_mass, category, bounding_box, walker_name) 
        walker.add_property("type", "simulation")

        return walker

    def _create_environment(self):
        # Initialize the environment parameters
        year, month, day, hour, minute, second = self.dmeta.environment_parameters["TimeofDay"]
        intensity, elevation, azimuth = self.dmeta.environment_parameters["Sun"]
        precipitation, precipitation_intensity = self.dmeta.environment_parameters["Precipitation"]
        fog_visual_range = self.dmeta.environment_parameters["Fog"]
        road_friction = self.dmeta.environment_parameters["RoadCondition"]
        weather = self.dmeta.environment_parameters["Weather"]

        # declare the environment parameters
        tod = xosc.TimeOfDay(False, year, month, day, hour, minute, second)
        sun = xosc.Sun(intensity=intensity, elevation=elevation, azimuth=azimuth)
        fog = xosc.Fog(visual_range=fog_visual_range)
        precip = xosc.Precipitation(precipitation=precipitation, intensity=precipitation_intensity)

        # declare weather 
        weather = xosc.Weather(weather, sun=sun, fog=fog, precipitation=precip)

        # declare road condition
        road_con = xosc.RoadCondition(friction_scale_factor=road_friction)

        # declare the enviroment variable
        environment = xosc.Environment("Environment1", tod, weather=weather, roadcondition=road_con)
        return xosc.EnvironmentAction(environment)

    def _create_init_vehicle_action(self, vehicle_type, vehicle_lane_position):
        # initialize the action variables
        if vehicle_type == "hero" or "adversary":
            absolute_speed = self.dmeta.vehicle_details["CarDetails"]["VehicleAbsoluteSpeed"]
        elif vehicle_type == "bicycle":
            absolute_speed = self.dmeta.vehicle_details["CyclistDetails"]["VehicleAbsoluteSpeed"]

        s, offset, lane_id, road_id = vehicle_lane_position
        orientation = xosc.Orientation(0, 0, 0, xosc.ReferenceContext.relative)

        # declare teleport action details
        lane_position = xosc.LanePosition(s, offset, lane_id, road_id, orientation)
        teleport_action = xosc.TeleportAction(lane_position)

        # declare absolute speed action details
        transition_details = xosc.TransitionDynamics(
                    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 0
                )
        absolute_speed_action = xosc.AbsoluteSpeedAction(absolute_speed, transition_details)

        return teleport_action, absolute_speed_action

    def _create_init_vehicle_control(self, name, osc_controller):
        """ enable the carla autopilot if adas is not provided """

        # define the property
        if osc_controller == "carla_autopilot":
            # randomly choose the auto pilot from ["carla_autopilot", "simple_vehicle_control", "vehicle_longitudinal_control"]
            if "hero" in name:
                property_controller_name = random.choice(self.dmeta.carla_auto_pilot)

            elif "adversary" in name:
                property_controller_name = random.choice(self.dmeta.simple_control) 

        elif osc_controller =="adas":
            property_controller_name = "external_control"

        # define the properties
        hero_property = xosc.Properties()
        hero_property.add_property(name="module", value=property_controller_name)

        # define controller and assigncontrolleragent
        controller = xosc.Controller(name = name+"Agent", properties=hero_property)
        assign_controller_action = xosc.AssignControllerAction(controller=controller)

        # define override controller value action
        override_controller_value_action = xosc.OverrideControllerValueAction()
        override_controller_value_action.throttle_active = False 
        override_controller_value_action.brake_active= False
        override_controller_value_action.clutch_active= False
        override_controller_value_action.steeringwheel_active= False
        override_controller_value_action.gear_active = False 
        override_controller_value_action.parkingbrake_active = False

        # define controller action
        controller_action = xosc.ControllerAction(assignControllerAction=assign_controller_action, overrideControllerValueAction=override_controller_value_action)

        return controller_action
    
    def _create_init_walker_action(self, walker_lane_position):
        # initialize the action variables
        s, offset, lane_id, road_id = walker_lane_position

        ## TODO orientation changes to 180 -> 0 if the pedestrain walk on the lane
        if self.dmeta.orientation_pedestrian == "left":
            orientation_angle = 180

        elif self.dmeta.orientation_pedestrian == "right":
            orientation_angle = 90

        else:
            raise Exception("Unknown Pedestrian Orientation")
        orientation = xosc.Orientation(orientation_angle, 0, 0, xosc.ReferenceContext.relative)

        # declare teleport action details
        lane_position = xosc.LanePosition(s, offset, lane_id, road_id, orientation)
        teleport_action = xosc.TeleportAction(lane_position)

        return teleport_action

    def _create_event_hero_route(self):
        # create a route planner for hero and actor car
        s, offset, lane_id, road_id = self.lane_position_parameters["route"]
        lane_position = xosc.LanePosition(s, offset, lane_id, road_id)

        # create action
        route_creation_action = xosc.AcquirePositionAction(position=lane_position)
        route_creation_event = xosc.Event("RouteCreation", xosc.Priority.overwrite)
        route_creation_event.add_action("RouteCreation", route_creation_action)

        route_creation_event.add_trigger(
            xosc.ValueTrigger(
                "StartCondition",
                0,
                xosc.ConditionEdge.rising,
                xosc.SimulationTimeCondition(0.1, xosc.Rule.greaterThan),
            )
        )
        return [route_creation_event]
    
    # def _create_event_route_creation(self):
    #     # create a route planner for hero and actor car
    #     s, offset, lane_id, road_id = self.lane_position_parameters["route"]
    #     lane_position = xosc.LanePosition(s, offset, lane_id, road_id)

    #     # create action
    #     route_creation_action = xosc.AcquirePositionAction(position=lane_position)
    #     route_creation_event = xosc.Event("RouteCreation", xosc.Priority.overwrite)
    #     route_creation_event.add_action("RouteCreation", route_creation_action)

    #     route_creation_event.add_trigger(
    #         xosc.ValueTrigger(
    #             "StartCondition",
    #             0,
    #             xosc.ConditionEdge.rising,
    #             xosc.SimulationTimeCondition(0.1, xosc.Rule.greaterThan),
    #         )
    #     )
    #     return [route_creation_event]
    
    def _create_event_actor_in_front(self, travel_for_distance = 10.0, waiting_time = 5):
        # Event 1 - Actor drives

        ## Declare the event
        actor_in_front_event_1 = xosc.Event("ActorStarts", xosc.Priority.overwrite)

        ## Action
        sin_time_action_1 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.distance, travel_for_distance)
        actor_in_front_action_1 = xosc.AbsoluteSpeedAction(10, sin_time_action_1)
        ### add action to the event
        actor_in_front_event_1.add_action("ActorStarts", actor_in_front_action_1)

        ## Start Trigger
        actor_in_front_event_1.add_trigger(
            xosc.ValueTrigger(
                "StartCondition",
                0,
                xosc.ConditionEdge.rising,
                xosc.SimulationTimeCondition(0.1, xosc.Rule.greaterThan),
            )
        )

        # Event 2 - Actor waits 
        actor_in_front_event_2 = xosc.Event("ActorStopsAndWaits", xosc.Priority.overwrite)

        # Action
        sin_time_action_2 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, waiting_time) # wait for some secs
        actor_in_front_action_2 =  xosc.AbsoluteSpeedAction(0, sin_time_action_2)
        actor_in_front_event_2.add_action("ActorStopsAndWaits", actor_in_front_action_2)
        
        # Trigger
        trigger_cond_event_2 = xosc.StoryboardElementStateCondition(xosc.StoryboardElementType.action,"ActorStarts",
                xosc.StoryboardElementState.completeState,
                )
        
        actor_in_front_event_2.add_trigger(
            xosc.ValueTrigger("AfterActorStarts", 0, xosc.ConditionEdge.rising, trigger_cond_event_2)
        )

        # Event 3 - Actor drives away
        
        ## Declare the event
        actor_in_front_event_3 = xosc.Event("ActorDrivesAway", xosc.Priority.overwrite)

        ## Action
        sin_time_action_3 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.distance, 500)
        actor_in_front_action_3 = xosc.AbsoluteSpeedAction(10, sin_time_action_3)

        ### add action to the event
        actor_in_front_event_3.add_action("ActorDrivesAway", actor_in_front_action_3)
        
        ## Trigger
        trigger_cond_event_3 = xosc.StoryboardElementStateCondition(xosc.StoryboardElementType.action,"ActorStopsAndWaits",
                xosc.StoryboardElementState.completeState,
        )
        actor_in_front_event_3.add_trigger(
            xosc.ValueTrigger("AfterActorStopsAndWaits", 0, xosc.ConditionEdge.rising, trigger_cond_event_3)
        )
        
        return [actor_in_front_event_1, actor_in_front_event_2, actor_in_front_event_3]

    def _create_event_pedestrian_crossing_front(self):

        # EVENT 1 - Pedestrian_Starts_Walking

        ## Declare the event
        ped_crossing_front_event_1 = xosc.Event("PedestrianStartsWalking", xosc.Priority.overwrite)

        ## Action
        sin_time_action_1 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.distance, 4.0)
        ped_crossing_front_action_1 = xosc.AbsoluteSpeedAction(10, sin_time_action_1)
        ### add action to the event
        ped_crossing_front_event_1.add_action("PedestrianStartsWalking", ped_crossing_front_action_1)

        ## Start Trigger
        s, offset, lane_id, road_id = self.lane_position_parameters["hero"] ## start the trigger as soon as the hero starts moving.

        pos_trigger_event_1 = xosc.LanePosition(s, offset, lane_id, road_id, xosc.Orientation(0, 0, 0, xosc.ReferenceContext.relative))
        trigger_cond_event_1 = xosc.ReachPositionCondition(
            position=pos_trigger_event_1,
            tolerance=2.0
        )

        ## add trigger to the event 
        ped_crossing_front_event_1.add_trigger(
                xosc.EntityTrigger("StartCondition", 0, xosc.ConditionEdge.rising, trigger_cond_event_1, "hero",)
            )   
    
        # EVENT 2 - Pedestrian_Stops_And_Waits
        # Declare the event
        ped_crossing_front_event_2 = xosc.Event("PedestrianStopsAndWaits", xosc.Priority.overwrite)

        # Action
        sin_time_action_2 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 10.0) # wait for 10 secs
        ped_crossing_front_action_2 =  xosc.AbsoluteSpeedAction(0, sin_time_action_2)
        ped_crossing_front_event_2.add_action("PedestrianStopsAndWaits", ped_crossing_front_action_2)
        
        # Trigger
        trigger_cond_event_2 = xosc.StoryboardElementStateCondition(xosc.StoryboardElementType.action,"PedestrianStartsWalking",
                xosc.StoryboardElementState.completeState,
                )
        
        ped_crossing_front_event_2.add_trigger(
            xosc.ValueTrigger("AfterPedestrianWalks", 0, xosc.ConditionEdge.rising, trigger_cond_event_2)
        )

        # EVENT 3 - Pedestrian_Walks_Away
        # Declare the event
        ped_crossing_front_event_3 = xosc.Event("PedestrianWalksAway", xosc.Priority.overwrite)

        # Action
        sin_time_action_3 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.distance, 6.5)
        ped_crossing_front_action_3 = xosc.AbsoluteSpeedAction(2.0, sin_time_action_3)
        ### add action to the event
        ped_crossing_front_event_3.add_action("PedestrianStartsWalkingAway", ped_crossing_front_action_3)

        # Trigger
        condition_group_event_3 = xosc.ConditionGroup()
        trigger_event_3 = xosc.Trigger()

        ## Trigger 1
        trigger_cond_event_3_1 = xosc.StandStillCondition(
            duration=0.1
        )
        condition_group_event_3.add_condition(
            xosc.EntityTrigger("StartCondition", 0, xosc.ConditionEdge.rising, trigger_cond_event_3_1, "hero")
        )
        ## Trigger 2
        trigger_cond_event_3_2 = xosc.StoryboardElementStateCondition(xosc.StoryboardElementType.action,"PedestrianStopsAndWaits",
                xosc.StoryboardElementState.completeState,
                )
        
        condition_group_event_3.add_condition(
            xosc.ValueTrigger("PedestrianStartsWalkingAway", 0, xosc.ConditionEdge.rising, trigger_cond_event_3_2)
        )

        trigger_event_3.add_conditiongroup(condition_group_event_3)

        ped_crossing_front_event_3.add_trigger(trigger_event_3)


        # EVENT 4 - Pedestrian_Waits
        # Declare the event
        ped_crossing_front_event_4 = xosc.Event("PedestrianWaits", xosc.Priority.overwrite)
        
        # Action
        sin_time_action_4 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 10.0) # wait for 10 secs
        ped_crossing_front_action_4 =  xosc.AbsoluteSpeedAction(0, sin_time_action_4)
        ped_crossing_front_event_4.add_action("PedestrianWaits", ped_crossing_front_action_4)

        # Trigger
        condition_group_event_4 = xosc.ConditionGroup()
        trigger_event_4 = xosc.Trigger()

        ## Trigger 1
        trigger_cond_event_4_1 = xosc.StandStillCondition(
            duration=0.1
        )
        condition_group_event_4.add_condition(
            xosc.EntityTrigger("StartCondition", 0, xosc.ConditionEdge.rising, trigger_cond_event_4_1, "pedestrian")
        )

        ## Trigger 2
        trigger_cond_event_4_2 = xosc.StoryboardElementStateCondition(xosc.StoryboardElementType.action,"PedestrianStartsWalkingAway",
                xosc.StoryboardElementState.completeState,
                )
        
        condition_group_event_4.add_condition(
            xosc.ValueTrigger("AfterPedestrianStartsWalking", 0, xosc.ConditionEdge.rising, trigger_cond_event_4_2)
        )

        trigger_event_4.add_conditiongroup(condition_group_event_4)

        ped_crossing_front_event_4.add_trigger(trigger_event_4)

        # EVENT 5 - Pedestrian_Walks_Away_Completely
       # Declare the event
        ped_crossing_front_event_5 = xosc.Event("PedestrianWalksAwayCompletely", xosc.Priority.overwrite)

        # Action
        sin_time_action_5 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.distance, 10)
        ped_crossing_front_action_5 = xosc.AbsoluteSpeedAction(2.0, sin_time_action_5)
        ### add action to the event
        ped_crossing_front_event_5.add_action("PedestrianStartsWalkingAwayCompletely", ped_crossing_front_action_5)

        # Trigger
        condition_group_event_5 = xosc.ConditionGroup()
        trigger_event_5 = xosc.Trigger()

        ## Trigger 1
        trigger_cond_event_5_1 = xosc.StandStillCondition(
            duration=0.1
        )
        condition_group_event_5.add_condition(
            xosc.EntityTrigger("StartCondition", 0, xosc.ConditionEdge.rising, trigger_cond_event_5_1, "hero")
        )
        ## Trigger 2
        trigger_cond_event_5_2 = xosc.StoryboardElementStateCondition(xosc.StoryboardElementType.action,"PedestrianWaits",
                xosc.StoryboardElementState.completeState,
                )
        
        condition_group_event_5.add_condition(
            xosc.ValueTrigger("PedestrianWalksAwayCompletely", 0, xosc.ConditionEdge.rising, trigger_cond_event_5_2)
        )

        trigger_event_5.add_conditiongroup(condition_group_event_5)

        ped_crossing_front_event_5.add_trigger(trigger_event_5)

        return [ped_crossing_front_event_1, ped_crossing_front_event_2, ped_crossing_front_event_3, ped_crossing_front_event_4, ped_crossing_front_event_5]

    def _create_event_bicycle_crossing_front(self):
        # EVENT 1 - CyclistStartsWalking

        ## Declare the event
        cycle_crossing_front_event_1 = xosc.Event("BicycleStarts", xosc.Priority.overwrite)

        ## Action
        sin_time_action_1 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.distance, 3.0)
        cycle_crossing_front_action_1 = xosc.AbsoluteSpeedAction(5, sin_time_action_1)
        ### add action to the event
        cycle_crossing_front_event_1.add_action("BicycleStarts", cycle_crossing_front_action_1)

        ## Start Trigger
        s, offset, lane_id, road_id = self.lane_position_parameters["hero"] ## start the trigger as soon as the hero starts moving.

        pos_trigger_event_1 = xosc.LanePosition(s, offset, lane_id, road_id, xosc.Orientation(0, 0, 0, xosc.ReferenceContext.relative))
        trigger_cond_event_1 = xosc.ReachPositionCondition(
            position=pos_trigger_event_1,
            tolerance=2.0
        )

        ## add trigger to the event 
        cycle_crossing_front_event_1.add_trigger(
                xosc.EntityTrigger("StartCondition", 0, xosc.ConditionEdge.rising, trigger_cond_event_1, "hero",)
            )   
    
        # EVENT 2 -Cyclist_Stops_And_Waits
        # Declare the event
        cycle_crossing_front_event_2 = xosc.Event("BicycleStopsAndWaits", xosc.Priority.overwrite)

        # Action
        sin_time_action_2 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 10.0) # wait for 10 secs
        cycle_crossing_front_action_2 =  xosc.AbsoluteSpeedAction(0, sin_time_action_2)
        cycle_crossing_front_event_2.add_action("BicycleStopsAndWaits", cycle_crossing_front_action_2)
        
        # Trigger
        condition_group_event_2 = xosc.ConditionGroup()
        trigger_event_2 = xosc.Trigger()

        ## Trigger 1
        trigger_cond_event_2_1 = xosc.StandStillCondition(
            duration=0.1
        )
        condition_group_event_2.add_condition(
            xosc.EntityTrigger("StartCondition", 0, xosc.ConditionEdge.rising, trigger_cond_event_2_1, "hero")
        )
        ## Trigger 2
        trigger_cond_event_2_2 = xosc.StoryboardElementStateCondition(xosc.StoryboardElementType.action,"BicycleStarts",
                xosc.StoryboardElementState.completeState,
                )
        
        condition_group_event_2.add_condition(
            xosc.ValueTrigger("AfterBicycleStarts", 0, xosc.ConditionEdge.rising, trigger_cond_event_2_2)
        )

        trigger_event_2.add_conditiongroup(condition_group_event_2)

        cycle_crossing_front_event_2.add_trigger(trigger_event_2)

        # EVENT 3 - Cyclist_Walks_Away
        # Declare the event
        cycle_crossing_front_event_3 = xosc.Event("BicycleDrivesAway", xosc.Priority.overwrite)

        # Action
        sin_time_action_3 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.distance, 6.5)
        cycle_crossing_front_action_3 = xosc.AbsoluteSpeedAction(2.0, sin_time_action_3)
        ### add action to the event
        cycle_crossing_front_event_3.add_action("BicycleDrivesAway", cycle_crossing_front_action_3)

        # Trigger
        condition_group_event_3 = xosc.ConditionGroup()
        trigger_event_3 = xosc.Trigger()

        ## Trigger 1
        trigger_cond_event_3_1 = xosc.StandStillCondition(
            duration=0.1
        )
        condition_group_event_3.add_condition(
            xosc.EntityTrigger("StartCondition", 0, xosc.ConditionEdge.rising, trigger_cond_event_3_1, "hero")
        )
        ## Trigger 2
        trigger_cond_event_3_2 = xosc.StoryboardElementStateCondition(xosc.StoryboardElementType.action,"BicycleStopsAndWaits",
                xosc.StoryboardElementState.completeState,
                )
        
        condition_group_event_3.add_condition(
            xosc.ValueTrigger("AfterBicycleStopsAndWaits", 0, xosc.ConditionEdge.rising, trigger_cond_event_3_2)
        )

        trigger_event_3.add_conditiongroup(condition_group_event_3)

        cycle_crossing_front_event_3.add_trigger(trigger_event_3)

        return [cycle_crossing_front_event_1, cycle_crossing_front_event_2, cycle_crossing_front_event_3]

    def _create_event_bicycle_in_front(self, travel_for_distance = 15.0, waiting_time = 5.0):
        # Event 1 - Bicycle drives

        ## Declare the event
        cycle_in_front_event_1 = xosc.Event("BicycleStarts", xosc.Priority.overwrite)

        ## Action
        sin_time_action_1 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.distance, travel_for_distance)
        cycle_in_front_action_1 = xosc.AbsoluteSpeedAction(7, sin_time_action_1)
        ### add action to the event
        cycle_in_front_event_1.add_action("BicycleStarts", cycle_in_front_action_1)

        ## Start Trigger
        cycle_in_front_event_1.add_trigger(
            xosc.ValueTrigger(
                "StartCondition",
                0,
                xosc.ConditionEdge.rising,
                xosc.SimulationTimeCondition(0.1, xosc.Rule.greaterThan),
            )
        )

        # Event 2 - Bicycle waits 
        cycle_in_front_event_2 = xosc.Event("BicycleStopsAndWaits", xosc.Priority.overwrite)

        # Action
        sin_time_action_2 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, waiting_time) # wait for 3 secs
        cycle_in_front_action_2 =  xosc.AbsoluteSpeedAction(0, sin_time_action_2)
        cycle_in_front_event_2.add_action("BicycleStopsAndWaits", cycle_in_front_action_2)
        
        # Trigger
        trigger_cond_event_2 = xosc.StoryboardElementStateCondition(xosc.StoryboardElementType.action,"BicycleStarts",
                xosc.StoryboardElementState.completeState,
                )
        
        cycle_in_front_event_2.add_trigger(
            xosc.ValueTrigger("AfterBicycleStarts", 0, xosc.ConditionEdge.rising, trigger_cond_event_2)
        )

        # Event 3 - Bicycle drives away
        
        ## Declare the event
        cycle_in_front_event_3 = xosc.Event("BicycleDrivesAway", xosc.Priority.overwrite)

        ## Action
        sin_time_action_3 = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.distance, 3.0)
        cycle_in_front_action_3 = xosc.AbsoluteSpeedAction(5, sin_time_action_3)

        ### add action to the event
        cycle_in_front_event_3.add_action("BicycleDrivesAway", cycle_in_front_action_3)
        
        ## Trigger
        trigger_cond_event_3 = xosc.StoryboardElementStateCondition(xosc.StoryboardElementType.action,"BicycleStopsAndWaits",
                xosc.StoryboardElementState.completeState,
        )
        cycle_in_front_event_3.add_trigger(
            xosc.ValueTrigger("AfterBicycleStopsAndWaits", 0, xosc.ConditionEdge.rising, trigger_cond_event_3)
        )
        
        return [cycle_in_front_event_1, cycle_in_front_event_2, cycle_in_front_event_3]

    def _create_maneuver_groups(self, name, events, maneuver_number):
        maneuver = xosc.Maneuver(f"Maneuver {maneuver_number}")

        for event in events:
            maneuver.add_event(event)

        maneuver_group = xosc.ManeuverGroup(f"Group {maneuver_number}")
        maneuver_group.add_actor(name)
        maneuver_group.add_maneuver(maneuver)

        return maneuver_group
    
    def _create_act_overall_start_trigger(self, egoname, start_distance_travelled = 0.1):
        # overall start condition - traveled Distance = 0.1 meters
        
        start_condition = xosc.TraveledDistanceCondition(start_distance_travelled)
        overall_start_trigger = xosc.EntityTrigger("OverallStartCondition", 0, xosc.ConditionEdge.rising, start_condition, egoname)

        return overall_start_trigger
    
    def _create_act_overall_stop_trigger(self, egoname, targetname, stop_distance_travelled = 250.0, stop_collision = False):
        
        # assign stop trigger from starting till the end of the single lane
        if "single_lane" in self.scenario_location or "multi_lane" in self.scenario_location:
            stop_distance_travelled = float(self.chosen_road_details.length)

        overall_stop_trigger = xosc.Trigger('stop')

        # stop condition - travelled distance = 100 meters
        stop_trigger_group =  xosc.ConditionGroup('stop')
        stop_condition = xosc.TraveledDistanceCondition(stop_distance_travelled)
        stop_trigger_1 = xosc.EntityTrigger("EndCondition", 0, xosc.ConditionEdge.rising, stop_condition, egoname)
        stop_trigger_group.add_condition(stop_trigger_1)

        stop_condition_2 = xosc.StandStillCondition(
            duration=10
        )
        stop_trigger_group.add_condition(
            xosc.EntityTrigger("EndStandStillCondition", 0, xosc.ConditionEdge.rising, stop_condition_2, "hero")
        )
        overall_stop_trigger.add_conditiongroup(stop_trigger_group)

        # stop condition - collision with other vehicle or pedestrian
        if stop_collision: 
            if "pedestrian" in targetname:
                stop_trigger_group_2 =  xosc.ConditionGroup('stop')
                stop_condition_2 = xosc.CollisionCondition(xosc.ObjectType.pedestrian) 
                stop_trigger_2 = xosc.EntityTrigger("CollisionCondition", 0, xosc.ConditionEdge.none, stop_condition_2, egoname)
                stop_trigger_group_2.add_condition(stop_trigger_2)
                overall_stop_trigger.add_conditiongroup(stop_trigger_group_2)

            elif "adversary" in targetname or "bicycle" in  targetname:
                stop_trigger_group_2 =  xosc.ConditionGroup('stop')
                stop_condition_2 = xosc.CollisionCondition(xosc.ObjectType.vehicle) 
                stop_trigger_2 = xosc.EntityTrigger("CollisionCondition", 0, xosc.ConditionEdge.none, stop_condition_2, egoname)
                stop_trigger_group_2.add_condition(stop_trigger_2)
                overall_stop_trigger.add_conditiongroup(stop_trigger_group_2)

        return overall_stop_trigger
    
    def _evaluation_metrics(self, stop_triggers_name, distance_name = "", distance=""):
        condition = xosc.ParameterCondition(distance_name, distance, xosc.Rule.lessThan)
        stop_trigger = xosc.ValueTrigger(stop_triggers_name, 0, xosc.ConditionEdge.rising, condition)
        return stop_trigger

    def _save_openscenario(self, sce):
        # TODO provide a proper filename later - done

        # specify the folder path where you want to save the file
        # generate the filename with the folder path
        
        folder_name  = self.map_name +"__"+self.scenario_information+"__"+ self.scenario_location

        file_name = "generate_scenario/output_scenarios/" + folder_name
        file_path = Path.cwd().parent / Path(file_name).resolve()
        scenario_number = [0]
        for f in file_path.glob("*.xosc"):
            if f is not None:
                scenario_number.append(int(str(f).split("\\")[-1].split(".xosc")[0]))
        
        final_scenario_number  = max(scenario_number)+1
        
  
        if not file_path.exists():
            file_path.mkdir(parents=True, exist_ok=True)

        final_file_path = str(file_path) + "//"+ str(final_scenario_number) +".xosc"
        sce.write_xml(final_file_path)
                   
    ## self.vehicle_types is a list containing [hero, actor, bicycle, walker]
    def scenario(self, egoname, targetname):
        ### create init
        init = xosc.Init()

        ### create catalogs
        catalog = xosc.Catalog()

        ### create road
        road = xosc.RoadNetwork(
            roadfile=self.map_name, scenegraph=""
        )

        ### create parameters
        paramdec = xosc.ParameterDeclarations()

        ### create entities
        entities = xosc.Entities()

        ### initialize the environment 
        env = self._create_environment()
        init.add_global_action(env) 

        ### initialize the actions for ego and other vehicle and walker
        for vehicle_type in self.vehicle_types:
            if ("hero" in vehicle_type) or ("bicycle" in vehicle_type) or ("adversary" in vehicle_type):
                vehicle = self._create_vehicle(vehicle_type)
                entities.add_scenario_object(vehicle_type, vehicle)

            if "pedestrian" in vehicle_type:
                walker = self._create_walker()
                entities.add_scenario_object(vehicle_type, walker)
        
        for vehicle_type in self.vehicle_types:
            if ("hero" == vehicle_type):
                teleport_action, absolute_speed_action = self._create_init_vehicle_action(vehicle_type, self.lane_position_parameters[vehicle_type])
                init.add_init_action(vehicle_type, teleport_action) 
                init.add_init_action(vehicle_type, absolute_speed_action)

                # carla autopilot enabler - add the vehicle below if wanted to make them operate on autopilot
                controller_action = self._create_init_vehicle_control(name=vehicle_type, osc_controller=self.osc_controller)
                init.add_init_action(vehicle_type, controller_action)
                
            elif ("adversary" in vehicle_type):
                teleport_action, absolute_speed_action = self._create_init_vehicle_action(vehicle_type, self.lane_position_parameters[vehicle_type])
                init.add_init_action(vehicle_type, teleport_action) 
                init.add_init_action(vehicle_type, absolute_speed_action)

                # Always assign the actor with autopilot.
                controller_action = self._create_init_vehicle_control(name=vehicle_type, osc_controller=self.osc_controller)
                init.add_init_action(vehicle_type, controller_action)

            elif ("bicycle" in vehicle_type):
                if self.scenario_information in ["hero_and_bicycle_crossing_in_front"]:
                    teleport_action = self._create_init_walker_action(self.lane_position_parameters[vehicle_type])
                    init.add_init_action(vehicle_type, teleport_action) 
                else:
                    teleport_action, absolute_speed_action = self._create_init_vehicle_action(vehicle_type, self.lane_position_parameters[vehicle_type])
                    init.add_init_action(vehicle_type, teleport_action) 
                    init.add_init_action(vehicle_type, absolute_speed_action)

            elif "pedestrian" in vehicle_type:
                teleport_action = self._create_init_walker_action(self.lane_position_parameters[vehicle_type])
                init.add_init_action(vehicle_type, teleport_action) 
        
        ## Create an route planner for hero and actor
        # assign route action - https://github.com/pyoscx/scenariogeneration/blob/main/examples/xosc/route_in_crossing.py
        
        # Acquire Position Action

        # Assign a route planner for the hero vehicle
        
        hero_events = self._create_event_hero_route()

        manuever_group_1 = self._create_maneuver_groups(name=egoname, events=hero_events, maneuver_number=1)

        # Assign a event for the other vehicles
        # if self.scenario_information == "hero_and_adversary_same_direction_route":
        #     events = self._create_event_route_creation()

        # TODO Sceanrio - Bicycle crossing infront (Done) and actor driving and stops for some time and drives again
        manuever_group_2, manuever_group_3 = None, None
        
        if self.scenario_information in ["hero_and_adversary_same_direction_route", "hero_and_adversary_different_direction_route", "hero_and_adversary_on_the_same_lane"]:
            events = self._create_event_actor_in_front()
             ## create the storyboard   
            manuever_group_2 = self._create_maneuver_groups(name=targetname, events=events, maneuver_number=2)

        elif self.scenario_information in ["hero_and_pedestrian_crossing_in_front", "hero_adversary_and_pedestrian_crossing_in_front", "hero_bicycle_and_pedestrian_crossing_in_front"]:
            events = self._create_event_pedestrian_crossing_front()
            ## create the storyboard   
            manuever_group_2 = self._create_maneuver_groups(name=targetname, events=events, maneuver_number=2)

        elif self.scenario_information in ["hero_and_bicycle_crossing_in_front"]:
            events = self._create_event_bicycle_crossing_front()
            ## create the storyboard   
            manuever_group_2 = self._create_maneuver_groups(name=targetname, events=events, maneuver_number=2)

        elif self.scenario_information in ["hero_and_bicycle_on_the_same_lane", "hero_adversary_and_bicycle_on_the_same_lane", "hero_and_bicycle_same_direction_route", "hero_and_bicycle_opposite_direction_route", "hero_and_bicycle_same_direction_adversary_opposite_route"]:
            events = self._create_event_bicycle_in_front()
            ## create the storyboard   
            manuever_group_2 = self._create_maneuver_groups(name=targetname, events=events, maneuver_number=2)

        elif self.scenario_information in ["hero_and_2_pedestrians_crossing_in_front", "hero_adversary_and_2_pedestrians_crossing_in_front"]:
            events = {}
            for targetname in ["pedestrian", "pedestriantwo"]:
                events[targetname] = self._create_event_pedestrian_crossing_front()
            ## create the storyboard   
            manuever_group_2 = self._create_maneuver_groups(name="pedestrian", events=events["pedestrian"], maneuver_number=2)
            
             ## create the storyboard   
            manuever_group_3 = self._create_maneuver_groups(name="pedestriantwo", events=events["pedestriantwo"], maneuver_number=3)

        # overall start and stop condition of the action (Act) triggered by "hero" car always
        overall_start_trigger = self._create_act_overall_start_trigger(egoname=egoname) 

        # change the stop_collision = False.
        overall_stop_trigger = self._create_act_overall_stop_trigger(egoname=egoname, targetname=targetname, stop_collision=False)
        act = xosc.Act("Act 1", overall_start_trigger, overall_stop_trigger)

        ## add the act manuever group
        act.add_maneuver_group(manuever_group_1)
        if not manuever_group_2 == None:
            act.add_maneuver_group(manuever_group_2)
        
        if not manuever_group_3 == None:
            act.add_maneuver_group(manuever_group_3)


        ## Final Evaluation metrics and stop triggers
        # create and add them to a ConditionGroup (and logic)
        evaluation_stop_trigger = xosc.ConditionGroup('stop')

        ### initialize the final stop triggers
        if self.osc_controller == "adas":
            for metrics in self.dmeta.adas_evaluation_metrics:
                if metrics == "criteria_DrivenDistanceTest":
                    evaluation_stop_trigger.add_condition(self._evaluation_metrics(metrics, distance_name = "distance_success", distance="70"))
                
                elif metrics == "criteria_AverageVelocityTest":
                    evaluation_stop_trigger.add_condition(self._evaluation_metrics(metrics, distance_name = "avg_velocity_success", distance="20"))
                    
                else:
                    evaluation_stop_trigger.add_condition(self._evaluation_metrics(metrics))

        elif self.osc_controller == "carla_autopilot":
            for metrics in self.dmeta.carla_autopilot_evaluation_metrics:
                if metrics == "criteria_DrivenDistanceTest":
                    distance_trigger = "70"

                    # assign stop trigger from starting till the end of the single lane
                    if "single_lane" in self.scenario_location or "multi_lane" in self.scenario_location:
                        distance_trigger = str(float(self.chosen_road_details.length))
                    
                    evaluation_stop_trigger.add_condition(self._evaluation_metrics(metrics, distance_name = "distance_success", distance=distance_trigger))

                elif metrics == "criteria_AverageVelocityTest":
                    evaluation_stop_trigger.add_condition(self._evaluation_metrics(metrics, distance_name = "avg_velocity_success", distance="20"))

                else:
                    evaluation_stop_trigger.add_condition(self._evaluation_metrics(metrics))
            
        ### create the storyboard
        story_board = xosc.StoryBoard(init, evaluation_stop_trigger)

        # TODO the below act has all the action needed including manuever, manuever group, events
        story_board.add_act(act)

        ## create the scenario
        sce = xosc.Scenario(
            self.scenario_information,
            "John Pravin",
            paramdec,
            entities=entities,
            storyboard=story_board,
            roadnetwork=road,
            catalog=catalog,
            osc_minor_version=self.open_scenario_version
        )

        # uncomment to print the resulting xml
        # prettyprint(sce.get_element())

        # # print the hero lane position and route position
        # print("hero - s, offset, lane_id, road_id = ", self.lane_position_parameters["hero"])
        # print("route  - s, offset, lane_id, road_id = ", self.lane_position_parameters["route"])

        # save the generated scenario files
        self._save_openscenario(sce)

if __name__ == "__main__":
    
    vehicle_types = ["hero", "route", "bicycle", "pedestrian"]
    se = Scenario(map_name = "Karlsruhe", vehicle_types=vehicle_types, scenario_location="3_way_intersection", scenario_information="hero_bicycle_and_pedestrian_crossing_in_front", osc_controller = "carla_autopilot")
    se.scenario(vehicle_types[0], vehicle_types[-1])
                                                                            # "3_way_intersection", "4_way_intersection"
    """ 

    Scenarios: 

    3-way Intersection and 4-way intersection:
        ACTOR 
        1. hero_and_actor_same_direction_route - hero_and_adversary_same_direction_route
        2. hero_and_actor_opposite_direction_route - hero_and_adversary_different_direction_route

        PEDESTRIAN 
        1. hero_and_pedestrian_crossing_in_front
        2. hero_actor_and_pedestrian_crossing_in_front - hero_adversary_and_pedestrian_crossing_in_front
        3. hero_bicycle_and_pedestrian_crossing_in_front - similar to the above one

        TODO: 
        4. hero_and_2_pedestrians_crossing_in_front
        5. hero_actor_and_2_pedestrian_crossing_in_front - hero_adversary_and_2_pedestrians_crossing_in_front

        BICYCLE
        1. hero_and_bicycle_same_direction_route
        2. hero_and_bicycle_opposite_direction_route
        3. hero_and_bicycle_same_direction_actor_opposite_route - hero_and_bicycle_same_direction_adversary_opposite_route

    Single Lane Intersection or Multiple lane:
        Pedestrian
        1. hero_and_pedestrian_crossing_in_front

        Bicycle
        2. hero_and_bicycle_crossing_in_front
        3. hero_and_bicycle_on_the_same_lane
        4. hero_actor_and_bicycle_same_lane - hero_adversary_and_bicycle_on_the_same_lane

        Actor
        5. hero_and_actor_same_lane - hero_and_adversary_on_the_same_lane

        TODO
        6.	Hero and pedestrian on the same lane opposite to each other: 
        7.	Hero and actor on the same lane opposite to each other. 

    First display: Towns
    Second display: Scenario_location
    Three display: Vehicle_types
    Four display: Scenario_information
    Fifth display: ADAS or CARLA 
    
    use them to generate the scenarios.
    

    ["Town01", "Town02, "Karlsruhe"]
    --> Town01 - Single_lane and 3_way_intersection, --> Town02 - single_lane and 3_way_intersection, --> Karlsruhe - single_lane & 4_way_intersection
    ["single_lane", "3_way_intersection", "4_way_intersection"]
    ["hero", "adversary", "bicycle", "pedestrian"]
    controller = "adas", "carla_autopilot"

    Scenario information: 
    
    3_way_intersection - DONE
        1. hero_and_actor_route_planner - ["hero", "route", "adversary"]
        2. hero_and_pedestrian_crossing_front  - ["hero", "route", "pedestrian"]
        3. hero_actor_and_pedestrian_crossing_front - ["hero", "route", "adversary", "pedestrian"]
        4. hero_and_bicycle_on_the_same_lane -  ["hero", "route", "bicycle"]
        5. hero_actor_and_bicycle_same_lane - ["hero", "route", "adversary", "bicycle"]

    Single_lane - DONE
        1. hero_and_bicycle_on_the_same_lane - ["hero", "route", "bicycle"]
        2. hero_actor_and_bicycle_same_lane = ["hero", "route", "adversary", "bicycle"]
        3. hero_and_pedestrian_crossing_front = ["hero", "route", "pedestrian"]
        4. hero_and_actor_same_lane - ["hero"., "route", "bicycle"]

    Enable CARLA Autopliot

    https://github.com/carla-simulator/scenario_runner/issues/801

    https://github.com/carla-simulator/scenario_runner/issues/577


    Controller Module value simple_vehicle_control or carla_autopilot

    1. There is basic control, actor_control simple_vehicle_control or carla_autopilot and pedestrian control too. (I would not be needing the pedestrian control)

    https://github.com/carla-simulator/scenario_runner/tree/master/srunner/scenariomanager/actorcontrols
    """

