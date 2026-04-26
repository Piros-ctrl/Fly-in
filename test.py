def parse_metadata(meta_str, line_num):
    meta_str = meta_str.strip()
    if not meta_str.startswith('[') or not meta_str.endswith(']'):
        raise ValueError(f"Line {line_num}: Invalid metadata block syntax: '{meta_str}'")
    
    inner = meta_str[1:-1].strip()
    if not inner:
        return {}

    metadata = {}
    for token in inner.split():
        if '=' not in token:
            raise ValueError(f"Line {line_num}: Invalid metadata token '{token}', expected key=value format")
        key, _, value = token.partition('=')
        if not key or not value:
            raise ValueError(f"Line {line_num}: Invalid metadata token '{token}', key or value is empty")
        metadata[key] = value

    return metadata


def parse_hub_line(line, line_num):
    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}

    # Split off metadata block if present
    if '[' in line:
        bracket_pos = line.index('[')
        main_part = line[:bracket_pos].strip()
        meta_str = line[bracket_pos:].strip()
    else:
        main_part = line.strip()
        meta_str = None

    parts = main_part.split()
    # parts[0] is the keyword (hub:, start_hub:, end_hub:), parts[1] is name, parts[2] is x, parts[3] is y
    if len(parts) < 4:
        raise ValueError(f"Line {line_num}: Hub definition must have a name and two integer coordinates")

    name = parts[1]

    # Validate zone name: no dashes or spaces
    if '-' in name or ' ' in name:
        raise ValueError(f"Line {line_num}: Zone name '{name}' must not contain dashes or spaces")

    # Validate coordinates
    try:
        x = int(parts[2])
        y = int(parts[3])
    except ValueError:
        raise ValueError(f"Line {line_num}: Zone '{name}' coordinates must be valid integers")

    # Parse metadata
    metadata = {}
    if meta_str:
        metadata = parse_metadata(meta_str, line_num)

    # Validate zone type if provided
    if 'zone' in metadata:
        if metadata['zone'] not in VALID_ZONE_TYPES:
            raise ValueError(
                f"Line {line_num}: Invalid zone type '{metadata['zone']}' for zone '{name}'. "
                f"Must be one of: {', '.join(VALID_ZONE_TYPES)}"
            )

    # Validate max_drones if provided
    if 'max_drones' in metadata:
        try:
            max_drones = int(metadata['max_drones'])
            if max_drones <= 0:
                raise ValueError()
            metadata['max_drones'] = max_drones
        except ValueError:
            raise ValueError(f"Line {line_num}: 'max_drones' for zone '{name}' must be a positive integer")

    return name, x, y, metadata


def parse_file(file):
    argument_dict = {}
    zones = []
    connections = []

    with open(file, 'r') as infos:
        for line_num, raw_line in enumerate(infos, start=1):
            line = raw_line.strip()

            # --- nb_drones ---
            if line.startswith("nb_drones"):
                parts = line.split(':')
                if len(parts) < 2 or not parts[1].strip():
                    raise ValueError(f"Line {line_num}: 'nb_drones' is missing a value")
                try:
                    drones_nb = int(parts[1].strip())
                except ValueError:
                    raise ValueError(f"Line {line_num}: 'nb_drones' must be a valid integer")
                if drones_nb <= 0:
                    raise ValueError(f"Line {line_num}: 'nb_drones' must be a positive number")
                if "nb_drones" in argument_dict:
                    raise ValueError(f"Line {line_num}: 'nb_drones' cannot be duplicated in the same file")
                argument_dict["nb_drones"] = drones_nb

            # --- start_hub ---
            elif line.startswith("start_hub"):
                if "start_hub" in argument_dict:
                    raise ValueError(f"Line {line_num}: 'start_hub' cannot be duplicated in the same file")
                name, x, y, metadata = parse_hub_line(line, line_num)
                argument_dict["start"] = {"coords": (x, y), "metadata": metadata}
                zones.append(name)

            # --- end_hub ---
            elif line.startswith("end_hub"):
                if "end_hub" in argument_dict:
                    raise ValueError(f"Line {line_num}: 'end_hub' cannot be duplicated in the same file")
                name, x, y, metadata = parse_hub_line(line, line_num)
                argument_dict["goal"] = {"coords": (x, y), "metadata": metadata}
                zones.append(name)

            # --- hub ---
            elif line.startswith("hub"):
                name, x, y, metadata = parse_hub_line(line, line_num)
                if name in zones:
                    raise ValueError(f"Line {line_num}: Zone name '{name}' is duplicated")
                argument_dict[name] = {"coords": (x, y), "metadata": metadata}
                zones.append(name)

            # --- connection ---
            elif line.startswith("connection"):
                # Split off metadata block if present
                if '[' in line:
                    bracket_pos = line.index('[')
                    main_part = line[:bracket_pos].strip()
                    meta_str = line[bracket_pos:].strip()
                else:
                    main_part = line.strip()
                    meta_str = None

                parts = main_part.split()
                if len(parts) < 2:
                    raise ValueError(f"Line {line_num}: Connection definition is missing zone pair")

                zone_pair = parts[1].split('-')
                if len(zone_pair) != 2 or not zone_pair[0] or not zone_pair[1]:
                    raise ValueError(f"Line {line_num}: Connection must be in format 'zone1-zone2'")

                zone_a, zone_b = zone_pair

                # Both zones must be predefined
                if zone_a not in zones:
                    raise ValueError(f"Line {line_num}: Connection references undefined zone '{zone_a}'")
                if zone_b not in zones:
                    raise ValueError(f"Line {line_num}: Connection references undefined zone '{zone_b}'")

                # Check for duplicate connections (a-b and b-a are the same)
                for existing in connections:
                    ex_a, ex_b = existing["pair"]
                    if (zone_a == ex_a and zone_b == ex_b) or (zone_a == ex_b and zone_b == ex_a):
                        raise ValueError(
                            f"Line {line_num}: Connection '{zone_a}-{zone_b}' already defined (duplicates including reversed pairs are not allowed)"
                        )

                # Parse and validate connection metadata
                metadata = {}
                if meta_str:
                    metadata = parse_metadata(meta_str, line_num)

                if 'max_link_capacity' in metadata:
                    try:
                        cap = int(metadata['max_link_capacity'])
                        if cap <= 0:
                            raise ValueError()
                        metadata['max_link_capacity'] = cap
                    except ValueError:
                        raise ValueError(f"Line {line_num}: 'max_link_capacity' must be a positive integer")

                connections.append({"pair": (zone_a, zone_b), "metadata": metadata})

    # Final structural checks
    if "nb_drones" not in argument_dict:
        raise ValueError("Missing required 'nb_drones' definition (must be the first line)")
    if "start" not in argument_dict:
        raise ValueError("Missing required 'start_hub' definition")
    if "goal" not in argument_dict:
        raise ValueError("Missing required 'end_hub' definition")

    argument_dict["connections"] = connections
    return argument_dict


if __name__ == "__main__":
    import json
    result = parse_file("drone_config.txt")
    print(json.dumps(
        {k: v for k, v in result.items()},
        indent=2,
        default=str  # handles tuples
    ))
