from catalog import DEVICE_TYPES, CLUSTERS, STANDARD_CATALOG, PROFILES, PROFILE_FEATURES
from schema import (DeviceDraft, MatterDeviceSpec, MatterDevice, MatterEndpoint, MatterCluster,
                    W3CDevice, W3CThingDescription, SmartThingsDevice, SmartThingsProfile,
                    SmartThingsCapability, SmartThingsComponent)
from urllib.parse import quote
from uuid import NAMESPACE_URL, uuid5
from itertools import product
import random
import re
import json

_ALLOWED = {"mandatoryConform", "optionalConform"}
_BLOCKED = {"disallowConform", "deprecateConform", "provisionalConform"}

def canonical_id(value):
    return f"0x{int(str(value), 16 if str(value).lower().startswith('0x') else 10):04X}"

def _standard_index():
    identifiers, names = {}, {}
    for node in STANDARD_CATALOG["clusters"].values():
        entries = [node["attributes"]] + [child["attributes"] for group in node["children"]
                   if group["tag"] == "clusterIds" for child in group["children"]]
        for entry in entries:
            if entry.get("id"):
                identifiers[canonical_id(entry["id"])] = node
            if entry.get("name"):
                names[entry["name"].removesuffix(" Cluster")] = node
    return identifiers, names

_STANDARD_CLUSTERS, _STANDARD_NAMES = _standard_index()
_STANDARD_TYPES = {canonical_id(node["attributes"]["id"]): node["attributes"]
                   for node in STANDARD_CATALOG["device_types"].values() if node["attributes"].get("id")}

def _merge_standard(base, node):
    children = {(child["tag"], child["attributes"].get("name")): child for child in base.get("children", [])}
    for child in node["children"]:
        key = (child["tag"], child["attributes"].get("name"))
        children[key] = _merge_standard(children.get(key, {}), child)
    return node | {"attributes": base.get("attributes", {}) | node["attributes"], "children": list(children.values())}

def _standard_members(node, section):
    classification = _attributes(node, "classification")
    members = _standard_members(_STANDARD_NAMES[classification["baseCluster"].removesuffix(" Cluster")], section) if classification.get("baseCluster") else {}
    for group in node["children"]:
        if group["tag"] == section:
            for child in group["children"]:
                name = child["attributes"]["name"]
                members[name] = _merge_standard(members.get(name, {}), child)
    return members

def _standard_fields(commands, name):
    fields = {child["attributes"]["name"]: child for child in commands[name]["children"] if child["tag"] == "field"}
    return _standard_fields(commands, name.removesuffix("WithOnOff")) if not fields and name.endswith("WithOnOff") else fields

def _attributes(node, tag):
    return next((child["attributes"] for child in node["children"] if child["tag"] == tag), {})

def _rule(node):
    return {"kind": node["tag"], **node["attributes"],
            **({"terms": [_rule(child) for child in node["children"]]} if node["children"] else {})}

