import streamlit as st
from scenario_generator import Scenario

def map_name_interface():
    # st.session_state.map_name = st.radio("**Select the Town for simulation**",
    #     ["Town01", "Town02", "Karlsruhe"],
    #     index=None,
        
    # )
    st.session_state.map_name = st.radio("**Select the Town for simulation**",
        ["Town01", "Karlsruhe"],
        index=None,
        
    )

def scenario_location_interface():

    if st.session_state.map_name == "Town01" or st.session_state.map_name == "Town02":
        st.session_state.scenario_location = st.radio("**Select the Scenario Location for simulation**",
        ["single_lane", "3_way_intersection"],
        index=None,
        )

    elif st.session_state.map_name == "Karlsruhe":
        st.session_state.scenario_location = st.radio("**Select the Scenario Location for simulation**",
            ["single_lane", "multi_lane", "3_way_intersection", "4_way_intersection"],
            index=None,
        )
        
def scenario_information_interface():
    
    if st.session_state.scenario_location == "single_lane" or st.session_state.scenario_location == "multi_lane":
        st.session_state.scenario_information = st.radio("**Select the Scenario information for simulation**",
            ["hero_and_adversary_on_the_same_lane", 
            "hero_and_bicycle_crossing_in_front", 
            "hero_and_bicycle_on_the_same_lane", 
            "hero_adversary_and_bicycle_on_the_same_lane", 
            "hero_and_pedestrian_crossing_in_front",
            ],
            index=None,
        )

    elif st.session_state.scenario_location == "3_way_intersection" or st.session_state.scenario_location == "4_way_intersection":
        st.session_state.scenario_information = st.radio("**Select the Scenario information for simulation**",
            [
            "hero_and_adversary_same_direction_route", 
            "hero_and_adversary_different_direction_route", 
            "hero_and_pedestrian_crossing_in_front", 
            "hero_adversary_and_pedestrian_crossing_in_front", 
            "hero_bicycle_and_pedestrian_crossing_in_front", 
            "hero_and_bicycle_same_direction_route", 
            "hero_and_bicycle_opposite_direction_route",
            "hero_and_bicycle_same_direction_adversary_opposite_route", 
            "hero_and_2_pedestrians_crossing_in_front",
            "hero_adversary_and_2_pedestrians_crossing_in_front"
            ],
            index=None,
        )


def osc_controller_interface():

    if st.session_state.vehicle_types:
        st.session_state.osc_controller = st.radio("**Select the OSC Controller for simulation**",
                    [
                    "adas_thesis", 
                    "carla_autopilot"
                    ],
                    index=None,
                )
            
def extract_vehicle():

    if st.session_state.scenario_information == "hero_and_adversary_on_the_same_lane" or st.session_state.scenario_information == "hero_and_adversary_same_direction_route" or st.session_state.scenario_information == "hero_and_adversary_different_direction_route":
        st.session_state.vehicle_types = ["hero", "route", "adversary"]
        st.write("Vehicle Corresponding the Scenario are", st.session_state.vehicle_types)

    if st.session_state.scenario_information == "hero_and_bicycle_on_the_same_lane" or st.session_state.scenario_information == "hero_and_bicycle_crossing_in_front" or st.session_state.scenario_information == "hero_and_bicycle_same_direction_route" or st.session_state.scenario_information == "hero_and_bicycle_opposite_direction_route":
        st.session_state.vehicle_types = ["hero", "route", "bicycle"]
        st.write("Vehicle Corresponding the Scenario are", st.session_state.vehicle_types)

    if st.session_state.scenario_information == "hero_and_pedestrian_crossing_in_front" or st.session_state.scenario_information == "hero_and_pedestrian_crossing_in_front":
        st.session_state.vehicle_types = ["hero", "route", "pedestrian"]
        st.write("Vehicle Corresponding the Scenario are", st.session_state.vehicle_types)
    
    if st.session_state.scenario_information == "hero_bicycle_and_pedestrian_crossing_in_front": 
        st.session_state.vehicle_types = ["hero", "route", "bicycle", "pedestrian"]
        st.write("Vehicle Corresponding the Scenario are", st.session_state.vehicle_types)
    
    if st.session_state.scenario_information == "hero_adversary_and_pedestrian_crossing_in_front":
        st.session_state.vehicle_types = ["hero", "route", "adversary", "pedestrian"]
        st.write("Vehicle Corresponding the Scenario are", st.session_state.vehicle_types)
    
    if st.session_state.scenario_information == "hero_adversary_and_bicycle_on_the_same_lane" or st.session_state.scenario_information == "hero_and_bicycle_same_direction_adversary_opposite_route":
        st.session_state.vehicle_types = ["hero", "route", "adversary", "bicycle"]
        st.write("Vehicle Corresponding the Scenario are", st.session_state.vehicle_types)
    
    if st.session_state.scenario_information == "hero_and_2_pedestrians_crossing_in_front":
        st.session_state.vehicle_types = ["hero", "route", "pedestrian", "pedestriantwo"]
        st.write("Vehicle Corresponding the Scenario are", st.session_state.vehicle_types)
    
    if st.session_state.scenario_information == "hero_adversary_and_2_pedestrians_crossing_in_front":
        st.session_state.vehicle_types = ["hero", "route", "adversary", "pedestrian", "pedestriantwo"]
        st.write("Vehicle Corresponding the Scenario are", st.session_state.vehicle_types)
    

