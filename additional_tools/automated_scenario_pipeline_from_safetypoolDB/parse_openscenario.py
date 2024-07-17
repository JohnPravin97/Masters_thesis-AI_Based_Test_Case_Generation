from lxml import etree
import argparse
import random
from scenariogeneration import xosc

"""
Conversion from Openscenario 1.1 to 1.0
1. Add Fog and removed wind details for the conversion of openscenario 1.1 to 1.0 in enrvironment section using scenariogeneration package.(Needed for the scenarioGenaration packaage). 
2. Add Road Condition in environemnt section. 
3. Change greaterorEqual and lessorEqual to greaterthan or lessthan.
4. In Entitites, change vehicle name to a actual carla supported name like vehicle.tesla.model3. 
5. Use scenariogeneration python package to convert openscenario 1.1 to 1.0
"""

# Default Values
CARLA_VEHICLE_MODEL = ["vehicle.dodge.charger_police", "vehicle.tesla.model3", "vehicle.audi.tt", "vehicle.ford.mustang", "vehicle.jeep.wrangler_rubicon","vehicle.mercedes.coupe_2020",
                       "vehicle.carlamotors.carlacola"]
FOG_VISUAL_RANGE = "10000.0"
ROAD_CONDITION_FRICTION = "1.0"


def parse_openscenario(input_path, output_path):
    
    root = etree.parse(input_path).getroot()

    for xosc_element in root:
        # Add the Vehicle name of N1 and Ego to carla compatible one 
        if xosc_element.tag == "Entities":
            for so_element in xosc_element.iter("ScenarioObject"):
                if so_element.find("Vehicle") is not None:
                    veh_element = so_element.find("Vehicle") 
                    if not veh_element.attrib["name"].startswith("vehicle"):
                        veh_element.attrib["name"] = random.choice(CARLA_VEHICLE_MODEL)
                

        if xosc_element.tag == "Storyboard":
            # Work with StoryBoard - Weather
            for sb_element in xosc_element.iter("Environment"):
                if sb_element.find("Weather") is not None:
                    weather_element = sb_element.find("Weather")
                    #Add the Fog Element as the scenariogeneration requires that the os v1.1 has it.
                    if weather_element.find("Fog") is None:
                        fog_element = etree.SubElement(weather_element, "Fog")
                        fog_element.set("visualRange", FOG_VISUAL_RANGE)
                        
                    # Remove the Wind Element as the scenariogeneration requires that the os v1.1 removes it.
                    if weather_element.find("Wind") is not None:
                        for element in weather_element:
                            if element.tag == "Wind":
                                element.getparent().remove(element)

                # Add the RoadCondition Element as the scenario runner needs it
                if sb_element.find("RoadCondition") is None:
                    road_condition_element = etree.SubElement(sb_element, "RoadCondition")
                    road_condition_element.set("frictionScaleFactor", ROAD_CONDITION_FRICTION)
        
            # Work with the greaterthanorequal (SimulationTimeCondition) or lessthanorequal(RelativeDistanceCondition) problem
            for sb_element in xosc_element.iter("Condition"):
                if sb_element.find("ByValueCondition") is not None:
                    by_value_element = sb_element.find("ByValueCondition")
                    for sim_element in by_value_element:
                        if sim_element.tag == "SimulationTimeCondition":
                            if "Equal" in sim_element.attrib["rule"]:
                                sim_element.attrib["rule"] = sim_element.attrib["rule"].split("O")[0] + "Than"

                if sb_element.find("ByEntityCondition") is not None:
                    by_value_element = sb_element.find("ByEntityCondition")
                    for sim_element in by_value_element:
                        if sim_element.tag == "EntityCondition":
                            for entity_element in sim_element:
                                if entity_element.tag == "RelativeDistanceCondition":
                                    if "Equal" in entity_element.attrib["rule"]:
                                        entity_element.attrib["rule"] = entity_element.attrib["rule"].split("O")[0] + "Than"       
        
    with open(output_path, 'wb') as f:
        f.write(
            etree.tostring(
                root, pretty_print=True, xml_declaration=True
            )
        )

def convert_openscenarios(path, version = 0):
    scenario = xosc.ParseOpenScenario(path)
    scenario.header.setVersion(minor=version)
    out_path = path.split(".")[0] + "_v1_0.xosc"
    scenario.write_xml(out_path)

def main():
    parser = argparse.ArgumentParser(description='OpenScenario Parser')

    # Add arguments
    parser.add_argument('input_file', type=str, help='Provide a OpenScenario 1.1 input file')
    # parser.add_argument('output_file', type=str, help='Output file path to store edited OpenScenario 1.1 data', default=)

    # Parse arguments
    args = parser.parse_args()
    # Access arguments
    input_file = args.input_file
    output_file = "automated_scenario_pipeline/output/" + input_file.split("\\")[-1]

    # Alter the openscenario 1.1 to prepare for the conversion using scenariogeneration package
    parse_openscenario(input_file, output_file)

    # Convert the openscenario 1.1 to openscenario 1.0 using the scenariogeneration package
    convert_openscenarios(output_file, version=0)


if __name__ == "__main__":
    main()