def _definition(node, types, scalar=None):
    metadata = node["attributes"]
    data_type = metadata.get("type", "unspecified")
    value = dict(scalar or {}) | {"name": metadata["name"], "data_type": data_type,
                                "nullable": _attributes(node, "quality").get("nullable") == "true"}
    if "conformance" not in value:
        value["conformance"] = [_rule(child) for child in node["children"] if child["tag"].endswith("Conform")]
    datatype = types.get(data_type.removeprefix("ref_").removesuffix(" Type."))
    datatype = next((child for child in node["children"] if child["tag"] in {"enum", "bitmap"}), datatype)
    if data_type == "ref_CharacteristicEnum":
        datatype = _standard_members(_STANDARD_CLUSTERS["0x0506"], "dataTypes")["CharacteristicEnum"]
    if data_type == "list":
        entry = next(child for child in node["children"] if child["tag"] == "entry")
        value |= {"value_type": "array", "items": _definition(entry | {"attributes": entry["attributes"] | {"name": "item"}}, types)}
    elif datatype and datatype["tag"] == "struct":
        value |= {"value_type": "struct", "fields": [_definition(child, types) | {"field_id": int(child["attributes"]["id"], 0)}
                  for child in datatype["children"] if child["tag"] == "field"]}
    elif data_type == "MessageID":
        value |= {"value_type": "string", "min_length": 16, "max_length": 16}
    elif datatype and datatype["tag"] == "enum":
        labels = {number: child["attributes"]["name"] for child in datatype["children"] if child["tag"] == "item"
                  for number in ([int(child["attributes"]["value"], 0)] if "value" in child["attributes"] else
                      range(int(child["attributes"]["from"], 0), int(child["attributes"]["to"], 0) + 1))}
        value.setdefault("enum_values", list(labels))
        value |= {"value_type": "integer", "enum_labels": labels}
    elif "value_type" not in value:
        if datatype and datatype["tag"] == "bitmap":
            value |= {"value_type": "integer", "minimum": 0,
                "maximum": sum(1 << int(child["attributes"]["bit"])
                    for child in datatype["children"] if child["tag"] == "bitfield")}
        elif data_type in {"string", "octstr", "bool", "single", "double"}:
            value["value_type"] = {"bool": "boolean", "single": "number", "double": "number"}.get(data_type, "string")
        else:
            aliases = {"temperature": "int16", "SignedTemperature": "int16", "UnsignedTemperature": "uint16",
                       "TemperatureDifference": "int16", "percent": "uint8", "percent100ths": "uint16",
                       "epoch-s": "uint32", "epoch-us": "uint64", "elapsed-s": "uint32", "utc": "uint32",
                       "energy-mWh": "int64", "amperage-mA": "int64", "power-mW": "int64",
                       "endpoint-no": "uint16", "vendor-id": "uint16", "devtype-id": "uint32", "node-id": "uint64", "tag": "uint8"}
            primitive = aliases.get(data_type, data_type)
            if match := re.fullmatch(r"(u?int|enum|map)(\d+)", primitive):
                bits = int(match[2])
                signed = primitive.startswith("int")
                value |= {"value_type": "integer", "minimum": -(1 << (bits - 1)) if signed else 0,
                          "maximum": (1 << (bits - int(signed))) - 1}
            else:
                value["value_type"] = "opaque"
    for child in node["children"]:
        constraint = child["attributes"]
        if child["tag"] != "constraint":
            continue
        kind = constraint.get("type")
        if kind in {"minLength", "maxLength", "minCount", "maxCount"} and constraint.get("value", "").isdigit():
            value["min_length" if kind.startswith("min") else "max_length"] = int(constraint["value"])
        if not scalar and kind in {"min", "max", "between"} and value["value_type"] in {"integer", "number"}:
            limits = [constraint["from"], constraint["to"]] if kind == "between" else [constraint["value"]]
            if all(re.fullmatch(r"-?\d+|0x[0-9a-fA-F]+", item) for item in limits):
                value.setdefault("constraints", []).append([kind, *[int(item, 16 if item.startswith("0x") else 10) for item in limits]])
    return value

def _cluster_detail(identifier):
    detail = CLUSTERS[identifier]
    source = _STANDARD_CLUSTERS[identifier]
    types = _standard_members(source, "dataTypes")
    properties = {}
    for name, node in _standard_members(source, "attributes").items():
        properties[name] = _definition(node, types, detail["properties"].get(name)) | {
            "attribute_id": int(node["attributes"]["id"], 0), "writable": _attributes(node, "access").get("write") == "true"}
    commands = {}
    metadata = _standard_members(source, "commands")
    for name, node in metadata.items():
        if node["attributes"].get("direction") != "commandToServer":
            continue
        scalar = detail["commands"].get(name, {})
        arguments = {field["name"]: field for field in scalar.get("arguments", [])}
        commands[name] = scalar | {"command_id": int(node["attributes"]["id"], 0), "timed": _attributes(node, "access").get("timed") == "true",
            "conformance": scalar.get("conformance", [_rule(child) for child in node["children"] if child["tag"].endswith("Conform")]),
            "arguments": [_definition(field, types, arguments.get(key)) | {"field_id": int(field["attributes"]["id"], 0)}
                          for key, field in _standard_fields(metadata, name).items()]}
    features = _standard_members(source, "features")
    return detail | {"properties": properties, "commands": commands,
        "features": {node["attributes"]["code"]: name for name, node in features.items()},
        "feature_conformance": {node["attributes"]["code"]: [_rule(child) for child in node["children"]
            if child["tag"].endswith("Conform")] for node in features.values()}}

def get_profiles():
    return json.dumps(PROFILES, ensure_ascii=False)

