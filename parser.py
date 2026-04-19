def parse_file(file):
    argument_dict = {}
    zones = []
    conections = []
    zone_type = ["normal", "blocked", "restricted", "priority"]
    with open(file, 'r') as infos:
        for line in infos:
            if "nb_drones" in line:
                drones_nb = line.strip(' ').split(':')[1]
                if int(drones_nb) <= 0:
                    raise ValueError("drones number can be just positive number")
                if "nb_drones" not in argument_dict:
                    argument_dict["nb_drones"] = int(drones_nb)
                else:
                    raise ValueError("nb_drones can't be duplicated in the same file")
            if "start_hub" in line:
                start_hub = (int(line.split(' ')[2]), int(line.split(' ')[3]))
                # if line.split:
                    # .
                if "start_hub" not in argument_dict:
                    argument_dict["start_hub"] = start_hub
                    zones.append("start")
                else:
                    raise ValueError("start_hub can't be duplicated in the same file")
            if "end_hub" in line:
                end_hub = (int(line.split(' ')[2]), int(line.split(' ')[3]))
                if "end_hub" not in argument_dict:
                    argument_dict["end_hub"] = end_hub
                    zones.append("goal")
                else:
                    raise ValueError("end_hub can't be duplicated in the same file")
            if line.startswith("hub"):
                zone_name = line.split(' ')[1]
                if (" " in zone_name
                    or "_" in zone_name):
                    raise ValueError("Zone names can use any valid characters but dashes and spaces")
                zone_cordination = (int(line.split(' ')[2]), int(line.split(' ')[3]))
                if zone_name not in argument_dict:
                    argument_dict[zone_name] = zone_cordination
                else:
                    raise ValueError(f"{zone_name} can't be duplicated in the same file")
                zones.append(zone_name)
            if "connection" in line:
                half = line.rstrip('\n').split(' ')
                zone = half[1].split('-')
                if (zone[0] in zones
                    and zone[1] in zones):
                    for conection in conections:
                        if zone[0] and zone[1] in conection:
                            raise ValueError("The same connection must not appear more than once")
                    conections.append(zone[0]+"-"+zone[1])
                else:
                    raise ValueError("Connections must link only predefined zones")
                
    argument_dict["conections"] = conections
    return argument_dict