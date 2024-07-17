from xml.etree import ElementTree as ET 

class BaseClass:
    __slots__ = {"id", "name"}

    def __init__(self, id, name):
        self.id = id
        self.name = name
        
class Road(BaseClass):
    __slots__=["length", "is_in_junction_id", "is_in_junction", "predecessor_name", "predecessor_id", "successor_name", "successor_id", "left_driving_lane_ids", "right_driving_lane_ids", "left_sidewalk_lane_ids", "right_sidewalk_lane_ids"]
    def __init__(self, id, name, length, is_in_junction_id, is_in_junction):
        super().__init__(id, name)
        self.length = length
        self.is_in_junction = is_in_junction
        self.is_in_junction_id = is_in_junction_id
        self.predecessor_name = ""
        self.predecessor_id = 0
        self.successor_name = ""
        self.successor_id = 0
        self.left_driving_lane_ids = []
        self.right_driving_lane_ids = []
        self.left_sidewalk_lane_ids = []
        self.right_sidewalk_lane_ids= []

    @classmethod
    def from_xodr(cls, xodr_road_element):
        if xodr_road_element.attrib["junction"] == "-1":
            is_in_junction = False
            is_in_junction_id = -1
        else:
            is_in_junction = True
            is_in_junction_id = xodr_road_element.attrib["junction"]


        road_class = cls(id = xodr_road_element.attrib["id"], name= xodr_road_element.attrib["name"], length= xodr_road_element.attrib["length"], is_in_junction_id=is_in_junction_id, is_in_junction= is_in_junction)
        
        for road_element in xodr_road_element:
            # Extract the link details 
            if road_element.tag == "link":
                # Extract predecessor and successor of a road
                for link_element in road_element:
                    if link_element.tag == "predecessor":
                        road_class.predecessor_name = link_element.attrib["elementType"]
                        road_class.predecessor_id = link_element.attrib["elementId"]
                    elif link_element.tag == "successor":
                        road_class.successor_name = link_element.attrib["elementType"]
                        road_class.successor_id = link_element.attrib["elementId"]

            # Extract the lanes details 
            elif road_element.tag == "lanes":
                left_id, left_sidwalk_id, right_id, right_sidewalk_id = [], [], [], []
                for lane_section_element in road_element:
                    if lane_section_element.tag == "laneSection":
                        for lanes in lane_section_element:
                            if lanes.tag == "left":
                                for left in lanes:
                                    if left.attrib["type"] == "driving" and left.attrib["id"] not in left_id:
                                        left_id.append(left.attrib["id"])
                                    elif left.attrib["type"] == "sidewalk" and left.attrib["id"] not in left_id:
                                        left_sidwalk_id.append(left.attrib["id"])

                            elif lanes.tag == "right":
                                for right in lanes:
                                    if right.attrib["type"] == "driving"and right.attrib["id"] not in right_id:
                                        right_id.append(right.attrib["id"])

                                    elif right.attrib["type"] == "sidewalk"and right.attrib["id"] not in right_id:
                                        right_sidewalk_id.append(right.attrib["id"])
                                        
                            elif lanes.tag == "center":
                                pass
                            
                road_class.left_driving_lane_ids = left_id
                road_class.right_driving_lane_ids = right_id
                road_class.left_sidewalk_lane_ids = left_sidwalk_id
                road_class.right_sidewalk_lane_ids = right_sidewalk_id
                
        return road_class

class Junction(BaseClass):
    __slots__=["id", "name", "junction_connect_list"]
    def __init__(self, id, name):
        super().__init__(id, name)
        self.junction_connect_list: list[Junction_Connection] = []

    @classmethod
    def from_xodr(cls, xodr_junction_element):
        junction_elem_obj = cls(id=xodr_junction_element.attrib["id"], name=xodr_junction_element.attrib["name"])

        for junction_element in xodr_junction_element:
            if junction_element.tag == "connection":
                junction_connection = Junction_Connection(connecting_id = junction_element.attrib["id"], incoming_road= junction_element.attrib["incomingRoad"], connecting_road= junction_element.attrib["connectingRoad"],  contact_point=junction_element.attrib["contactPoint"])
                for junction_lane in junction_element:
                    if junction_lane.tag == "laneLink":
                        junction_connection.lane_link = (junction_lane.attrib["from"], junction_lane.attrib["to"])

                junction_elem_obj.junction_connect_list.append(junction_connection)
        return junction_elem_obj

class Junction_Connection:
    __slots__=["connecting_id", "incoming_road", "connecting_road", "contact_point", "lane_link"]
    def __init__(self, connecting_id, incoming_road, connecting_road, contact_point):
        self.connecting_id = connecting_id
        self.incoming_road = incoming_road
        self.connecting_road = connecting_road
        self.contact_point = contact_point
        self.lane_link = ()
    