def complete_profile_device(draft: DeviceDraft, index: int) -> MatterDevice:
    selection = MatterDeviceSpec.model_validate(PROFILES[draft.profile_id])
    for endpoint in selection.endpoints:
        limits = PROFILE_FEATURES.get(endpoint.device_type, {})
        endpoint.allowed_features = {identifier: limits.get(identifier, requirement.get("required_features", []))
            for identifier, requirement in DEVICE_TYPES[endpoint.device_type]["clusters"].items()} | endpoint.allowed_features
    device = complete_matter_device(draft, selection, index)
    device.profile_id = draft.profile_id
    _apply_options(device, draft.options)
    return device

def json_schema(field):
    schema = {key: field[key] for key in ("minimum", "maximum", "unit") if key in field}
    kind = field["property_type"]
    if kind != "opaque":
        schema["type"] = kind
    for source, target in (("enum_values", "enum"), ("enum_labels", "x-enumLabels"),
                           ("min_length", "minItems" if kind == "array" else "minLength"),
                           ("max_length", "maxItems" if kind == "array" else "maxLength")):
        if source in field:
            schema[target] = field[source]
    if kind == "object" and "fields" in field:
        schema |= argument_schema(field["fields"])
    if kind == "array":
        schema["items"] = json_schema(field["items"])
    return {"oneOf": [schema, {"type": "null"}]} if field.get("nullable") and kind != "opaque" else schema

def argument_schema(fields):
    return {"type": "object", "properties": {field["name"]: json_schema(field) for field in fields},
            "required": [field["name"] for field in fields if field.get("required")],
            "additionalProperties": False}

def render_device(device: MatterDevice, protocol: str):
    if protocol == "Matter":
        return device
    identity = {key: getattr(device, key) for key in ("device_id", "device_name", "room_id", "profile_id")}
    return {"W3C": _w3c_device, "SmartThings": _smartthings_device}[protocol](device, identity)


def _name(name):
    words = re.findall(r"[A-Za-z0-9]+", name)
    return words[0][0].lower() + words[0][1:] + "".join(word.capitalize() for word in words[1:])


def _unique_name(name, interactions):
    name = _name(name)
    candidate, index = name, 2
    while candidate in interactions:
        candidate = f"{name}{index}"
        index += 1
    return candidate


def _w3c_device(device, identity):
    properties, actions = {}, {}
    base = f"https://devices.example.test/{quote(device.device_id, safe='')}"
    for endpoint in device.endpoints:
        for cluster in endpoint.clusters:
            for attribute in cluster.attributes:
                name = _unique_name(attribute["name"], properties)
                properties[name] = json_schema(attribute) | {"title": attribute["name"],
                    "readOnly": not attribute["writable"], "forms": [{"href": f"{base}/properties/{name}",
                        "op": ["readproperty", "writeproperty"] if attribute["writable"] else ["readproperty"]}]}
            for command in cluster.commands:
                name = _unique_name(command["name"], actions)
                actions[name] = {"title": command["name"], "input": argument_schema(command["fields"]),
                    "forms": [{"href": f"{base}/actions/{name}", "op": ["invokeaction"]}]}
    return W3CDevice(**identity, td=W3CThingDescription(
        id=f"urn:uuid:{uuid5(NAMESPACE_URL, base)}", title=device.device_name,
        securityDefinitions={"nosec_sc": {"scheme": "nosec"}}, security=["nosec_sc"],
        properties=properties, actions=actions))


def _smartthings_device(device, identity):
    components, capabilities = [], {}
    for index, endpoint in enumerate(device.endpoints, 1):
        refs = []
        for cluster in endpoint.clusters:
            if not cluster.attributes and not cluster.commands:
                continue
            attributes, commands = {}, {}
            for command in cluster.commands:
                name = _name(command["name"])
                commands[name] = {"name": name, "arguments": [{"name": field["name"],
                    "optional": not field.get("required"), "schema": json_schema(field)} for field in command["fields"]]}
            for attribute in cluster.attributes:
                name = _name(attribute["name"])
                attributes[name] = {"schema": {"type": "object", "properties": {"value": json_schema(attribute)},
                    "required": ["value"], "additionalProperties": False}}
                if attribute["writable"]:
                    setter = "write" + attribute["name"]
                    attributes[name]["setter"] = setter
                    commands[setter] = {"name": setter, "arguments": [{"name": "value", "schema": json_schema(attribute)}]}
            signature = json.dumps({"attributes": attributes, "commands": commands}, sort_keys=True)
            label = {6: "Power", 8: "Brightness", 98: "Presets", 257: "Lock", 258: "Covering",
                     513: "Temperature", 514: "Fan", 768: "Color", 1286: "Playback",
                     1290: "Content"}.get(cluster.cluster_id, cluster.name)
            identifier = f"custom.{_name(label)}{uuid5(NAMESPACE_URL, signature).hex[:12]}"
            capabilities[identifier] = SmartThingsCapability(id=identifier, name=label, attributes=attributes, commands=commands)
            refs.append({"id": identifier, "version": 1})
        components.append(SmartThingsComponent(id="main" if index == 1 else f"component{index}",
            label=device.device_name if index == 1 else f"Controls {index}", capabilities=refs))
    return SmartThingsDevice(**identity, profile=SmartThingsProfile(name=device.device_name, components=components),
                            capabilities=list(capabilities.values()))


