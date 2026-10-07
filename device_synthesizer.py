from catalog import SOURCE, DEVICE_TYPES, CLUSTERS
from schema import PropertySpec
from itertools import product
import random

def canonical_id(value):
    return f"0x{int(str(value), 16 if str(value).lower().startswith('0x') else 10):04X}"

def get_choices(device_type=None):
    if device_type is None:
        return {name: get_choices(name) for name in DEVICE_TYPES}
    return [
        {"cluster_id": identifier, "name": requirement["name"], "conformance": requirement["conformance"]}
        for identifier, requirement in DEVICE_TYPES[device_type]["clusters"].items()
        if (rule := _conformance(requirement["conformance"], set(), lambda _: None)) is None
        or rule["kind"] in {"mandatoryConform", "optionalConform"}
    ]

def get_details(device_type, cluster_ids):
    device = DEVICE_TYPES[device_type]
    cluster_ids = [canonical_id(identifier) for identifier in cluster_ids]
    return {
        "device_type": device_type,
        "clusters": {
            identifier: CLUSTERS[identifier] | {"requirement": device["clusters"][identifier]}
            for identifier in cluster_ids
        },
        "provenance": SOURCE | {"device_type_id": device["device_type_id"], "clusters": cluster_ids},
    }

def _property(name, definition, constraints, resolve):
    value = {key: definition[key] for key in
             ("value_type", "minimum", "maximum", "unit", "initial_value", "enum_values") if key in definition}
    initial = resolve(definition.get("default"))
    if value["value_type"] in {"integer", "number"} and initial is not None:
        value["initial_value"] = initial
    low, high = value.get("minimum"), value.get("maximum")
    alternatives = [resolve(rule[1]) for rule in definition.get("constraints", []) if rule[0] == "allowed"]
    for index, rules in enumerate((definition.get("constraints", []), constraints)):
        for kind, *limits in rules:
            if index == 0 and kind == "allowed":
                continue
            minimum, maximum = resolve(limits[0]), resolve(limits[-1])
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
        if value["initial_value"] not in values:
            value["initial_value"] = values[0]
    elif value["value_type"] in {"integer", "number"}:
        initial = value["initial_value"]
        initial = max(low, initial) if low is not None else initial
        initial = min(high, initial) if high is not None else initial
        value["initial_value"] = int(initial) if value["value_type"] == "integer" else initial
    return PropertySpec(property_name=name, **value)

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
    blocked = {"disallowConform", "deprecateConform", "provisionalConform"}
    if extra and extra["kind"] in blocked:
        return extra
    if base is None or base["kind"] in blocked:
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

def _select_features(detail, rng, resolve):
    requirement = detail.get("requirement", {})
    definitions = {name: {"conformance": rules} for name, rules in detail.get("feature_conformance", {}).items()}
    overrides = requirement.get("feature_conformance", {})
    required = set(requirement.get("required_features", []))
    candidates = [name for name in definitions if name not in required]
    profiles = []
    for flags in product((False, True), repeat=len(candidates)):
        selected = required | {name for name, flag in zip(candidates, flags) if flag}
        present = selected | {detail["features"][name] for name in selected}
        rules = {name: _member_rule(definition, overrides.get(name, []), present, resolve)
                 for name, definition in definitions.items()}
        if any((name not in selected and rule and rule["kind"] == "mandatoryConform") or
               (name in selected and (rule is None or rule["kind"] not in {"mandatoryConform", "optionalConform"}))
               for name, rule in rules.items()):
            continue
        if all(low <= len(selected & names) <= high for names, low, high in _choice_groups(rules)):
            profiles.append((selected, rules))
    selected, rules = rng.choice(profiles)
    required |= {name for name, rule in rules.items() if rule and rule["kind"] == "mandatoryConform"}
    return selected, required

def _select_members(definitions, overrides, present, resolve, rng):
    priority = {name: rng.random() for name in definitions}
    selected = set(definitions)
    for _ in range(len(definitions) + 1):
        rules = {name: _member_rule(definition, overrides.get(name, []), present | selected, resolve)
                 for name, definition in definitions.items()}
        allowed = {name for name, rule in rules.items() if rule and rule["kind"] in {"mandatoryConform", "optionalConform"}}
        mandatory = {name for name in allowed if rules[name]["kind"] == "mandatoryConform"}
        result = mandatory | {name for name in allowed if priority[name] < 0.5}
        for names, low, high in _choice_groups(rules):
            ordered = sorted(names, key=priority.get)
            result |= set(sorted(names - result, key=priority.get)[:max(0, low - len(result & names))])
            if len(result & names) > high:
                removable = [name for name in reversed(ordered) if name in result and name not in mandatory]
                result -= set(removable[:len(result & names) - high])
        if result == selected:
            return result, rules
        selected = result
    raise ValueError("Inconsistent member conformance")

