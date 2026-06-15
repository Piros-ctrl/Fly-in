class MapParser:

    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}
    ALLOWED_HUB_KEYS = {"zone", "max_drones", "color"}
    ALLOWED_CONNECTION_KEYS = {"max_link_capacity"}

    def __init__(self, file_path):
        self.file_path = file_path
        self.argument_dict = {}
        self.zones = []
        self.coords = []          # ← track used coordinates
        self.connections = []
        self.s_and_e = []

    # ------------------------------------------------------------------ #
    #  Public entry point                                                  #
    # ------------------------------------------------------------------ #

    def parse(self):
        self._validate_first_line()
        self._parse_lines()
        self._final_checks()
        self.argument_dict["connections"] = self.connections
        self.argument_dict["start_end"] = self.s_and_e
        return self.argument_dict

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _clean_line(self, raw_line):
        return raw_line.split('#', 1)[0].strip()

    def _validate_first_line(self):
        with open(self.file_path, 'r') as f:
            for raw_line in f:
                line = self._clean_line(raw_line)
                if not line:
                    continue
                if not line.startswith("nb_drones"):
                    raise ValueError("The first line must define nb_drones")
                return
        raise ValueError("The file is empty")

    def _parse_lines(self):
        with open(self.file_path, 'r') as f:
            for line_num, raw_line in enumerate(f, start=1):
                line = self._clean_line(raw_line)
                if not line:
                    continue

                if line.startswith("nb_drones"):
                    self._handle_nb_drones(line, line_num)
                elif line.startswith("start_hub"):
                    self._handle_start_hub(line, line_num)
                elif line.startswith("end_hub"):
                    self._handle_end_hub(line, line_num)
                elif line.startswith("hub"):
                    self._handle_hub(line, line_num)
                elif line.startswith("connection"):
                    self._handle_connection(line, line_num)

    def _final_checks(self):
        if "nb_drones" not in self.argument_dict:
            raise ValueError(
                "Missing required 'nb_drones' definition "
                "(must be the first line)")
        if "start_hub" not in self.argument_dict:
            raise ValueError(
                "Map must contain a start_hub")
        if "end_hub" not in self.argument_dict:
            raise ValueError(
                "Map must contain an end_hub")
        if len(self.s_and_e) != 2:
            raise ValueError(
                "Map must contain exactly one start_hub and one end_hub")

    # ------------------------------------------------------------------ #
    #  Shared zone registration                                            #
    # ------------------------------------------------------------------ #

    def _register_zone(self, name, x, y, line_num):
        """Check for duplicate name and duplicate coords, then register."""
        if name in self.zones:
            raise ValueError(
                f"Line {line_num}: Zone name '{name}' is already defined")
        if (x, y) in self.coords:
            raise ValueError(
                f"Line {line_num}: Zone '{name}' has coordinates "
                f"({x}, {y}) which are already used by another zone")
        self.zones.append(name)
        self.coords.append((x, y))

    # ------------------------------------------------------------------ #
    #  Line handlers                                                       #
    # ------------------------------------------------------------------ #

    def _handle_nb_drones(self, line, line_num):
        parts = line.split(':')
        if len(parts) < 2 or not parts[1].strip():
            raise ValueError(
                f"Line {line_num}: 'nb_drones' is missing a value")
        try:
            drones_nb = int(parts[1].strip())
        except ValueError:
            raise ValueError(
                f"Line {line_num}: 'nb_drones' must be a valid integer")
        if drones_nb <= 0:
            raise ValueError(
                f"Line {line_num}: 'nb_drones' must be a positive number")
        if "nb_drones" in self.argument_dict:
            raise ValueError(
                f"Line {line_num}: 'nb_drones' cannot"
                " be duplicated in the same file")
        self.argument_dict["nb_drones"] = drones_nb

    def _handle_start_hub(self, line, line_num):
        if "start_hub" in self.argument_dict:
            raise ValueError(
                f"Line {line_num}: 'start_hub' cannot"
                " be duplicated in the same file")
        name, x, y, metadata = self._parse_hub_line(line, line_num)

        if metadata.get("zone") == "blocked":
            raise ValueError(
                f"Line {line_num}: start_hub '{name}'"
                " cannot be a blocked zone")

        nb_drones = self.argument_dict.get("nb_drones")
        if nb_drones and metadata.get("max_drones", 1) < nb_drones:
            raise ValueError(
                f"Line {line_num}: start_hub '{name}' capacity "
                f"({metadata['max_drones']}) is less than "
                f"nb_drones ({nb_drones})")

        self._register_zone(name, x, y, line_num)
        self.argument_dict["start_hub"] = name
        self.argument_dict[name] = {"coords": (x, y), "metadata": metadata}
        self.s_and_e.append(name)

    def _handle_end_hub(self, line, line_num):
        if "end_hub" in self.argument_dict:
            raise ValueError(
                f"Line {line_num}: 'end_hub' cannot"
                " be duplicated in the same file")
        name, x, y, metadata = self._parse_hub_line(line, line_num)

        self._register_zone(name, x, y, line_num)
        self.argument_dict["end_hub"] = name
        self.argument_dict[name] = {"coords": (x, y), "metadata": metadata}
        self.s_and_e.append(name)

    def _handle_hub(self, line, line_num):
        name, x, y, metadata = self._parse_hub_line(line, line_num)
        self._register_zone(name, x, y, line_num)
        self.argument_dict[name] = {"coords": (x, y), "metadata": metadata}

    def _handle_connection(self, line, line_num):
        if '[' in line:
            bracket_pos = line.index('[')
            main_part = line[:bracket_pos].strip()
            meta_str = line[bracket_pos:].strip()
        else:
            main_part = line.strip()
            meta_str = None

        parts = main_part.split()
        if len(parts) < 2:
            raise ValueError(
                f"Line {line_num}: Connection definition is missing zone pair")

        zone_pair = parts[1].split('-')
        if len(zone_pair) != 2 or not zone_pair[0] or not zone_pair[1]:
            raise ValueError(
                f"Line {line_num}: Connection must be in format 'zone1-zone2'")

        zone_a, zone_b = zone_pair

        if zone_a == zone_b:
            raise ValueError(
                f"Line {line_num}: Loop connections are not allowed")
        if zone_a not in self.zones:
            raise ValueError(f"Line {line_num}: Connection references "
                             f"undefined zone '{zone_a}'")
        if zone_b not in self.zones:
            raise ValueError(f"Line {line_num}: Connection references "
                             f"undefined zone '{zone_b}'")

        for existing in self.connections:
            ex_a, ex_b = existing["pair"]
            if (
                (zone_a == ex_a and zone_b == ex_b)
                or (zone_a == ex_b and zone_b == ex_a)
            ):
                raise ValueError(
                    f"Line {line_num}: Connection "
                    f"'{zone_a}-{zone_b}' already defined "
                    "(duplicates including reversed pairs are not allowed)"
                )

        metadata = {}
        if meta_str:
            metadata = self._parse_metadata(meta_str, line_num)

        for key in metadata:
            if key not in self.ALLOWED_CONNECTION_KEYS:
                raise ValueError(
                    f"Line {line_num}: Invalid connection metadata key '{key}'"
                )

        if 'max_link_capacity' in metadata:
            try:
                cap = int(metadata['max_link_capacity'])
                if cap <= 0:
                    raise ValueError()
                metadata['max_link_capacity'] = cap
            except ValueError:
                raise ValueError(f"Line {line_num}: 'max_link_capacity'"
                                 " must be a positive integer")

        self.connections.append(
            {"pair": (zone_a, zone_b), "metadata": metadata})

    # ------------------------------------------------------------------ #
    #  Parsing utilities                                                   #
    # ------------------------------------------------------------------ #

    def _parse_hub_line(self, line, line_num):
        if '[' in line:
            bracket_pos = line.index('[')
            main_part = line[:bracket_pos].strip()
            meta_str = line[bracket_pos:].strip()
        else:
            main_part = line.strip()
            meta_str = None

        parts = main_part.split()
        if len(parts) < 4:
            raise ValueError(f"Line {line_num}: Hub definition must "
                             f"have a name and two integer coordinates")

        name = parts[1]

        if '-' in name or ' ' in name:
            raise ValueError(f"Line {line_num}: Zone name '{name}'"
                             " must not contain dashes or spaces")

        try:
            x = int(parts[2])
            y = int(parts[3])
        except ValueError:
            raise ValueError(f"Line {line_num}: Zone '{name}'"
                             " coordinates must be valid integers")

        metadata = {"zone": "normal", "color": None, "max_drones": 1}

        if meta_str:
            parsed = self._parse_metadata(meta_str, line_num)
            for key in parsed:
                if key not in self.ALLOWED_HUB_KEYS:
                    raise ValueError(f"Line {line_num}: "
                                     f"Invalid metadata key '{key}'")
            metadata.update(parsed)

        if metadata['zone'] not in self.VALID_ZONE_TYPES:
            raise ValueError(
                f"Line {line_num}: Invalid zone type "
                f"'{metadata['zone']}' for zone '{name}'. "
                f"Must be one of: {', '.join(self.VALID_ZONE_TYPES)}"
            )

        try:
            max_drones = int(metadata['max_drones'])
            if max_drones <= 0:
                raise ValueError()
            metadata['max_drones'] = max_drones
        except ValueError:
            raise ValueError(f"Line {line_num}: 'max_drones' for zone "
                             f"'{name}' must be a positive integer")

        return name, x, y, metadata

    def _parse_metadata(self, meta_str, line_num):
        meta_str = meta_str.strip()
        if not meta_str.startswith('[') or not meta_str.endswith(']'):
            raise ValueError(f"Line {line_num}: Invalid metadata "
                             f"block syntax: '{meta_str}'")

        inner = meta_str[1:-1].strip()
        if not inner:
            return {}

        metadata = {}
        for token in inner.split():
            if token.count('=') != 1:
                raise ValueError(
                    f"Line {line_num}: Invalid metadata token '{token}'"
                    f", expected key=value format"
                )
            key, _, value = token.partition('=')
            if not key or not value:
                raise ValueError(
                    f"Line {line_num}: Invalid metadata token '{token}'"
                    ", key or value is empty"
                )
            if key in metadata:
                raise ValueError(
                    f"Line {line_num}: Duplicate metadata key '{key}'")
            metadata[key] = value

        return metadata