def device_description(device):
    if isinstance(device, W3CDevice):
        return _document(device.td.model_dump(by_alias=True, exclude_none=True))
    if isinstance(device, SmartThingsDevice):
        documents = [("SmartThings Device Profile", device.profile)] + [
            ("SmartThings Capability Definition", cap) for cap in device.capabilities]
        return "\n\n".join(f"{title}\n{_document(spec.model_dump(by_alias=True, exclude_none=True))}"
                             for title, spec in documents)
    return "Matter node data model\n" + _document(device.model_dump(
        include={"node_id", "endpoints"}, exclude_none=True))


def _document(value):
    """Omit only default metadata; retain API schemas and native identifiers."""
    def compact(value):
        if isinstance(value, dict):
            return {key: compact(item) for key, item in value.items()
                    if not (key in {"nullable", "timed", "writeOnly"} and item is False)
                    and not (key in {"categories", "required"} and item == [])}
        return list(map(compact, value)) if isinstance(value, list) else value
    return json.dumps(compact(value), ensure_ascii=False, separators=(",", ":"))

def _apply_options(device, options):
    if not options:
        return
    content = [(name if name.startswith(("https://", "http://")) else
                f"https://media.example.test/{device.device_id}/{index}", name)
               for index, name in enumerate(options)]
    custom_field = {
        "robot_vacuum": (0x0150, "NewAreas"), "washer": (0x0051, "NewMode"),
        "dishwasher": (0x0059, "NewMode"), "dimmable_light": (0x0062, "SceneID"),
        "temperature_light": (0x0062, "SceneID"), "color_light": (0x0062, "SceneID"),
    }.get(device.profile_id)
    for endpoint in device.endpoints:
        for cluster in endpoint.clusters:
            for command in cluster.commands:
                for field in command["fields"]:
                    if cluster.cluster_id == 0x050A and field["name"] == "ContentURL":
                        field.update(enum_values=[url for url, _ in content], enum_labels=dict(content))
                    elif (cluster.cluster_id, field["name"]) == custom_field:
                        domain = field["items"] if field["name"] == "NewAreas" else field
                        domain.update(enum_values=list(range(len(options))),
                                      enum_labels={str(index): name for index, name in enumerate(options)})

def get_catalog(device_type=None):
    lines = []
    for name in ([device_type] if device_type else DEVICE_TYPES):
        lines.append(f"device_type: {name}")
        for identifier, requirement in DEVICE_TYPES[name]["clusters"].items():
            rule = _conformance(requirement["conformance"], set(), lambda _: None)
            if rule and rule["kind"] not in _ALLOWED:
                continue
            cluster = _catalog_cluster(identifier, requirement)
            lines.append(f"  {identifier} {cluster['name']} [{cluster['conformance']}]")
            if cluster["features"]:
                features = ", ".join(f"{code}={feature['name']} ({'required' if feature['required'] else 'optional'})"
                                     for code, feature in cluster["features"].items())
                lines.append(f"    features: {features}")
            for command, definition in cluster["commands"].items():
                arguments = ", ".join(f"{key}: {value}" for key, value in definition["arguments"].items())
                conformance = definition.get("conformance", "required" if definition["required"] else "optional")
                lines.append(f"    {command}({arguments}) [{conformance}]")
            if cluster["writable_properties"]:
                properties = ", ".join(f"{key}: {value}" for key, value in cluster["writable_properties"].items())
                lines.append(f"    writable_properties: {properties}")
        lines.append("")
    return "\n".join(lines).rstrip()