def main():
    st.sidebar.markdown('''<div> <h1> <b> <u> Carla Scenario Generation </u> </b> </h1> </div>''', unsafe_allow_html=True)
    st.sidebar.markdown('''<h4> <b> 
    Below are the authors details:</b></h4>''', unsafe_allow_html=True)
    st.sidebar.markdown('''
                        Name : John Pravin Arockiasamy \n
                        (<st180270@stud.uni-stuttgart.de>)\n
                        LinkedIn :  <https://www.linkedin.com/in/john-pravin/> \n
                        GitHub : <https://github.com/JohnPravin97> \n
                        ''')
    #Main Coding
    st.markdown('''<div align="center"> <h2> <b> Carla Scenario Generation  </b> </h2> </div>''', unsafe_allow_html=True)

    # st.title("Scenario Generator")
    with st.expander("select the below options for scenario generation:"):

        if "map_name" not in st.session_state:
            st.session_state.map_name = None
        
        if "scenario_location" not in st.session_state:
            st.session_state.scenario_location = None
        
        if "vehicle_types" not in st.session_state:
            st.session_state.vehicle_types = None
        
        if "scenario_information" not in st.session_state:
            st.session_state.scenario_information = None
        
        if "osc_controller" not in st.session_state:
            st.session_state.osc_controller = None

        # map_name = map_name_interface()
        
        # scenario_location = scenario_location_interface(map_name)

        # scenario_information = scenario_information_interface(scenario_location)
        
        # vehicle_types = extract_vehicle(scenario_information)

        # osc_controller = osc_controller_interface(vehicle_types)
        
        map_name_interface()
        
        scenario_location_interface()

        scenario_information_interface()

        extract_vehicle()

        osc_controller_interface()

        if st.button("finish"):
            # st.write(f"Selection: Map - {st.session_state.map_name} \n Scenario Location - {st.session_state.scenario_location}, \n Vehicle Types - {st.session_state.vehicle_types}, \n Scenario Information - {st.session_state.scenario_information}, Controller - {st.session_state.osc_controller}")
            se = Scenario(map_name=st.session_state.map_name, vehicle_types=st.session_state.vehicle_types, scenario_location=st.session_state.scenario_location, scenario_information=st.session_state.scenario_information, osc_controller=st.session_state.osc_controller)
            se.scenario(st.session_state.vehicle_types[0], st.session_state.vehicle_types[-1])
            st.markdown('''<div> <h5><b> Generated the scenario: </b></h5></div>''', unsafe_allow_html=True)
            st.write(f"**Map** -'{st.session_state.map_name}',  \n **Scenario Location** - '{st.session_state.scenario_location}',  \n **Vehicle Types** - '{st.session_state.vehicle_types}',  \n **Scenario Information** - '{st.session_state.scenario_information}',  \n **Controller** - '{st.session_state.osc_controller}'")

if __name__ == "__main__":
    main()