def device_api(matter: dict, initial_state=None, rng=None):
    properties, actions, features, required_features = {}, {}, {}, {}
    initial_state = initial_state or {}
    rng = rng or random
    details = {}
    for identifier, detail in matter["clusters"].items():
        rule = _conformance(detail.get("requirement", {}).get("conformance", []), set(initial_state), initial_state.get)
        if rule is None or rule["kind"] in {"mandatoryConform", "optionalConform"}:
            details[identifier] = detail
    for identifier, requirement in DEVICE_TYPES.get(matter.get("device_type"), {}).get("clusters", {}).items():
        rule = _conformance(requirement["conformance"], set(initial_state), initial_state.get)
        if rule and rule["kind"] == "mandatoryConform" and identifier not in details:
            details[identifier] = CLUSTERS[identifier] | {"requirement": requirement}
    for identifier, detail in details.items():
        attributes = detail["properties"]
        requirement = detail.get("requirement", {})
        constraints = requirement.get("constraints", {})
        state = dict(initial_state)

        def resolve(value):
            if isinstance(value, (int, float)):
                return value
            if value in state:
                return state[value]
            if value in attributes:
                allowed = next((rule[1] for rule in constraints.get(value, []) if rule[0] == "allowed"),
                               attributes[value].get("default", attributes[value]["initial_value"]))
                if allowed is None:
                    allowed = attributes[value]["initial_value"]
                return resolve(allowed)
            return None

        selected_features, mandatory_features = _select_features(detail, rng, resolve)
        features[identifier] = {name: label for name, label in detail["features"].items() if name in selected_features}
        required_features[identifier] = [name for name in detail["features"] if name in mandatory_features]
        present = selected_features | set(features[identifier].values())
        selected_properties, property_rules = _select_members(attributes, requirement.get("property_conformance", {}),
                                                               present, resolve, rng)
        selected_commands, _ = _select_members(detail["commands"], requirement.get("command_conformance", {}),
                                               present | selected_properties, resolve, rng)
        command_fields = {}
        for name, command in detail["commands"].items():
            if name not in selected_commands:
                continue
            fields = {field["name"]: field for field in command["arguments"]}
            selected, rules = _select_members(fields, {}, present | selected_properties | selected_commands, resolve, rng)
            command_fields[name] = ({key: field for key, field in fields.items() if key in selected}, rules)
        for fields, _ in command_fields.values():
            for field in fields.values():
                for kind, *limits in field.get("constraints", []):
                    if kind == "between" and isinstance(limits[0], (int, float)) and limits[-1] in attributes:
                        capacity = limits[-1]
                        if not attributes[capacity].get("writable") and capacity not in initial_state and resolve(capacity) < limits[0]:
                            state[capacity] = limits[0]
        pending = list(selected_properties)
        for fields, _ in command_fields.values():
            for field in fields.values():
                for rule in field.get("constraints", []):
                    pending.extend(dependency for dependency in rule[1:] if dependency in attributes)
        while pending:
            name = pending.pop()
            active = property_rules[name]
            if not active or active["kind"] not in {"mandatoryConform", "optionalConform"}:
                continue
            selected_properties.add(name)
            for rule in [*attributes[name].get("constraints", []), *constraints.get(name, [])]:
                for dependency in rule[1:]:
                    if dependency in attributes and dependency not in selected_properties:
                        active = property_rules[dependency]
                        if active and active["kind"] in {"mandatoryConform", "optionalConform"}:
                            selected_properties.add(dependency)
                            pending.append(dependency)
        for name, definition in attributes.items():
            if name not in selected_properties:
                continue
            if name in state:
                definition = definition | {"initial_value": state[name], "default": state[name]}
            prop = _property(name, definition, constraints.get(name, []), resolve)
            if prop is None:
                if property_rules[name]["kind"] == "mandatoryConform":
                    raise ValueError(f"No valid domain for mandatory property: {name}")
                continue
            properties[prop.property_name] = prop.model_dump(exclude_none=True)
            if "enum_labels" in definition:
                properties[prop.property_name]["enum_labels"] = definition["enum_labels"]
            if definition.get("writable"):
                actions[f"Write{name}"] = {
                    "description": f"Write {prop.property_name}",
                    "arguments": [prop.model_dump()], "required": [prop.property_name],
                    "effects": [{"operation": "set", "target_property": prop.property_name,
                                 "argument_name": prop.property_name}],
                }
        for name, command in detail["commands"].items():
            if name not in selected_commands:
                continue
            fields, argument_rules = command_fields[name]
            arguments = {key: _property(key, field, [], resolve) for key, field in fields.items()}
            required = [key for key in fields if argument_rules[key]["kind"] == "mandatoryConform"]
            if any(arguments[key] is None for key in required):
                raise ValueError(f"No valid domain for mandatory argument: {name}")
            actions[name] = {"description": f"Invoke {name}", "required": required,
                            "arguments": [prop.model_dump() for prop in arguments.values() if prop is not None]}
    for name, action in actions.items():
        action["action_name"] = name
    return {"properties": properties, "actions": actions, "features": features, "required_features": required_features}