def _catalog_text(rule):
    kind, terms = rule["kind"], rule.get("terms", [])
    if "name" in rule:
        return rule["name"]
    if "value" in rule:
        return str(rule["value"])
    if kind == "notTerm":
        return f"not ({_catalog_text(terms[0])})"
    if kind in {"andTerm", "orTerm", "greaterTerm", "otherwiseConform"}:
        separator = {"andTerm": " and ", "orTerm": " or ", "greaterTerm": " > ", "otherwiseConform": " otherwise "}[kind]
        return "(" + separator.join(map(_catalog_text, terms)) + ")"
    label = {"mandatoryConform": "required", "optionalConform": "optional",
             "disallowConform": "disallowed", "deprecateConform": "deprecated", "provisionalConform": "provisional"}[kind]
    if terms:
        label += " if " + " and ".join(map(_catalog_text, terms))
    if "choice" in rule:
        label += f" (choice {rule['choice']})"
    return label

def _catalog_member(definition, override, profiles, resolve):
    rules = [_member_rule(definition, override, present, resolve) for present in profiles]
    allowed = [rule for rule in rules if rule and rule["kind"] in _ALLOWED]
    if not allowed:
        return None
    conformance = " / ".join(dict.fromkeys(map(_catalog_text, allowed)))
    return {
        **{key: definition[key] for key in ("value_type", "unit") if key in definition},
        "required": len(allowed) == len(rules) and all(rule["kind"] == "mandatoryConform" for rule in allowed),
        **({"conformance": conformance} if conformance not in {"required", "optional"} else {}),
    }

def _catalog_cluster(identifier, requirement):
    detail = _cluster_detail(identifier) | {"requirement": requirement}
    resolve = lambda name: detail["properties"].get(name, {}).get("default")
    features = _feature_profiles(detail, resolve)
    profiles = [selected | {detail["features"][name] for name in selected}
                | set(detail["properties"]) | set(detail["commands"]) for selected in features]
    commands = {}
    for name, command in detail["commands"].items():
        summary = _catalog_member(command, requirement.get("command_conformance", {}).get(name, []), profiles, resolve)
        if summary is not None:
            command_profiles = [present for present in profiles
                if (rule := _member_rule(command, requirement.get("command_conformance", {}).get(name, []), present, resolve))
                and rule["kind"] in _ALLOWED]
            commands[name] = summary | {"arguments": {
                field["name"]: field["value_type"] for field in command["arguments"]
                if _catalog_member(field, [], command_profiles, resolve) is not None}}
    rule = requirement["conformance"][0]
    return {
        "cluster_id": identifier, "name": detail["name"], "required": rule["kind"] == "mandatoryConform",
        "conformance": " / ".join(map(_catalog_text, requirement["conformance"])),
        **({"condition": " and ".join(map(_catalog_text, rule["terms"]))} if rule.get("terms") else {}),
        "features": {name: {"name": label, "required": all(name in selected for selected in features)}
                     for name, label in detail["features"].items() if any(name in selected for selected in features)},
        "commands": commands,
        "writable_properties": {name: prop["value_type"] for name, prop in detail["properties"].items()
            if prop.get("writable") and _catalog_member(prop,
                requirement.get("property_conformance", {}).get(name, []), profiles, resolve) is not None},
    }

def get_clusters(device_type, cluster_ids, commands=None, properties=None, allowed_features=None):
    device = DEVICE_TYPES[device_type]
    cluster_ids = [canonical_id(identifier) for identifier in cluster_ids]
    return {
        "device_type": device_type,
        "clusters": {
            identifier: _cluster_detail(identifier) | {"requirement": device["clusters"][identifier],
                "requested_commands": (commands or {}).get(identifier, []),
                "requested_properties": (properties or {}).get(identifier, [])}
                | {"profile": allowed_features is not None}
                | ({"allowed_features": allowed_features[identifier]} if allowed_features and identifier in allowed_features else {})
            for identifier in cluster_ids
        },
        "allowed_features": allowed_features,
    }

def _property(name, definition, constraints, resolve, present=frozenset()):
    value = {key: definition[key] for key in
             ("value_type", "minimum", "maximum", "unit", "enum_values", "enum_labels", "min_length", "max_length", "nullable") if key in definition}
    low, high = value.get("minimum"), value.get("maximum")
    alternatives = [resolve(rule[1]) for rule in definition.get("constraints", []) if rule[0] == "allowed"]
    for index, rules in enumerate((definition.get("constraints", []), constraints)):
        for kind, *limits in rules:
            if index == 0 and kind == "allowed":
                continue
            minimum, maximum = resolve(limits[0], "minimum"), resolve(limits[-1], "maximum")
            if kind in {"between", "min", "allowed"} and minimum is not None:
                low = max(low, minimum) if low is not None else minimum
            if kind in {"between", "max", "allowed"} and maximum is not None:
                high = min(high, maximum) if high is not None else maximum
        if index == 0 and alternatives:
            values = value["enum_values"] if "enum_values" in value else list(range(int(low), int(high) + 1))
            value["enum_values"] = sorted(set(values + alternatives))
            low, high = min(value["enum_values"]), max(value["enum_values"])
    if low is not None and high is not None and low > high:
        return None
    value |= {"minimum": low, "maximum": high}
    if "enum_values" in value:
        values = [item for item in value["enum_values"]
                  if (low is None or item >= low) and (high is None or item <= high)]
        if not values:
            return None
        value["enum_values"] = values
    if "enum_labels" in value:
        labels = {int(str(key), 16 if str(key).startswith("0x") else 10): label for key, label in value["enum_labels"].items()}
        value["enum_labels"] = {str(key): label for key, label in labels.items() if key in value["enum_values"]}
    if "fields" in definition:
        fields = {field["name"]: field for field in definition["fields"]}
        rules = {name: _member_rule(field, [], present, resolve) for name, field in fields.items()}
        members = [_property(name, field, [], resolve, present) | {"required": rules[name]["kind"] == "mandatoryConform"}
                   for name, field in fields.items() if rules[name] and rules[name]["kind"] in _ALLOWED]
        if members:
            value["fields"] = members
    if "items" in definition:
        value["items"] = _property("item", definition["items"], [], resolve, present)
    if value["value_type"] == "struct":
        value["value_type"] = "object"
    if definition.get("data_type") in {"octstr", "MessageID"}:
        value["encoding"] = "hex"
    value |= {"name": name, "property_type": value.pop("value_type"), "data_type": definition["data_type"]}
    if "field_id" in definition:
        value["field_id"] = definition["field_id"]
    return {key: item for key, item in value.items() if item is not None}

def _condition(term, present, resolve):
    kind, terms = term["kind"], term.get("terms", [])
    if kind in {"feature", "attribute", "command"}:
        return term["name"] in present
    if kind == "condition":
        return term["name"] == "Matter"
    if kind == "notTerm":
        return not _condition(terms[0], present, resolve)
    if kind == "orTerm":
        return any(_condition(child, present, resolve) for child in terms)
    if kind == "andTerm":
        return all(_condition(child, present, resolve) for child in terms)
    if kind == "greaterTerm":
        left = resolve(terms[0]["name"])
        right = float(terms[1]["value"])
        return left is not None and left > right
    return False

def _conformance(rules, present, resolve):
    for rule in rules:
        if rule["kind"] == "otherwiseConform":
            result = _conformance(rule["terms"], present, resolve)
            if result is not None:
                return result
        elif all(_condition(term, present, resolve) for term in rule.get("terms", [])):
            return rule
    return None

def _member_rule(definition, override, present, resolve):
    base = _conformance(definition.get("conformance", []), present, resolve)
    extra = _conformance(override, present, resolve)
    if extra and extra["kind"] in _BLOCKED:
        return extra
    if base is None or base["kind"] in _BLOCKED:
        return base
    return extra if extra and extra["kind"] == "mandatoryConform" else base

def _choice_groups(rules):
    groups = {}
    for name, rule in rules.items():
        if rule and rule.get("choice"):
            groups.setdefault(rule["choice"], []).append((name, rule))
    for members in groups.values():
        names = {name for name, _ in members}
        minimum = max(int(rule.get("min", 1)) for _, rule in members)
        maximum = min(int(rule.get("max", len(names) if rule.get("more") == "true" else 1))
                      for _, rule in members)
        yield names, minimum, maximum

def _feature_profiles(detail, resolve):
    requirement = detail.get("requirement", {})
    definitions = {name: {"conformance": rules} for name, rules in detail.get("feature_conformance", {}).items()}
    overrides = requirement.get("feature_conformance", {})
    required = set(requirement.get("required_features", []))
    allowed = set(detail.get("allowed_features", definitions))
    if not required <= allowed:
        return []
    candidates = [name for name in definitions if name not in required and name in allowed]
    profiles = []
    for flags in product((False, True), repeat=len(candidates)):
        selected = required | {name for name, flag in zip(candidates, flags) if flag}
        present = selected | {detail["features"][name] for name in selected}
        rules = {name: _member_rule(definition, overrides.get(name, []), present, resolve)
                 for name, definition in definitions.items()}
        if any((name not in selected and rule and rule["kind"] == "mandatoryConform") or
               (name in selected and (rule is None or rule["kind"] not in _ALLOWED))
               for name, rule in rules.items()):
            continue
        if all(low <= len(selected & names) <= high for names, low, high in _choice_groups(rules)):
            profiles.append(selected)
    return profiles

def _select_features(detail, rng, resolve):
    profiles = []
    for selected in _feature_profiles(detail, resolve):
        present = selected | {detail["features"][name] for name in selected} | set(detail["properties"]) | set(detail["commands"])
        if all((section != "properties" or detail[section].get(name, {}).get("writable"))
               and (rule := _member_rule(detail[section].get(name, {}),
                    detail.get("requirement", {}).get(override, {}).get(name, []), present, resolve))
               and rule["kind"] in _ALLOWED
               for section, override, requested in (("commands", "command_conformance", "requested_commands"),
                                                    ("properties", "property_conformance", "requested_properties"))
               for name in detail.get(requested, [])):
            profiles.append(selected)
    if not profiles:
        raise ValueError(f"No feature profile supports requested controls: {detail['name']}")
    return rng.choice(profiles)

def _select_members(definitions, overrides, present, resolve, rng, required=frozenset()):
    required = set(required)
    priority = {name: rng.random() for name in definitions}
    selected = set(definitions)
    for _ in range(len(definitions) + 1):
        rules = {name: _member_rule(definition, overrides.get(name, []), present | selected, resolve)
                 for name, definition in definitions.items()}
        allowed = {name for name, rule in rules.items() if rule and rule["kind"] in _ALLOWED}
        if required - allowed:
            raise ValueError(f"Unavailable requested controls: {sorted(required - allowed)}")
        mandatory = required | {name for name in allowed if rules[name]["kind"] == "mandatoryConform"}
        result = mandatory | {name for name in allowed if priority[name] < 0.5}
        for names, low, high in _choice_groups(rules):
            ordered = sorted(names, key=priority.get)
            result |= set(sorted(names - result, key=priority.get)[:max(0, low - len(result & names))])
            if len(result & names) > high:
                removable = [name for name in reversed(ordered) if name in result and name not in mandatory]
                result -= set(removable[:len(result & names) - high])
            if len(result & names) > high:
                raise ValueError("Requested controls conflict with member choice")
        if result == selected:
            return result, rules
        selected = result
    raise ValueError("Inconsistent member conformance")

def _complete_cluster(identifier, detail, rng):
    source = _STANDARD_CLUSTERS[identifier]
    properties, actions = [], []
    attributes = detail["properties"]
    requirement = detail.get("requirement", {})
    constraints = requirement.get("constraints", {})
    capacities = {}

    def resolve(value, bound=None):
        if isinstance(value, (int, float)):
            return value
        if value in capacities:
            return capacities[value]
        if value in attributes:
            allowed = next((rule[1] for rule in constraints.get(value, []) if rule[0] == "allowed"),
                           attributes[value].get("default"))
            if allowed is not None:
                return resolve(allowed, bound)
            if bound:
                domain = _property(value, attributes[value], constraints.get(value, []), resolve)
                return domain.get(bound) if domain is not None else None
        return None

    selected_features = _select_features(detail, rng, resolve)
    present = selected_features | {detail["features"][name] for name in selected_features}
    selected_properties, property_rules = _select_members(attributes, requirement.get("property_conformance", {}),
                                                           present, resolve, rng, detail.get("requested_properties", []))
    selected_commands, _ = _select_members(detail["commands"], requirement.get("command_conformance", {}),
                                           present | selected_properties, resolve, rng, detail.get("requested_commands", []))
    command_fields = {}
    for name, command in detail["commands"].items():
        if name not in selected_commands:
            continue
        fields = {field["name"]: field for field in command["arguments"]}
        selected, rules = _select_members(fields, {}, present | selected_properties | selected_commands, resolve, rng)
        if detail.get("profile"):
            selected = {name for name, rule in rules.items() if rule and rule["kind"] in _ALLOWED}
        command_fields[name] = ({key: field for key, field in fields.items() if key in selected}, rules)
    fields = [field for arguments, _ in command_fields.values() for field in arguments.values()]
    for field in fields:
        for kind, *limits in field.get("constraints", []):
            if kind == "between" and isinstance(limits[0], (int, float)) and limits[-1] in attributes:
                capacity = limits[-1]
                value = resolve(capacity, "maximum")
                if not attributes[capacity].get("writable") and value is not None and value < limits[0]:
                    capacities[capacity] = limits[0]
    pending = list(selected_properties) + [
        dependency for field in fields for rule in field.get("constraints", [])
        for dependency in rule[1:] if dependency in attributes]
    while pending:
        name = pending.pop()
        active = property_rules[name]
        if not active or active["kind"] not in _ALLOWED:
            continue
        selected_properties.add(name)
        for rule in [*attributes[name].get("constraints", []), *constraints.get(name, [])]:
            for dependency in rule[1:]:
                if dependency in attributes and dependency not in selected_properties:
                    active = property_rules[dependency]
                    if active and active["kind"] in _ALLOWED:
                        selected_properties.add(dependency)
                        pending.append(dependency)
    for name, definition in attributes.items():
        if name not in selected_properties:
            continue
        prop = _property(name, definition, constraints.get(name, []), resolve, present | selected_properties | selected_commands)
        if prop is None:
            if property_rules[name]["kind"] == "mandatoryConform" or name in detail.get("requested_properties", []):
                raise ValueError(f"No valid domain for mandatory property: {name}")
            continue
        properties.append(prop | {"attribute_id": definition["attribute_id"], "writable": definition["writable"]})
    for name, command in detail["commands"].items():
        if name not in selected_commands:
            continue
        fields, argument_rules = command_fields[name]
        arguments = {key: _property(key, field, [], resolve, present | selected_properties | selected_commands) for key, field in fields.items()}
        required = [key for key in fields if argument_rules[key]["kind"] == "mandatoryConform"]
        if any(arguments[key] is None for key in required):
            raise ValueError(f"No valid domain for mandatory argument: {name}")
        actions.append({"command_id": command["command_id"], "name": name, "timed": command["timed"],
            "fields": [prop | {"required": key in required} for key, prop in arguments.items() if prop is not None]})
    features = _standard_members(source, "features")
    feature_bits = {node["attributes"]["code"]: int(node["attributes"]["bit"]) for node in features.values()}
    return MatterCluster(cluster_id=int(identifier, 16), name=detail["name"], revision=int(source["attributes"]["revision"]),
        feature_map=sum(1 << feature_bits[code] for code in selected_features), attributes=properties, commands=actions)

def device_api(matter: dict, rng=None):
    rng = rng or random
    details = {}
    for identifier, detail in matter["clusters"].items():
        rule = _conformance(detail.get("requirement", {}).get("conformance", []), set(), lambda _: None)
        if rule is None or rule["kind"] in _ALLOWED:
            details[identifier] = detail
        elif detail.get("requested_commands") or detail.get("requested_properties"):
            raise ValueError(f"Requested controls belong to unavailable cluster: {identifier}")
    for identifier, requirement in DEVICE_TYPES.get(matter.get("device_type"), {}).get("clusters", {}).items():
        rule = _conformance(requirement["conformance"], set(), lambda _: None)
        if rule and rule["kind"] == "mandatoryConform" and identifier not in details:
            details[identifier] = _cluster_detail(identifier) | {"requirement": requirement}
            if matter.get("allowed_features") is not None:
                details[identifier]["allowed_features"] = matter["allowed_features"].get(identifier, requirement.get("required_features", []))
    return [_complete_cluster(identifier, detail, rng) for identifier, detail in details.items()]

def complete_matter_device(draft: DeviceDraft, selection: MatterDeviceSpec, index: int) -> MatterDevice:
    endpoints = []
    for endpoint_id, endpoint in enumerate(selection.endpoints, start=1):
        definition = DEVICE_TYPES[endpoint.device_type]
        device_type = _STANDARD_TYPES[definition["device_type_id"]]
        endpoints.append(MatterEndpoint(endpoint_id=endpoint_id, device_types=[{
            "device_type_id": int(device_type["id"], 0), "name": endpoint.device_type, "revision": int(device_type["revision"])}],
            clusters=device_api(get_clusters(endpoint.device_type, endpoint.clusters, endpoint.commands, endpoint.properties, endpoint.allowed_features or None))))
    return MatterDevice(**draft.model_dump(include={"device_id", "device_name", "room_id"}), node_id=index + 1, endpoints=endpoints)
