"""Matter 1.4 controllable endpoint facts from the pinned official catalog."""

from typing import Literal, TypeAlias

DeviceType: TypeAlias = Literal[
    "Aggregator", "Air Purifier", "Basic Video Player",
    "Casting Video Client", "Casting Video Player", "Color Temperature Light",
    "Contact Sensor", "Content App", "Cook Surface",
    "Cooktop", "Dimmable Light", "Dimmable Plug-In Unit",
    "Dishwasher", "Door Lock", "Energy EVSE",
    "Extended Color Light", "Extractor Hood", "Fan",
    "Laundry Dryer", "Laundry Washer", "Microwave Oven",
    "Mode Select", "Mounted Dimmable Load Control", "Mounted On/Off Control",
    "Network Infrastructure Manager", "Occupancy Sensor", "On/Off Light",
    "On/Off Plug-in Unit", "Pump", "Rain Sensor",
    "Refrigerator", "Robotic Vacuum Cleaner", "Room Air Conditioner",
    "Smoke CO Alarm", "Speaker", "Temperature Controlled Cabinet",
    "Thermostat", "Thread Border Router", "Water Freeze Detector",
    "Water Heater", "Water Leak Detector", "Water Valve",
    "Window Covering",
]

ClusterId: TypeAlias = Literal[
    "0x0006", "0x0008", "0x0025", "0x0048", "0x0049", "0x004A",
    "0x0050", "0x0051", "0x0052", "0x0053", "0x0054", "0x0055",
    "0x0056", "0x0057", "0x0059", "0x005C", "0x005D", "0x005E",
    "0x005F", "0x0060", "0x0061", "0x0071", "0x0072", "0x0080",
    "0x0081", "0x0094", "0x0097", "0x0099", "0x009B", "0x009D",
    "0x009E", "0x0101", "0x0102", "0x0150", "0x0200", "0x0201",
    "0x0202", "0x0204", "0x0300", "0x0406", "0x0451", "0x0452",
    "0x0453", "0x0504", "0x0505", "0x0506", "0x0507", "0x0508",
    "0x0509", "0x050A", "0x050B", "0x050C", "0x050E", "0x050F",
    "0x0510",
]

SOURCE = {
    'standard': 'Matter',
    'version': '1.4',
    'ref': 'v1.4.0.0',
    'commit': '43aa98c2d30ee547c6b587b9de7bbb794f175ece',
    'source_url': 'https://github.com/project-chip/connectedhomeip/tree/43aa98c2d30ee547c6b587b9de7bbb794f175ece/data_model/1.4',
}

DEVICE_TYPES = {
    'Aggregator': {
        'device_type_id': '0x000E',
        'clusters': {
            '0x0025': {'name': 'Actions', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Air Purifier': {
        'device_type_id': '0x002D',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0071': {'name': 'HEPA Filter Monitoring', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0072': {'name': 'Activated Carbon Filter Monitoring', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0202': {'name': 'Fan Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Basic Video Player': {
        'device_type_id': '0x0028',
        'clusters': {
            '0x0006': {'name': 'OnOff', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0097': {'name': 'Messages', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0504': {'name': 'Channel', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0505': {'name': 'Target Navigator', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0506': {'name': 'Media Playback', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0507': {'name': 'Media Input', 'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'attribute', 'name': 'PhysicalInputs'}]}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0508': {'name': 'Low Power', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0509': {'name': 'Keypad Input', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x050B': {'name': 'Audio Output', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x050F': {'name': 'Content Control', 'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'provisionalConform'}, {'kind': 'optionalConform'}]}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Casting Video Client': {
        'device_type_id': '0x0029',
        'clusters': {
            '0x0510': {'name': 'Content App Observer', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Casting Video Player': {
        'device_type_id': '0x0023',
        'clusters': {
            '0x0006': {'name': 'OnOff', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0097': {'name': 'Messages', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0504': {'name': 'Channel', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0505': {'name': 'Target Navigator', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0506': {'name': 'Media Playback', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0507': {'name': 'Media Input', 'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'attribute', 'name': 'PhysicalInputs'}]}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0508': {'name': 'Low Power', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0509': {'name': 'Keypad Input', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x050A': {'name': 'Content Launcher', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x050B': {'name': 'Audio Output', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x050C': {'name': 'Application Launcher', 'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'attribute', 'name': 'ContentAppPlatform'}]}], 'required_features': ['AP'], 'feature_conformance': {'AP': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x050E': {'name': 'Account Login', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x050F': {'name': 'Content Control', 'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'provisionalConform'}, {'kind': 'optionalConform'}]}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Color Temperature Light': {
        'device_type_id': '0x010C',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['LT'], 'feature_conformance': {'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x0008': {'name': 'Level Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['OO', 'LT'], 'feature_conformance': {'OO': [{'kind': 'mandatoryConform'}], 'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {'CurrentLevel': [('between', 1, 254)], 'MinLevel': [('allowed', 1)], 'MaxLevel': [('allowed', 254)]}},
            '0x0300': {'name': 'Color Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['CT'], 'feature_conformance': {'CT': [{'kind': 'mandatoryConform'}]}, 'constraints': {}, 'property_conformance': {'RemainingTime': [{'kind': 'mandatoryConform'}]}},
        },
    },
    'Contact Sensor': {
        'device_type_id': '0x0015',
        'clusters': {
            '0x0080': {'name': 'Boolean State Configuration', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Content App': {
        'device_type_id': '0x0024',
        'clusters': {
            '0x0504': {'name': 'Channel', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0505': {'name': 'Target Navigator', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0506': {'name': 'Media Playback', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0509': {'name': 'Keypad Input', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x050A': {'name': 'Content Launcher', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x050C': {'name': 'Application Launcher', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {'AP': [{'kind': 'disallowConform'}]}, 'constraints': {}},
            '0x050E': {'name': 'Account Login', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Cook Surface': {
        'device_type_id': '0x0077',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'optionalConform'}], 'required_features': ['OFFONLY'], 'feature_conformance': {'OFFONLY': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x0056': {'name': 'Temperature Control', 'conformance': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Cooktop': {
        'device_type_id': '0x0078',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['OFFONLY'], 'feature_conformance': {'OFFONLY': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
        },
    },
    'Dimmable Light': {
        'device_type_id': '0x0101',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['LT'], 'feature_conformance': {'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x0008': {'name': 'Level Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['OO', 'LT'], 'feature_conformance': {'LT': [{'kind': 'mandatoryConform'}], 'OO': [{'kind': 'mandatoryConform'}]}, 'constraints': {'CurrentLevel': [('between', 1, 254)], 'MinLevel': [('allowed', 1)], 'MaxLevel': [('allowed', 254)]}},
        },
    },
    'Dimmable Plug-In Unit': {
        'device_type_id': '0x010B',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['LT'], 'feature_conformance': {'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x0008': {'name': 'Level Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['OO', 'LT'], 'feature_conformance': {'OO': [{'kind': 'mandatoryConform'}], 'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {'CurrentLevel': [('between', 1, 254)], 'MinLevel': [('allowed', 1)], 'MaxLevel': [('allowed', 254)]}},
        },
    },
    'Dishwasher': {
        'device_type_id': '0x0075',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'optionalConform'}], 'required_features': ['DF'], 'feature_conformance': {'DF': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x0056': {'name': 'Temperature Control', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0059': {'name': 'Dishwasher Mode', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]}, 'constraints': {}, 'property_conformance': {'StartUpMode': [{'kind': 'disallowConform'}]}},
            '0x005D': {'name': 'Dishwasher Alarm', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0060': {'name': 'Operational State', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Door Lock': {
        'device_type_id': '0x000A',
        'clusters': {
            '0x0101': {'name': 'Door Lock', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {'USR': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'condition', 'name': 'Matter'}, {'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIN'}, {'kind': 'feature', 'name': 'RID'}, {'kind': 'feature', 'name': 'FPG'}, {'kind': 'feature', 'name': 'FACE'}, {'kind': 'feature', 'name': 'ALIRO'}]}]}]}], 'RID': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'provisionalConform'}, {'kind': 'optionalConform'}]}]}, 'constraints': {}, 'property_conformance': {'AlarmMask': [{'kind': 'optionalConform', 'terms': [{'kind': 'attribute', 'name': 'Alarms'}]}]}},
        },
    },
    'Energy EVSE': {
        'device_type_id': '0x050C',
        'clusters': {
            '0x0099': {'name': 'Energy EVSE', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x009D': {'name': 'Energy EVSE Mode', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Extended Color Light': {
        'device_type_id': '0x010D',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['LT'], 'feature_conformance': {'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x0008': {'name': 'Level Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['OO', 'LT'], 'feature_conformance': {'OO': [{'kind': 'mandatoryConform'}], 'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {'CurrentLevel': [('between', 1, 254)], 'MinLevel': [('allowed', 1)], 'MaxLevel': [('allowed', 254)]}},
            '0x0300': {'name': 'Color Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['XY', 'CT'], 'feature_conformance': {'HS': [{'kind': 'optionalConform'}], 'EHUE': [{'kind': 'optionalConform'}], 'CL': [{'kind': 'optionalConform'}], 'XY': [{'kind': 'mandatoryConform'}], 'CT': [{'kind': 'mandatoryConform'}]}, 'constraints': {}, 'property_conformance': {'RemainingTime': [{'kind': 'mandatoryConform'}]}},
        },
    },
    'Extractor Hood': {
        'device_type_id': '0x007A',
        'clusters': {
            '0x0071': {'name': 'HEPA Filter Monitoring', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0072': {'name': 'Activated Carbon Filter Monitoring', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0202': {'name': 'Fan Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {'RCK': [{'kind': 'disallowConform'}], 'WND': [{'kind': 'disallowConform'}], 'DIR': [{'kind': 'disallowConform'}]}, 'constraints': {}},
        },
    },
    'Fan': {
        'device_type_id': '0x002B',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0202': {'name': 'Fan Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}, 'property_conformance': {'FanModeSequence': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'condition', 'name': 'Matter'}]}]}},
        },
    },
    'Laundry Dryer': {
        'device_type_id': '0x007C',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'optionalConform'}], 'required_features': ['DF'], 'feature_conformance': {'DF': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x004A': {'name': 'Laundry Dryer Controls', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0051': {'name': 'Laundry Washer Mode', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]}, 'constraints': {}, 'property_conformance': {'StartUpMode': [{'kind': 'disallowConform'}]}},
            '0x0056': {'name': 'Temperature Control', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0060': {'name': 'Operational State', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Laundry Washer': {
        'device_type_id': '0x0073',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'optionalConform'}], 'required_features': ['DF'], 'feature_conformance': {'DF': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x0051': {'name': 'Laundry Washer Mode', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]}, 'constraints': {}, 'property_conformance': {'StartUpMode': [{'kind': 'disallowConform'}]}},
            '0x0053': {'name': 'Laundry Washer Controls', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0056': {'name': 'Temperature Control', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0060': {'name': 'Operational State', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Microwave Oven': {
        'device_type_id': '0x0079',
        'clusters': {
            '0x005E': {'name': 'Microwave Oven Mode', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x005F': {'name': 'Microwave Oven Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0060': {'name': 'Operational State', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}, 'property_conformance': {'CountdownTime': [{'kind': 'mandatoryConform'}]}},
            '0x0202': {'name': 'Fan Control', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {'WND': [{'kind': 'disallowConform'}], 'DIR': [{'kind': 'disallowConform'}]}, 'constraints': {}},
        },
    },
    'Mode Select': {
        'device_type_id': '0x0027',
        'clusters': {
            '0x0050': {'name': 'Mode Select', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Mounted Dimmable Load Control': {
        'device_type_id': '0x0110',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['LT'], 'feature_conformance': {'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x0008': {'name': 'Level Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['OO', 'LT'], 'feature_conformance': {'OO': [{'kind': 'mandatoryConform'}], 'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {'CurrentLevel': [('between', 1, 254)], 'MinLevel': [('allowed', 1)], 'MaxLevel': [('allowed', 254)]}},
        },
    },
    'Mounted On/Off Control': {
        'device_type_id': '0x010F',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['LT'], 'feature_conformance': {'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x0008': {'name': 'Level Control', 'conformance': [{'kind': 'optionalConform'}], 'required_features': ['OO', 'LT'], 'feature_conformance': {'OO': [{'kind': 'mandatoryConform'}], 'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {'CurrentLevel': [('between', 1, 254)], 'MinLevel': [('allowed', 1)], 'MaxLevel': [('allowed', 254)]}},
        },
    },
    'Network Infrastructure Manager': {
        'device_type_id': '0x0090',
        'clusters': {
            '0x0451': {'name': 'Wi-Fi Network Management', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0452': {'name': 'Thread Border Router Management', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0453': {'name': 'Thread Network Directory', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Occupancy Sensor': {
        'device_type_id': '0x0107',
        'clusters': {
            '0x0080': {'name': 'Boolean State Configuration', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0406': {'name': 'Occupancy Sensing', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'On/Off Light': {
        'device_type_id': '0x0100',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['LT'], 'feature_conformance': {'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x0008': {'name': 'Level Control', 'conformance': [{'kind': 'optionalConform'}], 'required_features': ['OO', 'LT'], 'feature_conformance': {'OO': [{'kind': 'mandatoryConform'}], 'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {'CurrentLevel': [('between', 1, 254)], 'MinLevel': [('allowed', 1)], 'MaxLevel': [('allowed', 254)]}},
        },
    },
    'On/Off Plug-in Unit': {
        'device_type_id': '0x010A',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['LT'], 'feature_conformance': {'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x0008': {'name': 'Level Control', 'conformance': [{'kind': 'optionalConform'}], 'required_features': ['OO', 'LT'], 'feature_conformance': {'OO': [{'kind': 'mandatoryConform'}], 'LT': [{'kind': 'mandatoryConform'}]}, 'constraints': {'CurrentLevel': [('between', 1, 254)], 'MinLevel': [('allowed', 1)], 'MaxLevel': [('allowed', 254)]}},
        },
    },
    'Pump': {
        'device_type_id': '0x0303',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0008': {'name': 'Level Control', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0200': {'name': 'Pump Configuration and Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Rain Sensor': {
        'device_type_id': '0x0044',
        'clusters': {
            '0x0080': {'name': 'Boolean State Configuration', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Refrigerator': {
        'device_type_id': '0x0070',
        'clusters': {
            '0x0052': {'name': 'Refrigerator And Temperature Controlled Cabinet Mode', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]}, 'constraints': {}, 'property_conformance': {'StartUpMode': [{'kind': 'disallowConform'}]}},
            '0x0057': {'name': 'Refrigerator Alarm', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Robotic Vacuum Cleaner': {
        'device_type_id': '0x0074',
        'clusters': {
            '0x0054': {'name': 'RVC Run Mode', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0055': {'name': 'RVC Clean Mode', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0061': {'name': 'RVC Operational State', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0150': {'name': 'Service Area', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Room Air Conditioner': {
        'device_type_id': '0x0072',
        'clusters': {
            '0x0006': {'name': 'On/Off', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['DF'], 'feature_conformance': {'DF': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
            '0x0201': {'name': 'Thermostat', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0202': {'name': 'Fan Control', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0204': {'name': 'Thermostat User Interface Configuration', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}, 'property_conformance': {'KeypadLockout': [{'kind': 'optionalConform'}]}},
        },
    },
    'Smoke CO Alarm': {
        'device_type_id': '0x0076',
        'clusters': {
            '0x005C': {'name': 'Smoke CO Alarm', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Speaker': {
        'device_type_id': '0x0022',
        'clusters': {
            '0x0006': {'name': 'OnOff', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0008': {'name': 'Level Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Temperature Controlled Cabinet': {
        'device_type_id': '0x0071',
        'clusters': {
            '0x0048': {'name': 'Oven Cavity Operational State', 'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'attribute', 'name': 'Heater'}]}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}, 'command_conformance': {'Pause': [{'kind': 'disallowConform'}], 'Resume': [{'kind': 'disallowConform'}]}},
            '0x0049': {'name': 'Oven Mode', 'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'attribute', 'name': 'Heater'}]}], 'required_features': [], 'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]}, 'constraints': {}, 'property_conformance': {'StartUpMode': [{'kind': 'disallowConform'}]}},
            '0x0052': {'name': 'Refrigerator and Temperature Controlled Cabinet Mode', 'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'attribute', 'name': 'Cooler'}]}], 'required_features': [], 'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]}, 'constraints': {}, 'property_conformance': {'StartUpMode': [{'kind': 'disallowConform'}]}},
            '0x0056': {'name': 'Temperature Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Thermostat': {
        'device_type_id': '0x0301',
        'clusters': {
            '0x009B': {'name': 'Energy Preference', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0201': {'name': 'Thermostat', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {'SCH': [{'kind': 'disallowConform'}]}, 'constraints': {}, 'property_conformance': {'AlarmMask': [{'kind': 'disallowConform'}]}, 'command_conformance': {'GetRelayStatusLog': [{'kind': 'disallowConform'}], 'GetRelayStatusLogResponse': [{'kind': 'disallowConform'}]}},
            '0x0204': {'name': 'Thermostat User Interface Configuration', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Thread Border Router': {
        'device_type_id': '0x0091',
        'clusters': {
            '0x0452': {'name': 'Thread Border Router Management', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0453': {'name': 'Thread Network Directory', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Water Freeze Detector': {
        'device_type_id': '0x0041',
        'clusters': {
            '0x0080': {'name': 'Boolean State Configuration', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Water Heater': {
        'device_type_id': '0x050F',
        'clusters': {
            '0x0094': {'name': 'Water Heater Management', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x009E': {'name': 'Water Heater Mode', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
            '0x0201': {'name': 'Thermostat', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': ['HEAT'], 'feature_conformance': {'HEAT': [{'kind': 'mandatoryConform'}]}, 'constraints': {}},
        },
    },
    'Water Leak Detector': {
        'device_type_id': '0x0043',
        'clusters': {
            '0x0080': {'name': 'Boolean State Configuration', 'conformance': [{'kind': 'optionalConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Water Valve': {
        'device_type_id': '0x0042',
        'clusters': {
            '0x0081': {'name': 'Valve Configuration and Control', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {}, 'constraints': {}},
        },
    },
    'Window Covering': {
        'device_type_id': '0x0202',
        'clusters': {
            '0x0102': {'name': 'Window Covering', 'conformance': [{'kind': 'mandatoryConform'}], 'required_features': [], 'feature_conformance': {'ABS': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'condition', 'name': 'Zigbee'}]}]}, 'constraints': {}},
        },
    },
}

CLUSTERS = {
    '0x0006': {
        'name': 'On/Off',
        'features': {'LT': 'Lighting', 'DF': 'DeadFrontBehavior', 'OFFONLY': 'OffOnly'},
        'feature_conformance': {'LT': [{'kind': 'optionalConform', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'OFFONLY'}]}]}], 'DF': [{'kind': 'optionalConform', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'OFFONLY'}]}]}], 'OFFONLY': [{'kind': 'optionalConform', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'LT'}, {'kind': 'feature', 'name': 'DF'}]}]}]}]},
        'properties': {
            'OnOff': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': False, 'default': None},
            'GlobalSceneControl': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'LT'}]}], 'value_type': 'boolean', 'initial_value': True, 'constraints': [], 'writable': False, 'default': None},
            'OnTime': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'LT'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'OffWaitTime': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'LT'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'StartUpOnOff': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'LT'}]}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'Off', '1': 'On', '2': 'Toggle'}, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'Off': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'On': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'OFFONLY'}]}]}], 'arguments': []},
            'Toggle': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'OFFONLY'}]}]}], 'arguments': []},
            'OnWithRecallGlobalScene': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'LT'}]}], 'arguments': []},
            'OnWithTimedOff': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'LT'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OnOffControl', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': [('between', 0, 1)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OnTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OffWaitTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)]},
            ]},
        },
    },
    '0x0008': {
        'name': 'Level Control',
        'features': {'OO': 'OnOff', 'LT': 'Lighting', 'FQ': 'Frequency'},
        'feature_conformance': {'OO': [{'kind': 'optionalConform'}], 'LT': [{'kind': 'optionalConform'}], 'FQ': [{'kind': 'provisionalConform'}]},
        'properties': {
            'CurrentLevel': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 'MinLevel', 'MaxLevel')], 'writable': False, 'default': None},
            'RemainingTime': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'LT'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'MinLevel': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'LT'}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'LT'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 254)], 'writable': False, 'default': 0},
            'MaxLevel': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 254, 'constraints': [('between', 'MinLevel', 254)], 'writable': False, 'default': 254},
            'CurrentFrequency': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'FQ'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 'MinFrequency', 'MaxFrequency')], 'writable': False, 'default': 0},
            'MinFrequency': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'FQ'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'MaxFrequency': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'FQ'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('min', 'MinFrequency')], 'writable': False, 'default': 0},
            'Options': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'OnOffTransitionTime': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'OnLevel': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 'MinLevel', 'MaxLevel')], 'writable': True, 'default': None},
            'OnTransitionTime': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'OffTransitionTime': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'DefaultMoveRate': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('min', 1)], 'writable': True, 'default': None},
            'StartUpCurrentLevel': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'LT'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'MoveToLevel': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Level', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 254)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
            ]},
            'Move': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'MoveMode', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Rate', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
            ]},
            'Step': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepMode', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepSize', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
            ]},
            'Stop': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
            ]},
            'MoveToLevelWithOnOff': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Level', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 254)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
            ]},
            'MoveWithOnOff': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'MoveMode', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Rate', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
            ]},
            'StepWithOnOff': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepMode', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepSize', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
            ]},
            'StopWithOnOff': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
            ]},
            'MoveToClosestFrequency': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'FQ'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Frequency', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0025': {
        'name': 'Actions',
        'features': {},
        'feature_conformance': {},
        'properties': {
            'SetupURL': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'string', 'initial_value': '', 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'InstantAction': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ActionID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'InvokeID', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
            ]},
            'InstantActionWithTransition': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ActionID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'InvokeID', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
            ]},
            'StartAction': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ActionID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'InvokeID', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
            ]},
            'StartActionWithDuration': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ActionID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'InvokeID', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Duration', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
            ]},
            'StopAction': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ActionID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'InvokeID', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
            ]},
            'PauseAction': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ActionID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'InvokeID', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
            ]},
            'PauseActionWithDuration': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ActionID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'InvokeID', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Duration', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
            ]},
            'ResumeAction': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ActionID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'InvokeID', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
            ]},
            'EnableAction': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ActionID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'InvokeID', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
            ]},
            'EnableActionWithDuration': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ActionID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'InvokeID', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Duration', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
            ]},
            'DisableAction': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ActionID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'InvokeID', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
            ]},
            'DisableActionWithDuration': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ActionID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'InvokeID', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Duration', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0048': {
        'name': 'Oven Cavity Operational State',
        'features': {},
        'feature_conformance': {},
        'properties': {
            'CurrentPhase': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'Pause': {'conformance': [{'kind': 'disallowConform'}], 'arguments': []},
            'Stop': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'command', 'name': 'Start'}]}, {'kind': 'optionalConform'}]}], 'arguments': []},
            'Start': {'conformance': [{'kind': 'optionalConform'}], 'arguments': []},
            'Resume': {'conformance': [{'kind': 'disallowConform'}], 'arguments': []},
        },
    },
    '0x0049': {
        'name': 'Oven Mode',
        'features': {'DEPONOFF': 'OnOff'},
        'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]},
        'properties': {
            'CurrentMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'StartUpMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'OnMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'ChangeToMode': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'NewMode', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x004A': {
        'name': 'Laundry Dryer Controls',
        'features': {},
        'feature_conformance': {},
        'properties': {
            'SelectedDrynessLevel': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3], 'enum_labels': {'0': 'Low', '1': 'Normal', '2': 'Extra', '3': 'Max'}, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
        },
    },
    '0x0050': {
        'name': 'Mode Select',
        'features': {'DEPONOFF': 'OnOff'},
        'feature_conformance': {'DEPONOFF': [{'kind': 'optionalConform'}]},
        'properties': {
            'Description': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'string', 'initial_value': '', 'constraints': [], 'writable': False, 'default': None},
            'CurrentMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'StartUpMode': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'OnMode': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'DEPONOFF'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'ChangeToMode': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'NewMode', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0051': {
        'name': 'Laundry Washer Mode',
        'features': {'DEPONOFF': 'OnOff'},
        'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]},
        'properties': {
            'CurrentMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'StartUpMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'OnMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'ChangeToMode': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'NewMode', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0052': {
        'name': 'Refrigerator And Temperature Controlled Cabinet Mode',
        'features': {'DEPONOFF': 'OnOff'},
        'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]},
        'properties': {
            'CurrentMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'StartUpMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'OnMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'ChangeToMode': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'NewMode', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0053': {
        'name': 'Laundry Washer Controls',
        'features': {'SPIN': 'Spin', 'RINSE': 'Rinse'},
        'feature_conformance': {'SPIN': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'RINSE': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}]},
        'properties': {
            'SpinSpeedCurrent': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SPIN'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 15)], 'writable': True, 'default': None},
            'NumberOfRinses': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'RINSE'}]}], 'value_type': 'integer', 'initial_value': 1, 'enum_values': [0, 1, 2, 3], 'enum_labels': {'0': 'None', '1': 'Normal', '2': 'Extra', '3': 'Max'}, 'constraints': [], 'writable': True, 'default': 1},
        },
        'commands': {
        },
    },
    '0x0054': {
        'name': 'RVC Run Mode',
        'features': {'DEPONOFF': 'OnOff'},
        'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]},
        'properties': {
            'CurrentMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'StartUpMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'OnMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'ChangeToMode': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'NewMode', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0055': {
        'name': 'RVC Clean Mode',
        'features': {'DEPONOFF': 'OnOff'},
        'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]},
        'properties': {
            'CurrentMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'StartUpMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'OnMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'ChangeToMode': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'NewMode', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0056': {
        'name': 'Temperature Control',
        'features': {'TN': 'TemperatureNumber', 'TL': 'TemperatureLevel', 'STEP': 'TemperatureStep'},
        'feature_conformance': {'TN': [{'kind': 'optionalConform', 'choice': 'a'}], 'TL': [{'kind': 'optionalConform', 'choice': 'a'}], 'STEP': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'TN'}]}]},
        'properties': {
            'TemperatureSetpoint': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'TN'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 0, 'constraints': [('between', 'MinTemperature', 'MaxTemperature')], 'writable': False, 'default': None},
            'MinTemperature': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'TN'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MaxTemperature': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'TN'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'Step': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'STEP'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'SelectedTemperatureLevel': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'TL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 31)], 'writable': False, 'default': None},
        },
        'commands': {
            'SetTemperature': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'TN'}]}], 'name': 'TargetTemperature', 'required': True, 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'TL'}]}], 'name': 'TargetTemperatureLevel', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0057': {
        'name': 'Refrigerator Alarm',
        'features': {'RESET': 'Reset'},
        'feature_conformance': {'RESET': [{'kind': 'disallowConform'}]},
        'properties': {
            'Mask': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'Latch': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'RESET'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'State': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'Supported': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
        },
        'commands': {
            'Reset': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'RESET'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Alarms', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'ModifyEnabledAlarms': {'conformance': [{'kind': 'disallowConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Mask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0059': {
        'name': 'Dishwasher Mode',
        'features': {'DEPONOFF': 'OnOff'},
        'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]},
        'properties': {
            'CurrentMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'StartUpMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'OnMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'ChangeToMode': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'NewMode', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x005C': {
        'name': 'Smoke CO Alarm',
        'features': {'SMOKE': 'SmokeAlarm', 'CO': 'COAlarm'},
        'feature_conformance': {'SMOKE': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'CO': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}]},
        'properties': {
            'ExpressedState': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'enum_labels': {'0': 'Normal', '1': 'SmokeAlarm', '2': 'COAlarm', '3': 'BatteryAlert', '4': 'Testing', '5': 'HardwareFault', '6': 'EndOfService', '7': 'InterconnectSmoke', '8': 'InterconnectCO'}, 'constraints': [], 'writable': False, 'default': None},
            'SmokeState': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SMOKE'}]}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'Normal', '1': 'Warning', '2': 'Critical'}, 'constraints': [], 'writable': False, 'default': None},
            'COState': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CO'}]}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'Normal', '1': 'Warning', '2': 'Critical'}, 'constraints': [], 'writable': False, 'default': None},
            'BatteryAlert': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'Normal', '1': 'Warning', '2': 'Critical'}, 'constraints': [], 'writable': False, 'default': None},
            'DeviceMuted': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'enum_labels': {'0': 'NotMuted', '1': 'Muted'}, 'constraints': [], 'writable': False, 'default': None},
            'TestInProgress': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': False, 'default': None},
            'HardwareFaultAlert': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': False, 'default': None},
            'EndOfServiceAlert': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'enum_labels': {'0': 'Normal', '1': 'Expired'}, 'constraints': [], 'writable': False, 'default': None},
            'InterconnectSmokeAlarm': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'Normal', '1': 'Warning', '2': 'Critical'}, 'constraints': [], 'writable': False, 'default': None},
            'InterconnectCOAlarm': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'Normal', '1': 'Warning', '2': 'Critical'}, 'constraints': [], 'writable': False, 'default': None},
            'ContaminationState': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'SMOKE'}]}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3], 'enum_labels': {'0': 'Normal', '1': 'Low', '2': 'Warning', '3': 'Critical'}, 'constraints': [], 'writable': False, 'default': None},
            'SmokeSensitivityLevel': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'SMOKE'}]}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'High', '1': 'Standard', '2': 'Low'}, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'SelfTestRequest': {'conformance': [{'kind': 'optionalConform'}], 'arguments': []},
        },
    },
    '0x005D': {
        'name': 'Dishwasher Alarm',
        'features': {'RESET': 'Reset'},
        'feature_conformance': {'RESET': [{'kind': 'optionalConform'}]},
        'properties': {
            'Mask': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 63.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'Latch': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'RESET'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 63.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'State': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 63.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'Supported': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 63.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
        },
        'commands': {
            'Reset': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'RESET'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Alarms', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 63.0, 'initial_value': 0, 'constraints': []},
            ]},
            'ModifyEnabledAlarms': {'conformance': [{'kind': 'optionalConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Mask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 63.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x005E': {
        'name': 'Microwave Oven Mode',
        'features': {'DEPONOFF': 'OnOff'},
        'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]},
        'properties': {
            'CurrentMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'StartUpMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'OnMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'ChangeToMode': {'conformance': [{'kind': 'disallowConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'NewMode', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x005F': {
        'name': 'Microwave Oven Control',
        'features': {'PWRNUM': 'PowerAsNumber', 'WATTS': 'PowerInWatts', 'PWRLMTS': 'PowerNumberLimits'},
        'feature_conformance': {'PWRNUM': [{'kind': 'optionalConform', 'choice': 'a'}], 'WATTS': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'provisionalConform'}, {'kind': 'optionalConform', 'choice': 'a'}]}], 'PWRLMTS': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'PWRNUM'}]}]},
        'properties': {
            'PowerSetting': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PWRNUM'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MinPower': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PWRLMTS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 10, 'constraints': [('between', 1, 99)], 'writable': False, 'default': 10},
            'MaxPower': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PWRLMTS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 100, 'constraints': [('max', 100)], 'writable': False, 'default': 100},
            'PowerStep': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PWRLMTS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 10, 'constraints': [], 'writable': False, 'default': 10},
            'SelectedWattIndex': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'provisionalConform'}, {'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'WATTS'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'WattRating': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'SetCookingParameters': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'optionalConform', 'choice': 'b', 'more': 'true'}], 'name': 'CookMode', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform', 'choice': 'b', 'more': 'true', 'terms': [{'kind': 'feature', 'name': 'PWRNUM'}]}], 'name': 'PowerSetting', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 100, 'constraints': [('between', 'MinPower', 'MaxPower')], 'default': 'MaxPower'},
                {'conformance': [{'kind': 'optionalConform', 'choice': 'b', 'more': 'true', 'terms': [{'kind': 'feature', 'name': 'WATTS'}]}], 'name': 'WattSettingIndex', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'StartAfterSetting', 'required': False, 'value_type': 'boolean', 'initial_value': False, 'constraints': []},
            ]},
        },
    },
    '0x0060': {
        'name': 'Operational State',
        'features': {},
        'feature_conformance': {},
        'properties': {
            'CurrentPhase': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'Pause': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'command', 'name': 'Resume'}]}, {'kind': 'optionalConform'}]}], 'arguments': []},
            'Stop': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'command', 'name': 'Start'}]}, {'kind': 'optionalConform'}]}], 'arguments': []},
            'Start': {'conformance': [{'kind': 'optionalConform'}], 'arguments': []},
            'Resume': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'command', 'name': 'Pause'}]}, {'kind': 'optionalConform'}]}], 'arguments': []},
        },
    },
    '0x0061': {
        'name': 'RVC Operational State',
        'features': {},
        'feature_conformance': {},
        'properties': {
            'CurrentPhase': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'OperationalState': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 64, 'enum_values': [64, 65, 66], 'enum_labels': {'0x40': 'SeekingCharger', '0x41': 'Charging', '0x42': 'Docked'}, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'Pause': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'command', 'name': 'Resume'}]}, {'kind': 'optionalConform'}]}], 'arguments': []},
            'Stop': {'conformance': [{'kind': 'disallowConform'}], 'arguments': []},
            'Start': {'conformance': [{'kind': 'disallowConform'}], 'arguments': []},
            'Resume': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'command', 'name': 'Pause'}]}, {'kind': 'optionalConform'}]}], 'arguments': []},
            'GoHome': {'conformance': [{'kind': 'optionalConform'}], 'arguments': []},
        },
    },
    '0x0071': {
        'name': 'Resource Monitoring Clusters',
        'features': {'CON': 'Condition', 'WRN': 'Warning', 'REP': 'ReplacementProductList'},
        'feature_conformance': {'CON': [{'kind': 'optionalConform'}], 'WRN': [{'kind': 'optionalConform'}], 'REP': [{'kind': 'optionalConform'}]},
        'properties': {
            'Condition': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CON'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'DegradationDirection': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CON'}]}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'enum_labels': {'0': 'Up', '1': 'Down'}, 'constraints': [], 'writable': False, 'default': None},
            'ChangeIndication': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'OK', '1': 'Warning', '2': 'Critical'}, 'constraints': [], 'writable': False, 'default': 0},
            'InPlaceIndicator': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'ResetCondition': {'conformance': [{'kind': 'optionalConform'}], 'arguments': []},
        },
    },
    '0x0072': {
        'name': 'Resource Monitoring Clusters',
        'features': {'CON': 'Condition', 'WRN': 'Warning', 'REP': 'ReplacementProductList'},
        'feature_conformance': {'CON': [{'kind': 'optionalConform'}], 'WRN': [{'kind': 'optionalConform'}], 'REP': [{'kind': 'optionalConform'}]},
        'properties': {
            'Condition': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CON'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'DegradationDirection': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CON'}]}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'enum_labels': {'0': 'Up', '1': 'Down'}, 'constraints': [], 'writable': False, 'default': None},
            'ChangeIndication': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'OK', '1': 'Warning', '2': 'Critical'}, 'constraints': [], 'writable': False, 'default': 0},
            'InPlaceIndicator': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'ResetCondition': {'conformance': [{'kind': 'optionalConform'}], 'arguments': []},
        },
    },
    '0x0080': {
        'name': 'Boolean State Configuration',
        'features': {'VIS': 'Visual', 'AUD': 'Audible', 'SPRS': 'AlarmSuppress', 'SENSLVL': 'SensitivityLevel'},
        'feature_conformance': {'VIS': [{'kind': 'optionalConform'}], 'AUD': [{'kind': 'optionalConform'}], 'SPRS': [{'kind': 'optionalConform', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'VIS'}, {'kind': 'feature', 'name': 'AUD'}]}]}], 'SENSLVL': [{'kind': 'optionalConform'}]},
        'properties': {
            'CurrentSensitivityLevel': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SENSLVL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'SupportedSensitivityLevels': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SENSLVL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 2, 10)], 'writable': False, 'default': None},
            'DefaultSensitivityLevel': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'SENSLVL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'AlarmsActive': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'VIS'}, {'kind': 'feature', 'name': 'AUD'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'AlarmsSuppressed': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SPRS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'AlarmsEnabled': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'VIS'}, {'kind': 'feature', 'name': 'AUD'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'AlarmsSupported': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'VIS'}, {'kind': 'feature', 'name': 'AUD'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'SensorFault': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
        },
        'commands': {
            'SuppressAlarm': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SPRS'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'AlarmsToSuppress', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
            ]},
            'EnableDisableAlarm': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'VIS'}, {'kind': 'feature', 'name': 'AUD'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'AlarmsToEnableDisable', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0081': {
        'name': 'Valve Configuration and Control',
        'features': {'TS': 'TimeSync', 'LVL': 'Level'},
        'feature_conformance': {'TS': [], 'LVL': [{'kind': 'optionalConform'}]},
        'properties': {
            'CurrentState': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'Closed', '1': 'Open', '2': 'Transitioning'}, 'constraints': [], 'writable': False, 'default': None},
            'TargetState': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'Closed', '1': 'Open', '2': 'Transitioning'}, 'constraints': [], 'writable': False, 'default': None},
            'CurrentLevel': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'LVL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'TargetLevel': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'LVL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'DefaultOpenLevel': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'LVL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 100, 'constraints': [('between', 1, 100)], 'writable': True, 'default': 100},
            'ValveFault': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 63.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'LevelStep': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'LVL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 1, 'constraints': [('between', 1, 50)], 'writable': False, 'default': 1},
        },
        'commands': {
            'Open': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'LVL'}]}], 'name': 'TargetLevel', 'required': False, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 0, 'constraints': [('min', 1)]},
            ]},
            'Close': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
        },
    },
    '0x0094': {
        'name': 'Water Heater Management',
        'features': {'EM': 'EnergyManagement', 'TP': 'TankPercent'},
        'feature_conformance': {'EM': [{'kind': 'optionalConform'}], 'TP': [{'kind': 'optionalConform'}]},
        'properties': {
            'HeaterTypes': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 31.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'HeatDemand': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 31.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'TankVolume': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'EM'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'TankPercentage': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'TP'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'BoostState': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'enum_labels': {'0': 'Inactive', '1': 'Active'}, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'CancelBoost': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
        },
    },
    '0x0097': {
        'name': 'Messages',
        'features': {'CONF': 'ReceivedConfirmation', 'RESP': 'ConfirmationResponse', 'RPLY': 'ConfirmationReply', 'PROT': 'ProtectedMessages'},
        'feature_conformance': {'CONF': [{'kind': 'optionalConform'}], 'RESP': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'CONF'}]}], 'RPLY': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'CONF'}]}], 'PROT': [{'kind': 'optionalConform'}]},
        'properties': {
        },
        'commands': {
        },
    },
    '0x0099': {
        'name': 'Energy EVSE',
        'features': {'PREF': 'ChargingPreferences', 'SOC': 'SoCReporting', 'PNC': 'PlugAndCharge', 'RFID': 'RFID', 'V2X': 'V2X'},
        'feature_conformance': {'PREF': [{'kind': 'mandatoryConform'}], 'SOC': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'provisionalConform'}, {'kind': 'optionalConform'}]}], 'PNC': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'provisionalConform'}, {'kind': 'optionalConform'}]}], 'RFID': [{'kind': 'optionalConform'}], 'V2X': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'provisionalConform'}, {'kind': 'optionalConform'}]}]},
        'properties': {
            'State': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5, 6], 'enum_labels': {'0': 'NotPluggedIn', '1': 'PluggedInNoDemand', '2': 'PluggedInDemand', '3': 'PluggedInCharging', '4': 'PluggedInDischarging', '5': 'SessionEnding', '6': 'Fault'}, 'constraints': [], 'writable': False, 'default': None},
            'SupplyState': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5], 'enum_labels': {'0': 'Disabled', '1': 'ChargingEnabled', '2': 'DischargingEnabled', '3': 'DisabledError', '4': 'DisabledDiagnostics', '5': 'Enabled'}, 'constraints': [], 'writable': False, 'default': None},
            'FaultState': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 255], 'enum_labels': {'0': 'NoError', '1': 'MeterFailure', '2': 'OverVoltage', '3': 'UnderVoltage', '4': 'OverCurrent', '5': 'ContactWetFailure', '6': 'ContactDryFailure', '7': 'GroundFault', '8': 'PowerLoss', '9': 'PowerQuality', '10': 'PilotShortCircuit', '11': 'EmergencyStop', '12': 'EVDisconnected', '13': 'WrongPowerSupply', '14': 'LiveNeutralSwap', '15': 'OverTemperature', '255': 'Other'}, 'constraints': [], 'writable': False, 'default': None},
            'NextChargeTargetSoC': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PREF'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'ApproximateEVEfficiency': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'PREF'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'StateOfCharge': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SOC'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'VehicleID': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PNC'}]}], 'value_type': 'string', 'initial_value': '', 'constraints': [], 'writable': False, 'default': None},
            'SessionID': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'Disable': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'StartDiagnostics': {'conformance': [{'kind': 'optionalConform'}], 'arguments': []},
            'GetTargets': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PREF'}]}], 'arguments': []},
            'ClearTargets': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PREF'}]}], 'arguments': []},
        },
    },
    '0x009B': {
        'name': 'Energy Preference',
        'features': {'BALA': 'EnergyBalance', 'LPMS': 'LowPowerModeSensitivity'},
        'feature_conformance': {'BALA': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'LPMS': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}]},
        'properties': {
            'CurrentEnergyBalance': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'BALA'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'CurrentLowPowerModeSensitivity': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'LPMS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
        },
    },
    '0x009D': {
        'name': 'Energy EVSE Mode',
        'features': {'DEPONOFF': 'OnOff'},
        'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]},
        'properties': {
            'CurrentMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'StartUpMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'OnMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'ChangeToMode': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'NewMode', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x009E': {
        'name': 'Water Heater Mode',
        'features': {'DEPONOFF': 'OnOff'},
        'feature_conformance': {'DEPONOFF': [{'kind': 'disallowConform'}]},
        'properties': {
            'CurrentMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'StartUpMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'OnMode': {'conformance': [{'kind': 'disallowConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
            'ChangeToMode': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'NewMode', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0101': {
        'name': 'Door Lock',
        'features': {'PIN': 'PINCredential', 'RID': 'RFIDCredential', 'FGP': 'FingerCredentials', 'WDSCH': 'WeekDayAccessSchedules', 'DPS': 'DoorPositionSensor', 'FACE': 'FaceCredentials', 'COTA': 'CredentialOverTheAirAccess', 'USR': 'User', 'YDSCH': 'YearDayAccessSchedules', 'HDSCH': 'HolidaySchedules', 'UBOLT': 'Unbolting', 'ALIRO': 'AliroProvisioning', 'ALBU': 'AliroBLEUWB'},
        'feature_conformance': {'PIN': [{'kind': 'optionalConform'}], 'RID': [{'kind': 'optionalConform'}], 'FGP': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'provisionalConform'}, {'kind': 'optionalConform'}]}], 'WDSCH': [{'kind': 'optionalConform'}], 'DPS': [{'kind': 'optionalConform'}], 'FACE': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'provisionalConform'}, {'kind': 'optionalConform'}]}], 'COTA': [{'kind': 'optionalConform'}], 'USR': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'ALIRO'}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIN'}, {'kind': 'feature', 'name': 'RID'}, {'kind': 'feature', 'name': 'FGP'}, {'kind': 'feature', 'name': 'FACE'}]}]}]}], 'YDSCH': [{'kind': 'optionalConform'}], 'HDSCH': [{'kind': 'optionalConform'}], 'UBOLT': [{'kind': 'optionalConform'}], 'ALIRO': [{'kind': 'optionalConform'}], 'ALBU': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'ALIRO'}]}]},
        'properties': {
            'LockState': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3], 'enum_labels': {'0': 'NotFullyLocked', '1': 'Locked', '2': 'Unlocked', '3': 'Unlatched'}, 'constraints': [], 'writable': False, 'default': None},
            'LockType': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 'enum_labels': {'0': 'DeadBolt', '1': 'Magnetic', '2': 'Other', '3': 'Mortise', '4': 'Rim', '5': 'LatchBolt', '6': 'CylindricalLock', '7': 'TubularLock', '8': 'InterconnectedLock', '9': 'DeadLatch', '10': 'DoorFurniture', '11': 'Eurocylinder'}, 'constraints': [], 'writable': False, 'default': None},
            'ActuatorEnabled': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': False, 'default': None},
            'DoorState': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'DPS'}]}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5], 'enum_labels': {'0': 'DoorOpen', '1': 'DoorClosed', '2': 'DoorJammed', '3': 'DoorForcedOpen', '4': 'DoorUnspecifiedError', '5': 'DoorAjar'}, 'constraints': [], 'writable': False, 'default': None},
            'DoorOpenEvents': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'DPS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'DoorClosedEvents': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'DPS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'OpenPeriod': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'DPS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'NumberOfTotalUsersSupported': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'USR'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'NumberOfPINUsersSupported': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PIN'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'NumberOfRFIDUsersSupported': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'RID'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'NumberOfWeekDaySchedulesSupportedPerUser': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'WDSCH'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 253)], 'writable': False, 'default': 0},
            'NumberOfYearDaySchedulesSupportedPerUser': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'YDSCH'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 253)], 'writable': False, 'default': 0},
            'NumberOfHolidaySchedulesSupported': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HDSCH'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 253)], 'writable': False, 'default': 0},
            'MaxPINCodeLength': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PIN'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MinPINCodeLength': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PIN'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MaxRFIDCodeLength': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'RID'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MinRFIDCodeLength': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'RID'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'CredentialRulesSupport': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'USR'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 7.0, 'initial_value': 1, 'constraints': [], 'writable': False, 'default': 1},
            'NumberOfCredentialsSupportedPerUser': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'USR'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'Language': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'string', 'initial_value': '', 'constraints': [], 'writable': False, 'default': None},
            'LEDSettings': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'NoLEDSignal', '1': 'NoLEDSignalAccessAllowed', '2': 'LEDSignalAll'}, 'constraints': [], 'writable': False, 'default': 0},
            'AutoRelockTime': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'SoundVolume': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3], 'enum_labels': {'0': 'Silent', '1': 'Low', '2': 'High', '3': 'Medium'}, 'constraints': [], 'writable': False, 'default': 0},
            'OperatingMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4], 'enum_labels': {'0': 'Normal', '1': 'Vacation', '2': 'Privacy', '3': 'NoRemoteLockUnlock', '4': 'Passage'}, 'constraints': [], 'writable': False, 'default': 0},
            'SupportedOperatingModes': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 31.0, 'initial_value': 31, 'constraints': [], 'writable': False, 'default': 65526},
            'DefaultConfigurationRegister': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'EnableLocalProgramming': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': False, 'default': 1},
            'EnableOneTouchLocking': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': True, 'default': 0},
            'EnableInsideStatusLED': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': True, 'default': 0},
            'EnablePrivacyModeButton': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': True, 'default': 0},
            'LocalProgrammingFeatures': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 15.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'WrongCodeEntryLimit': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIN'}, {'kind': 'feature', 'name': 'RID'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 1, 255)], 'writable': False, 'default': None},
            'UserCodeTemporaryDisableTime': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIN'}, {'kind': 'feature', 'name': 'RID'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 1, 255)], 'writable': False, 'default': None},
            'SendPINOverTheAir': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'USR'}]}, {'kind': 'feature', 'name': 'PIN'}]}]}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': False, 'default': 0},
            'RequirePINforRemoteOperation': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'COTA'}, {'kind': 'feature', 'name': 'PIN'}]}]}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': False, 'default': 0},
            'ExpiringUserTimeout': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'USR'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 2880)], 'writable': False, 'default': None},
            'AlarmMask': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 127.0, 'initial_value': 127, 'constraints': [], 'writable': True, 'default': 65535},
            'AliroBLEAdvertisingVersion': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'ALBU'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'NumberOfAliroCredentialIssuerKeysSupported': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'ALIRO'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'NumberOfAliroEndpointKeysSupported': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'ALIRO'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
        },
        'commands': {
            'LockDoor': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'UnlockDoor': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'Toggle': {'conformance': [{'kind': 'disallowConform'}], 'arguments': []},
            'UnlockWithTimeout': {'conformance': [{'kind': 'optionalConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Timeout', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
            ]},
            'GetPINCode': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'USR'}]}, {'kind': 'feature', 'name': 'PIN'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
            ]},
            'ClearPINCode': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'USR'}]}, {'kind': 'feature', 'name': 'PIN'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'PINSlotIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfPINUsersSupported'), ('allowed', 65534)]},
            ]},
            'ClearAllPINCodes': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'USR'}]}, {'kind': 'feature', 'name': 'PIN'}]}]}], 'arguments': []},
            'SetUserStatus': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'USR'}]}, {'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIN'}, {'kind': 'feature', 'name': 'RID'}, {'kind': 'feature', 'name': 'FGP'}]}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserStatus', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 3], 'constraints': []},
            ]},
            'GetUserStatus': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'USR'}]}, {'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIN'}, {'kind': 'feature', 'name': 'RID'}, {'kind': 'feature', 'name': 'FGP'}]}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
            ]},
            'SetWeekDaySchedule': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'WDSCH'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'WeekDayIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfWeekDaySchedulesSupportedPerUser')]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfTotalUsersSupported')]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'DaysMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 127.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StartHour', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 23)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StartMinute', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 59)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'EndHour', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 23)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'EndMinute', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 59)]},
            ]},
            'GetWeekDaySchedule': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'WDSCH'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'WeekDayIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfWeekDaySchedulesSupportedPerUser')]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfTotalUsersSupported')]},
            ]},
            'ClearWeekDaySchedule': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'WDSCH'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'WeekDayIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfWeekDaySchedulesSupportedPerUser'), ('allowed', 254)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfTotalUsersSupported')]},
            ]},
            'GetYearDaySchedule': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'YDSCH'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'YearDayIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfYearDaySchedulesSupportedPerUser')]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfTotalUsersSupported')]},
            ]},
            'ClearYearDaySchedule': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'YDSCH'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'YearDayIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfYearDaySchedulesSupportedPerUser'), ('allowed', 254)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfTotalUsersSupported')]},
            ]},
            'GetHolidaySchedule': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HDSCH'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'HolidayIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfHolidaySchedulesSupported')]},
            ]},
            'ClearHolidaySchedule': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HDSCH'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'HolidayIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfHolidaySchedulesSupported'), ('allowed', 254)]},
            ]},
            'SetUserType': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'USR'}]}, {'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIN'}, {'kind': 'feature', 'name': 'RID'}, {'kind': 'feature', 'name': 'FGP'}]}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserType', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 'constraints': []},
            ]},
            'GetUserType': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'USR'}]}, {'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIN'}, {'kind': 'feature', 'name': 'RID'}, {'kind': 'feature', 'name': 'FGP'}]}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
            ]},
            'GetRFIDCode': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'USR'}]}, {'kind': 'feature', 'name': 'RID'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
            ]},
            'ClearRFIDCode': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'USR'}]}, {'kind': 'feature', 'name': 'RID'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'RFIDSlotIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfRFIDUsersSupported'), ('allowed', 65534)]},
            ]},
            'ClearAllRFIDCodes': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'USR'}]}, {'kind': 'feature', 'name': 'RID'}]}]}], 'arguments': []},
            'SetUser': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'USR'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OperationType', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfTotalUsersSupported')]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserName', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserUniqueID', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 4294967295, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserStatus', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 3], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserType', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'CredentialRule', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'constraints': []},
            ]},
            'GetUser': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'USR'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfTotalUsersSupported')]},
            ]},
            'ClearUser': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'USR'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UserIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 'NumberOfTotalUsersSupported'), ('allowed', 65534)]},
            ]},
            'UnboltDoor': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'UBOLT'}]}], 'arguments': []},
            'ClearAliroReaderConfig': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'ALIRO'}]}], 'arguments': []},
        },
    },
    '0x0102': {
        'name': 'Window Covering',
        'features': {'LF': 'Lift', 'TL': 'Tilt', 'PA_LF': 'PositionAwareLift', 'ABS': 'AbsolutePosition', 'PA_TL': 'PositionAwareTilt'},
        'feature_conformance': {'LF': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'TL': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'PA_LF': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'LF'}]}], 'ABS': [{'kind': 'optionalConform'}], 'PA_TL': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'TL'}]}]},
        'properties': {
            'Type': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 255], 'enum_labels': {'0': 'RollerShade', '1': 'RollerShade2Motor', '2': 'RollerShadeExterior', '3': 'RollerShadeExterior2Motor', '4': 'Drapery', '5': 'Awning', '6': 'Shutter', '7': 'TiltBlindTiltOnly', '8': 'TiltBlindLiftAndTilt', '9': 'ProjectorScreen', '255': 'Unknown'}, 'constraints': [], 'writable': False, 'default': 0},
            'PhysicalClosedLimitLift': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'LF'}, {'kind': 'feature', 'name': 'PA_LF'}, {'kind': 'feature', 'name': 'ABS'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'PhysicalClosedLimitTilt': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'TL'}, {'kind': 'feature', 'name': 'PA_TL'}, {'kind': 'feature', 'name': 'ABS'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'CurrentPositionLift': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'LF'}, {'kind': 'feature', 'name': 'PA_LF'}, {'kind': 'feature', 'name': 'ABS'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 'InstalledOpenLimitLift', 'InstalledClosedLimitLift')], 'writable': False, 'default': None},
            'CurrentPositionTilt': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'TL'}, {'kind': 'feature', 'name': 'PA_TL'}, {'kind': 'feature', 'name': 'ABS'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 'InstalledOpenLimitTilt', 'InstalledClosedLimitTilt')], 'writable': False, 'default': None},
            'NumberOfActuationsLift': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'LF'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'NumberOfActuationsTilt': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'TL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'ConfigStatus': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 127.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'CurrentPositionLiftPercentage': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'LF'}, {'kind': 'feature', 'name': 'PA_LF'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'CurrentPositionTiltPercentage': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'TL'}, {'kind': 'feature', 'name': 'PA_TL'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'OperationalStatus': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 63.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'TargetPositionLiftPercent100ths': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'LF'}, {'kind': 'feature', 'name': 'PA_LF'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 10000.0, 'unit': '0.01%', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'TargetPositionTiltPercent100ths': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'TL'}, {'kind': 'feature', 'name': 'PA_TL'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 10000.0, 'unit': '0.01%', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'EndProductType': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 255], 'enum_labels': {'0': 'RollerShade', '1': 'RomanShade', '2': 'BalloonShade', '3': 'WovenWood', '4': 'PleatedShade', '5': 'CellularShade', '6': 'LayeredShade', '7': 'LayeredShade2D', '8': 'SheerShade', '9': 'TiltOnlyInteriorBlind', '10': 'InteriorBlind', '11': 'VerticalBlindStripCurtain', '12': 'InteriorVenetianBlind', '13': 'ExteriorVenetianBlind', '14': 'LateralLeftCurtain', '15': 'LateralRightCurtain', '16': 'CentralCurtain', '17': 'RollerShutter', '18': 'ExteriorVerticalScreen', '19': 'AwningTerracePatio', '20': 'AwningVerticalScreen', '21': 'TiltOnlyPergola', '22': 'SwingingShutter', '23': 'SlidingShutter', '255': 'Unknown'}, 'constraints': [], 'writable': False, 'default': 0},
            'CurrentPositionLiftPercent100ths': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'LF'}, {'kind': 'feature', 'name': 'PA_LF'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 10000.0, 'unit': '0.01%', 'initial_value': 0, 'constraints': [('max', 10000)], 'writable': False, 'default': None},
            'CurrentPositionTiltPercent100ths': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'TL'}, {'kind': 'feature', 'name': 'PA_TL'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 10000.0, 'unit': '0.01%', 'initial_value': 0, 'constraints': [('max', 10000)], 'writable': False, 'default': None},
            'InstalledOpenLimitLift': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'LF'}, {'kind': 'feature', 'name': 'PA_LF'}, {'kind': 'feature', 'name': 'ABS'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)], 'writable': False, 'default': 0},
            'InstalledClosedLimitLift': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'LF'}, {'kind': 'feature', 'name': 'PA_LF'}, {'kind': 'feature', 'name': 'ABS'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 65534, 'constraints': [('max', 65534)], 'writable': False, 'default': 65534},
            'InstalledOpenLimitTilt': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'TL'}, {'kind': 'feature', 'name': 'PA_TL'}, {'kind': 'feature', 'name': 'ABS'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)], 'writable': False, 'default': 0},
            'InstalledClosedLimitTilt': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'TL'}, {'kind': 'feature', 'name': 'PA_TL'}, {'kind': 'feature', 'name': 'ABS'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 65534, 'constraints': [('max', 65534)], 'writable': False, 'default': 65534},
            'SafetyStatus': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4095.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
        },
        'commands': {
            'UpOrOpen': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'DownOrClose': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'StopMotion': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'GoToLiftValue': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'LF'}, {'kind': 'feature', 'name': 'ABS'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'LiftValue', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
            ]},
            'GoToLiftPercentage': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'LF'}, {'kind': 'feature', 'name': 'PA_LF'}]}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'LF'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'LiftPercent100thsValue', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 10000.0, 'unit': '0.01%', 'initial_value': 0, 'constraints': []},
            ]},
            'GoToTiltValue': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'TL'}, {'kind': 'feature', 'name': 'ABS'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TiltValue', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
            ]},
            'GoToTiltPercentage': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'TL'}, {'kind': 'feature', 'name': 'PA_TL'}]}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'TL'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TiltPercent100thsValue', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 10000.0, 'unit': '0.01%', 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0150': {
        'name': 'Service Area',
        'features': {'SELRUN': 'SelectWhileRunning', 'PROG': 'ProgressReporting', 'MAPS': 'Maps'},
        'feature_conformance': {'SELRUN': [{'kind': 'optionalConform'}], 'PROG': [{'kind': 'optionalConform'}], 'MAPS': [{'kind': 'optionalConform'}]},
        'properties': {
            'CurrentArea': {'conformance': [], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'SkipArea': {'conformance': [], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'SkippedArea', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0200': {
        'name': 'Pump Configuration and Control',
        'features': {'PRSCONST': 'ConstantPressure', 'PRSCOMP': 'CompensatedPressure', 'FLW': 'ConstantFlow', 'SPD': 'ConstantSpeed', 'TEMP': 'ConstantTemperature', 'AUTO': 'Automatic', 'LOCAL': 'LocalOperation'},
        'feature_conformance': {'PRSCONST': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'PRSCOMP': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'FLW': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'SPD': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'TEMP': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'AUTO': [{'kind': 'optionalConform'}], 'LOCAL': [{'kind': 'optionalConform'}]},
        'properties': {
            'MaxPressure': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MaxSpeed': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MaxFlow': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MinConstPressure': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PRSCONST'}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MaxConstPressure': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PRSCONST'}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MinCompPressure': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PRSCOMP'}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MaxCompPressure': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PRSCOMP'}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MinConstSpeed': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SPD'}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MaxConstSpeed': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SPD'}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MinConstFlow': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'FLW'}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MaxConstFlow': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'FLW'}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'MinConstTemp': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'TEMP'}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': [('min', -27315)], 'writable': False, 'default': None},
            'MaxConstTemp': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'TEMP'}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': [('min', -27315)], 'writable': False, 'default': None},
            'PumpStatus': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 511.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'EffectiveOperationMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3], 'enum_labels': {'0': 'Normal', '1': 'Minimum', '2': 'Maximum', '3': 'Local'}, 'constraints': [], 'writable': False, 'default': None},
            'EffectiveControlMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 5, 7], 'enum_labels': {'0': 'ConstantSpeed', '1': 'ConstantPressure', '2': 'ProportionalPressure', '3': 'ConstantFlow', '5': 'ConstantTemperature', '7': 'Automatic'}, 'constraints': [], 'writable': False, 'default': None},
            'Capacity': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'Speed': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'LifetimeRunningHours': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 16777215.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'Power': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 16777215.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'LifetimeEnergyConsumed': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 4294967295.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'OperationMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3], 'enum_labels': {'0': 'Normal', '1': 'Minimum', '2': 'Maximum', '3': 'Local'}, 'constraints': [], 'writable': True, 'default': 0},
            'ControlMode': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 5, 7], 'enum_labels': {'0': 'ConstantSpeed', '1': 'ConstantPressure', '2': 'ProportionalPressure', '3': 'ConstantFlow', '5': 'ConstantTemperature', '7': 'Automatic'}, 'constraints': [], 'writable': True, 'default': 0},
        },
        'commands': {
        },
    },
    '0x0201': {
        'name': 'Thermostat',
        'features': {'HEAT': 'Heating', 'COOL': 'Cooling', 'OCC': 'Occupancy', 'SCH': 'ScheduleConfiguration', 'SB': 'Setback', 'AUTO': 'AutoMode', 'LTNE': 'LocalTemperatureNotExposed', 'MSCH': 'MatterScheduleConfiguration', 'PRES': 'Presets'},
        'feature_conformance': {'HEAT': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}, {'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}]}], 'COOL': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}, {'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}]}], 'OCC': [{'kind': 'optionalConform'}], 'SCH': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'optionalConform', 'terms': [{'kind': 'condition', 'name': 'Zigbee'}]}, {'kind': 'deprecateConform'}]}], 'SB': [{'kind': 'optionalConform'}], 'AUTO': [{'kind': 'optionalConform'}], 'LTNE': [{'kind': 'optionalConform'}], 'MSCH': [{'kind': 'optionalConform'}], 'PRES': [{'kind': 'optionalConform'}]},
        'properties': {
            'LocalTemperature': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'OutdoorTemperature': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'Occupancy': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'OCC'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 1, 'constraints': [], 'writable': False, 'default': 1},
            'AbsMinHeatSetpointLimit': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'HEAT'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 700, 'constraints': [], 'writable': False, 'default': 700},
            'AbsMaxHeatSetpointLimit': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'HEAT'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 3000, 'constraints': [], 'writable': False, 'default': 3000},
            'AbsMinCoolSetpointLimit': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'COOL'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 1600, 'constraints': [], 'writable': False, 'default': 1600},
            'AbsMaxCoolSetpointLimit': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'COOL'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 3200, 'constraints': [], 'writable': False, 'default': 3200},
            'PICoolingDemand': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'COOL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'PIHeatingDemand': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'HEAT'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'HVACSystemTypeConfiguration': {'conformance': [{'kind': 'deprecateConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 63.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'OccupiedCoolingSetpoint': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'COOL'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 2600, 'constraints': [], 'writable': True, 'default': 2600},
            'OccupiedHeatingSetpoint': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HEAT'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 2000, 'constraints': [], 'writable': True, 'default': 2000},
            'UnoccupiedCoolingSetpoint': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'COOL'}, {'kind': 'feature', 'name': 'OCC'}]}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 2600, 'constraints': [], 'writable': True, 'default': 2600},
            'UnoccupiedHeatingSetpoint': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'HEAT'}, {'kind': 'feature', 'name': 'OCC'}]}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 2000, 'constraints': [], 'writable': True, 'default': 2000},
            'MinHeatSetpointLimit': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'HEAT'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 700, 'constraints': [], 'writable': True, 'default': 'AbsMinHeatSetpointLimit'},
            'MaxHeatSetpointLimit': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'HEAT'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 3000, 'constraints': [], 'writable': True, 'default': 'AbsMaxHeatSetpointLimit'},
            'MinCoolSetpointLimit': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'COOL'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 1600, 'constraints': [], 'writable': True, 'default': 'AbsMinCoolSetpointLimit'},
            'MaxCoolSetpointLimit': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'COOL'}]}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 3200, 'constraints': [], 'writable': True, 'default': 'AbsMaxCoolSetpointLimit'},
            'RemoteSensing': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 7.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'ControlSequenceOfOperation': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 4, 'enum_values': [0, 1, 2, 3, 4, 5], 'enum_labels': {'0': 'CoolingOnly', '1': 'CoolingWithReheat', '2': 'HeatingOnly', '3': 'HeatingWithReheat', '4': 'CoolingAndHeating', '5': 'CoolingAndHeatingWithReheat'}, 'constraints': [], 'writable': True, 'default': 4},
            'SystemMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 1, 'enum_values': [0, 1, 3, 4, 5, 6, 7, 8, 9], 'enum_labels': {'0': 'Off', '1': 'Auto', '3': 'Cool', '4': 'Heat', '5': 'EmergencyHeat', '6': 'Precooling', '7': 'FanOnly', '8': 'Dry', '9': 'Sleep'}, 'constraints': [], 'writable': True, 'default': 1},
            'AlarmMask': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'condition', 'name': 'Zigbee'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 7.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'ThermostatRunningMode': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'feature', 'name': 'AUTO'}]}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 3, 4], 'enum_labels': {'0': 'Off', '3': 'Cool', '4': 'Heat'}, 'constraints': [], 'writable': False, 'default': 0},
            'StartOfWeek': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SCH'}]}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5, 6], 'enum_labels': {'0': 'Sunday', '1': 'Monday', '2': 'Tuesday', '3': 'Wednesday', '4': 'Thursday', '5': 'Friday', '6': 'Saturday'}, 'constraints': [], 'writable': False, 'default': None},
            'NumberOfWeeklyTransitions': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SCH'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'NumberOfDailyTransitions': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SCH'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'TemperatureSetpointHold': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'enum_labels': {'0': 'SetpointHoldOff', '1': 'SetpointHoldOn'}, 'constraints': [], 'writable': True, 'default': 0},
            'TemperatureSetpointHoldDuration': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 1440)], 'writable': True, 'default': None},
            'ThermostatProgrammingOperationMode': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 7.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'ThermostatRunningState': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 127.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'SetpointChangeSource': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'Manual', '1': 'Schedule', '2': 'External'}, 'constraints': [], 'writable': False, 'default': 0},
            'ACType': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4], 'enum_labels': {'0': 'Unknown', '1': 'CoolingFixed', '2': 'HeatPumpFixed', '3': 'CoolingInverter', '4': 'HeatPumpInverter'}, 'constraints': [], 'writable': True, 'default': 0},
            'ACCapacity': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'ACRefrigerantType': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3], 'enum_labels': {'0': 'Unknown', '1': 'R22', '2': 'R410a', '3': 'R407c'}, 'constraints': [], 'writable': True, 'default': 0},
            'ACCompressorType': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3], 'enum_labels': {'0': 'Unknown', '1': 'T1', '2': 'T2', '3': 'T3'}, 'constraints': [], 'writable': True, 'default': 0},
            'ACErrorCode': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 31.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'ACLouverPosition': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 1, 'enum_values': [1, 2, 3, 4, 5], 'enum_labels': {'1': 'Closed', '2': 'Open', '3': 'Quarter', '4': 'Half', '5': 'ThreeQuarters'}, 'constraints': [], 'writable': True, 'default': 0},
            'ACCoilTemperature': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'unit': '0.01°C', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'ACCapacityFormat': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0], 'enum_labels': {'0': 'BTUh'}, 'constraints': [], 'writable': True, 'default': 0},
            'NumberOfPresets': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PRES'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'NumberOfSchedules': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'MSCH'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'NumberOfScheduleTransitions': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'MSCH'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'NumberOfScheduleTransitionPerDay': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'MSCH'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'SetpointRaiseLower': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Mode', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Amount', 'required': True, 'value_type': 'integer', 'minimum': -128.0, 'maximum': 127.0, 'initial_value': 0, 'constraints': []},
            ]},
            'GetWeeklySchedule': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SCH'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'DaysToReturn', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ModeToReturn', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': []},
            ]},
            'ClearWeeklySchedule': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SCH'}]}], 'arguments': []},
            'GetRelayStatusLog': {'conformance': [{'kind': 'optionalConform', 'terms': [{'kind': 'condition', 'name': 'Zigbee'}]}], 'arguments': []},
        },
    },
    '0x0202': {
        'name': 'Fan Control',
        'features': {'SPD': 'MultiSpeed', 'AUT': 'Auto', 'RCK': 'Rocking', 'WND': 'Wind', 'STEP': 'Step', 'DIR': 'AirflowDirection'},
        'feature_conformance': {'SPD': [{'kind': 'optionalConform'}], 'AUT': [{'kind': 'optionalConform'}], 'RCK': [{'kind': 'optionalConform'}], 'WND': [{'kind': 'optionalConform'}], 'STEP': [{'kind': 'optionalConform'}], 'DIR': [{'kind': 'optionalConform'}]},
        'properties': {
            'FanMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5, 6], 'enum_labels': {'0': 'Off', '1': 'Low', '2': 'Medium', '3': 'High', '4': 'On', '5': 'Auto', '6': 'Smart'}, 'constraints': [], 'writable': True, 'default': 0},
            'FanModeSequence': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'condition', 'name': 'Zigbee'}]}, {'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5], 'enum_labels': {'0': 'OffLowMedHigh', '1': 'OffLowHigh', '2': 'OffLowMedHighAuto', '3': 'OffLowHighAuto', '4': 'OffHighAuto', '5': 'OffHigh'}, 'constraints': [], 'writable': False, 'default': None},
            'PercentSetting': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 0, 'constraints': [('max', 100)], 'writable': True, 'default': 0},
            'PercentCurrent': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 100.0, 'unit': '%', 'initial_value': 0, 'constraints': [('max', 100)], 'writable': False, 'default': None},
            'SpeedMax': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SPD'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('between', 1, 100)], 'writable': False, 'default': None},
            'SpeedSetting': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SPD'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 'SpeedMax')], 'writable': True, 'default': 0},
            'SpeedCurrent': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SPD'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 'SpeedMax')], 'writable': False, 'default': None},
            'RockSupport': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'RCK'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 7.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'RockSetting': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'RCK'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 7.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'WindSupport': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'WND'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'WindSetting': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'WND'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'AirflowDirection': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'DIR'}]}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'enum_labels': {'0': 'Forward', '1': 'Reverse'}, 'constraints': [], 'writable': True, 'default': 0},
        },
        'commands': {
            'Step': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'STEP'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Direction', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'Wrap', 'required': False, 'value_type': 'boolean', 'initial_value': False, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'LowestOff', 'required': False, 'value_type': 'boolean', 'initial_value': True, 'constraints': []},
            ]},
        },
    },
    '0x0204': {
        'name': 'Thermostat User Interface Configuration',
        'features': {},
        'feature_conformance': {},
        'properties': {
            'TemperatureDisplayMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'enum_labels': {'0': 'Celsius', '1': 'Fahrenheit'}, 'constraints': [], 'writable': True, 'default': None},
            'KeypadLockout': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4, 5], 'enum_labels': {'0': 'NoLockout', '1': 'Lockout1', '2': 'Lockout2', '3': 'Lockout3', '4': 'Lockout4', '5': 'Lockout5'}, 'constraints': [], 'writable': True, 'default': None},
            'ScheduleProgrammingVisibility': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'enum_labels': {'0': 'ScheduleProgrammingPermitted', '1': 'ScheduleProgrammingDenied'}, 'constraints': [], 'writable': True, 'default': None},
        },
        'commands': {
        },
    },
    '0x0300': {
        'name': 'Color Control',
        'features': {'HS': 'HueSaturation', 'EHUE': 'EnhancedHue', 'CL': 'ColorLoop', 'XY': 'XY', 'CT': 'ColorTemperature'},
        'feature_conformance': {'HS': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'EHUE'}]}, {'kind': 'optionalConform'}]}], 'EHUE': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CL'}]}, {'kind': 'optionalConform'}]}], 'CL': [{'kind': 'optionalConform'}], 'XY': [{'kind': 'optionalConform'}], 'CT': [{'kind': 'optionalConform'}]},
        'properties': {
            'CurrentHue': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 254)], 'writable': False, 'default': 0},
            'CurrentSaturation': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 254)], 'writable': False, 'default': 0},
            'RemainingTime': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)], 'writable': False, 'default': 0},
            'CurrentX': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'XY'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'CurrentY': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'XY'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'DriftCompensation': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3, 4], 'enum_labels': {'0': 'None', '1': 'OtherOrUnknown', '2': 'TemperatureMonitoring', '3': 'OpticalLuminanceMonitoringAndFeedback', '4': 'OpticalColorMonitoringAndFeedback'}, 'constraints': [], 'writable': False, 'default': None},
            'CompensationText': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'string', 'initial_value': '', 'constraints': [], 'writable': False, 'default': None},
            'ColorTemperatureMireds': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CT'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'ColorMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 1, 'enum_values': [0, 1, 2], 'enum_labels': {'0': 'CurrentHueAndCurrentSaturation', '1': 'CurrentXAndCurrentY', '2': 'ColorTemperatureMireds'}, 'constraints': [], 'writable': False, 'default': 1},
            'Options': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'NumberOfPrimaries': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 6)], 'writable': False, 'default': None},
            'Primary1X': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '0'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'Primary1Y': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '0'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'Primary1Intensity': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '0'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'Primary2X': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '1'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'Primary2Y': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '1'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'Primary2Intensity': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '1'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'Primary3X': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '2'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'Primary3Y': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '2'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'Primary3Intensity': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '2'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'Primary4X': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '3'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'Primary4Y': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '3'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'Primary4Intensity': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '3'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'Primary5X': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '4'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'Primary5Y': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '4'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'Primary5Intensity': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '4'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'Primary6X': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '5'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'Primary6Y': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '5'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'Primary6Intensity': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'greaterTerm', 'terms': [{'kind': 'attribute', 'name': 'NumberOfPrimaries'}, {'kind': 'literal', 'value': '5'}]}]}, {'kind': 'optionalConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'WhitePointX': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': True, 'default': None},
            'WhitePointY': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': True, 'default': None},
            'ColorPointRX': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': True, 'default': None},
            'ColorPointRY': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': True, 'default': None},
            'ColorPointRIntensity': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'ColorPointGX': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': True, 'default': None},
            'ColorPointGY': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': True, 'default': None},
            'ColorPointGIntensity': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'ColorPointBX': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': True, 'default': None},
            'ColorPointBY': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': True, 'default': None},
            'ColorPointBIntensity': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'EnhancedCurrentHue': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'EHUE'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'EnhancedColorMode': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 1, 'enum_values': [0, 1, 2, 3], 'enum_labels': {'0': 'CurrentHueAndCurrentSaturation', '1': 'CurrentXAndCurrentY', '2': 'ColorTemperatureMireds', '3': 'EnhancedCurrentHueAndCurrentSaturation'}, 'constraints': [], 'writable': False, 'default': 1},
            'ColorLoopActive': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 1)], 'writable': False, 'default': 0},
            'ColorLoopDirection': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 1)], 'writable': False, 'default': 0},
            'ColorLoopTime': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 25, 'constraints': [], 'writable': False, 'default': 25},
            'ColorLoopStartEnhancedHue': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 8960, 'constraints': [], 'writable': False, 'default': 8960},
            'ColorLoopStoredEnhancedHue': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CL'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'ColorCapabilities': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 31.0, 'initial_value': 0, 'constraints': [('max', 31)], 'writable': False, 'default': 0},
            'ColorTempPhysicalMinMireds': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CT'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 65279)], 'writable': False, 'default': None},
            'ColorTempPhysicalMaxMireds': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CT'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)], 'writable': False, 'default': None},
            'CoupleColorTempToLevelMinMireds': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'CT'}, {'kind': 'attribute', 'name': 'ColorTemperatureMireds'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 'ColorTempPhysicalMinMireds', 'ColorTemperatureMireds')], 'writable': False, 'default': None},
            'StartUpColorTemperatureMireds': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'CT'}, {'kind': 'attribute', 'name': 'ColorTemperatureMireds'}]}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('between', 1, 65279)], 'writable': True, 'default': None},
        },
        'commands': {
            'MoveToHue': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HS'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Hue', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 254)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Direction', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'MoveHue': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HS'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'MoveMode', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 3], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Rate', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'StepHue': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HS'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepMode', 'required': True, 'value_type': 'integer', 'initial_value': 1, 'enum_values': [1, 3], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepSize', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'MoveToSaturation': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HS'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Saturation', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 254)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'MoveSaturation': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HS'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'MoveMode', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 3], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Rate', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'StepSaturation': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HS'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepMode', 'required': True, 'value_type': 'integer', 'initial_value': 1, 'enum_values': [1, 3], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepSize', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'MoveToHueAndSaturation': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'HS'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Hue', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 254)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Saturation', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 254)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'MoveToColor': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'XY'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ColorX', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ColorY', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'MoveColor': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'XY'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'RateX', 'required': True, 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'RateY', 'required': True, 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'StepColor': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'XY'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepX', 'required': True, 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepY', 'required': True, 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'MoveToColorTemperature': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CT'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ColorTemperatureMireds', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'EnhancedMoveToHue': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'EHUE'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'EnhancedHue', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Direction', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'EnhancedMoveHue': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'EHUE'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'MoveMode', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 3], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Rate', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'EnhancedStepHue': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'EHUE'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepMode', 'required': True, 'value_type': 'integer', 'initial_value': 1, 'enum_values': [1, 3], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepSize', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'EnhancedMoveToHueAndSaturation': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'EHUE'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'EnhancedHue', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Saturation', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [('max', 254)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'ColorLoopSet': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CL'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'UpdateFlags', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 15.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Action', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Direction', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Time', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StartHue', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'StopMoveStep': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'HS'}, {'kind': 'feature', 'name': 'XY'}, {'kind': 'feature', 'name': 'CT'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'MoveColorTemperature': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CT'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'MoveMode', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 3], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Rate', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ColorTemperatureMinimumMireds', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ColorTemperatureMaximumMireds', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
            'StepColorTemperature': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'CT'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepMode', 'required': True, 'value_type': 'integer', 'initial_value': 1, 'enum_values': [1, 3], 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'StepSize', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TransitionTime', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65534)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ColorTemperatureMinimumMireds', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ColorTemperatureMaximumMireds', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [('max', 65279)]},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsMask', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OptionsOverride', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': []},
            ]},
        },
    },
    '0x0406': {
        'name': 'Occupancy Sensing',
        'features': {'OTHER': 'Other', 'PIR': 'PassiveInfrared', 'US': 'Ultrasonic', 'PHY': 'PhysicalContact', 'AIR': 'ActiveInfrared', 'RAD': 'Radar', 'RFS': 'RFSensing', 'VIS': 'Vision'},
        'feature_conformance': {'OTHER': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'PIR': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'US': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'PHY': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'AIR': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'RAD': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'RFS': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}], 'VIS': [{'kind': 'optionalConform', 'choice': 'a', 'more': 'true'}]},
        'properties': {
            'Occupancy': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.0, 'initial_value': 0, 'constraints': [('between', 0, 1)], 'writable': False, 'default': None},
            'OccupancySensorType': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform'}, {'kind': 'deprecateConform'}]}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3], 'enum_labels': {'0': 'PIR', '1': 'Ultrasonic', '2': 'PIRAndUltrasonic', '3': 'PhysicalContact'}, 'constraints': [], 'writable': False, 'default': None},
            'OccupancySensorTypeBitmap': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform'}, {'kind': 'deprecateConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 7.0, 'initial_value': 0, 'constraints': [('between', 0, 7)], 'writable': False, 'default': None},
            'HoldTime': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': None},
            'PIROccupiedToUnoccupiedDelay': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIR'}, {'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'PIR'}]}, {'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'US'}]}, {'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'PHY'}]}]}]}]}]}, {'kind': 'deprecateConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'PIRUnoccupiedToOccupiedDelay': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIR'}, {'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'PIR'}]}, {'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'US'}]}, {'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'PHY'}]}]}]}]}, {'kind': 'attribute', 'name': 'PIRUnoccupiedToOccupiedThreshold'}]}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIR'}, {'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'PIR'}]}, {'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'US'}]}, {'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'PHY'}]}]}]}]}]}, {'kind': 'deprecateConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'PIRUnoccupiedToOccupiedThreshold': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIR'}, {'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'PIR'}]}, {'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'US'}]}, {'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'PHY'}]}]}]}]}, {'kind': 'attribute', 'name': 'PIRUnoccupiedToOccupiedDelay'}]}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'PIR'}, {'kind': 'andTerm', 'terms': [{'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'PIR'}]}, {'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'US'}]}, {'kind': 'notTerm', 'terms': [{'kind': 'feature', 'name': 'PHY'}]}]}]}]}]}, {'kind': 'deprecateConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 1, 'constraints': [('between', 1, 254)], 'writable': True, 'default': 1},
            'UltrasonicOccupiedToUnoccupiedDelay': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'feature', 'name': 'US'}]}]}, {'kind': 'deprecateConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'UltrasonicUnoccupiedToOccupiedDelay': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'feature', 'name': 'US'}, {'kind': 'attribute', 'name': 'UltrasonicUnoccupiedToOccupiedThreshold'}]}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'feature', 'name': 'US'}]}]}, {'kind': 'deprecateConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'UltrasonicUnoccupiedToOccupiedThreshold': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'feature', 'name': 'US'}, {'kind': 'attribute', 'name': 'UltrasonicUnoccupiedToOccupiedDelay'}]}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'feature', 'name': 'US'}]}]}, {'kind': 'deprecateConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 1, 'constraints': [('between', 1, 254)], 'writable': True, 'default': 1},
            'PhysicalContactOccupiedToUnoccupiedDelay': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'feature', 'name': 'PHY'}]}]}, {'kind': 'deprecateConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'PhysicalContactUnoccupiedToOccupiedDelay': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'feature', 'name': 'PHY'}, {'kind': 'attribute', 'name': 'PhysicalContactUnoccupiedToOccupiedThreshold'}]}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'feature', 'name': 'PHY'}]}]}, {'kind': 'deprecateConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': True, 'default': 0},
            'PhysicalContactUnoccupiedToOccupiedThreshold': {'conformance': [{'kind': 'otherwiseConform', 'terms': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'feature', 'name': 'PHY'}, {'kind': 'attribute', 'name': 'PhysicalContactUnoccupiedToOccupiedDelay'}]}]}, {'kind': 'optionalConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'attribute', 'name': 'HoldTime'}, {'kind': 'feature', 'name': 'PHY'}]}]}, {'kind': 'deprecateConform'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 1, 'constraints': [('between', 1, 254)], 'writable': True, 'default': 1},
        },
        'commands': {
        },
    },
    '0x0451': {
        'name': 'Wi-Fi Network Management',
        'features': {},
        'feature_conformance': {},
        'properties': {
            'PassphraseSurrogate': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.8446744073709552e+19, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'NetworkPassphraseRequest': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
        },
    },
    '0x0452': {
        'name': 'Thread Border Router Management',
        'features': {'PC': 'PANChange'},
        'feature_conformance': {'PC': [{'kind': 'optionalConform'}]},
        'properties': {
            'BorderRouterName': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'string', 'initial_value': '', 'constraints': [], 'writable': False, 'default': None},
            'ThreadVersion': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'InterfaceEnabled': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': False, 'default': None},
            'ActiveDatasetTimestamp': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.8446744073709552e+19, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'PendingDatasetTimestamp': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.8446744073709552e+19, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
        },
        'commands': {
            'GetActiveDatasetRequest': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'GetPendingDatasetRequest': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
        },
    },
    '0x0453': {
        'name': 'Thread Network Directory',
        'features': {},
        'feature_conformance': {},
        'properties': {
            'ThreadNetworkTableSize': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 10, 'constraints': [], 'writable': False, 'default': 10},
        },
        'commands': {
        },
    },
    '0x0504': {
        'name': 'Channel',
        'features': {'CL': 'ChannelList', 'LI': 'LineupInfo', 'EG': 'ElectronicGuide', 'RP': 'RecordProgram'},
        'feature_conformance': {'CL': [{'kind': 'optionalConform'}], 'LI': [{'kind': 'optionalConform'}], 'EG': [{'kind': 'optionalConform'}], 'RP': [{'kind': 'optionalConform'}]},
        'properties': {
        },
        'commands': {
            'ChangeChannel': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'orTerm', 'terms': [{'kind': 'feature', 'name': 'CL'}, {'kind': 'feature', 'name': 'LI'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Match', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
            ]},
            'ChangeChannelByNumber': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'MajorNumber', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'MinorNumber', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 65535.0, 'initial_value': 0, 'constraints': []},
            ]},
            'SkipChannel': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Count', 'required': True, 'value_type': 'integer', 'minimum': -32768.0, 'maximum': 32767.0, 'initial_value': 0, 'constraints': []},
            ]},
            'RecordProgram': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'RP'}, {'kind': 'feature', 'name': 'EG'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ProgramIdentifier', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ShouldRecordSeries', 'required': True, 'value_type': 'boolean', 'initial_value': False, 'constraints': []},
            ]},
            'CancelRecordProgram': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'andTerm', 'terms': [{'kind': 'feature', 'name': 'RP'}, {'kind': 'feature', 'name': 'EG'}]}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ProgramIdentifier', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ShouldRecordSeries', 'required': True, 'value_type': 'boolean', 'initial_value': False, 'constraints': []},
            ]},
        },
    },
    '0x0505': {
        'name': 'Target Navigator',
        'features': {},
        'feature_conformance': {},
        'properties': {
            'CurrentTarget': {'conformance': [{'kind': 'optionalConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 255, 'constraints': [], 'writable': False, 'default': 255},
        },
        'commands': {
            'NavigateTarget': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Target', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'Data', 'required': False, 'value_type': 'string', 'initial_value': '', 'constraints': []},
            ]},
        },
    },
    '0x0506': {
        'name': 'Media Playback',
        'features': {'AS': 'AdvancedSeek', 'VS': 'VariableSpeed', 'TT': 'TextTracks', 'AT': 'AudioTracks', 'AA': 'AudioAdvance'},
        'feature_conformance': {'AS': [{'kind': 'optionalConform'}], 'VS': [{'kind': 'optionalConform'}], 'TT': [{'kind': 'optionalConform'}], 'AT': [{'kind': 'optionalConform'}], 'AA': [{'kind': 'optionalConform'}]},
        'properties': {
            'CurrentState': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 1, 2, 3], 'enum_labels': {'0': 'Playing', '1': 'Paused', '2': 'NotPlaying', '3': 'Buffering'}, 'constraints': [], 'writable': False, 'default': None},
            'Duration': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'AS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.8446744073709552e+19, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'PlaybackSpeed': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'AS'}]}], 'value_type': 'number', 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
            'SeekRangeEnd': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'AS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.8446744073709552e+19, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
            'SeekRangeStart': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'AS'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.8446744073709552e+19, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'Play': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'Pause': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'Stop': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'StartOver': {'conformance': [{'kind': 'optionalConform'}], 'arguments': []},
            'Previous': {'conformance': [{'kind': 'optionalConform'}], 'arguments': []},
            'Next': {'conformance': [{'kind': 'optionalConform'}], 'arguments': []},
            'Rewind': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'VS'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'AA'}]}], 'name': 'AudioAdvanceUnmuted', 'required': True, 'value_type': 'boolean', 'initial_value': False, 'constraints': []},
            ]},
            'FastForward': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'VS'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'AA'}]}], 'name': 'AudioAdvanceUnmuted', 'required': True, 'value_type': 'boolean', 'initial_value': False, 'constraints': []},
            ]},
            'SkipForward': {'conformance': [{'kind': 'optionalConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'DeltaPositionMilliseconds', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.8446744073709552e+19, 'initial_value': 0, 'constraints': []},
            ]},
            'SkipBackward': {'conformance': [{'kind': 'optionalConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'DeltaPositionMilliseconds', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.8446744073709552e+19, 'initial_value': 0, 'constraints': []},
            ]},
            'Seek': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'AS'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Position', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 1.8446744073709552e+19, 'initial_value': 0, 'constraints': []},
            ]},
            'ActivateAudioTrack': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'AT'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TrackID', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'AT'}]}], 'name': 'AudioOutputIndex', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
            'ActivateTextTrack': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'TT'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TrackID', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
            ]},
            'DeactivateTextTrack': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'TT'}]}], 'arguments': []},
        },
    },
    '0x0507': {
        'name': 'Media Input',
        'features': {'NU': 'NameUpdates'},
        'feature_conformance': {'NU': [{'kind': 'optionalConform'}]},
        'properties': {
            'CurrentInput': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'SelectInput': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Index', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
            'ShowInputStatus': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'HideInputStatus': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'RenameInput': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'NU'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Index', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Name', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
            ]},
        },
    },
    '0x0508': {
        'name': 'Low Power',
        'features': {},
        'feature_conformance': {},
        'properties': {
        },
        'commands': {
            'Sleep': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
        },
    },
    '0x0509': {
        'name': 'Keypad Input',
        'features': {'NV': 'NavigationKeyCodes', 'LK': 'LocationKeys', 'NK': 'NumberKeys'},
        'feature_conformance': {'NV': [{'kind': 'optionalConform'}], 'LK': [{'kind': 'optionalConform'}], 'NK': [{'kind': 'optionalConform'}]},
        'properties': {
        },
        'commands': {
            'SendKey': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'KeyCode', 'required': True, 'value_type': 'integer', 'initial_value': 0, 'enum_values': [0, 10, 11, 12, 13, 1, 29, 30, 31, 2, 42, 43, 44, 47, 3, 4, 74, 75, 76, 77, 78, 79, 5, 6, 106, 107, 108, 109, 7, 8, 9, 16, 17, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 48, 49, 50, 51, 52, 53, 54, 55, 56, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 80, 81, 82, 83, 84, 85, 86, 87, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 113, 114, 115, 116, 117, 118], 'constraints': []},
            ]},
        },
    },
    '0x050A': {
        'name': 'Content Launcher',
        'features': {'CS': 'ContentSearch', 'UP': 'URLPlayback', 'AS': 'AdvancedSeek', 'TT': 'TextTracks', 'AT': 'AudioTracks'},
        'feature_conformance': {'CS': [{'kind': 'optionalConform'}], 'UP': [{'kind': 'optionalConform'}], 'AS': [{'kind': 'optionalConform'}], 'TT': [{'kind': 'optionalConform'}], 'AT': [{'kind': 'optionalConform'}]},
        'properties': {
            'SupportedStreamingProtocols': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'UP'}]}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 3.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': 0},
        },
        'commands': {
            'LaunchURL': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'UP'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'ContentURL', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'DisplayString', 'required': False, 'value_type': 'string', 'initial_value': '', 'constraints': []},
            ]},
        },
    },
    '0x050B': {
        'name': 'Audio Output',
        'features': {'NU': 'NameUpdates'},
        'feature_conformance': {'NU': [{'kind': 'optionalConform'}]},
        'properties': {
            'CurrentOutput': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'SelectOutput': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Index', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
            ]},
            'RenameOutput': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'NU'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Index', 'required': True, 'value_type': 'integer', 'minimum': 0.0, 'maximum': 255.0, 'initial_value': 0, 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Name', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
            ]},
        },
    },
    '0x050C': {
        'name': 'Application Launcher',
        'features': {'AP': 'ApplicationPlatform'},
        'feature_conformance': {'AP': [{'kind': 'optionalConform'}]},
        'properties': {
        },
        'commands': {
        },
    },
    '0x050E': {
        'name': 'Account Login',
        'features': {},
        'feature_conformance': {},
        'properties': {
        },
        'commands': {
            'GetSetupPIN': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TempAccountIdentifier', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
            ]},
            'Login': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'TempAccountIdentifier', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'SetupPIN', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
            ]},
            'Logout': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
        },
    },
    '0x050F': {
        'name': 'Content Control',
        'features': {'ST': 'ScreenTime', 'PM': 'PINManagement', 'BU': 'BlockUnrated', 'OCR': 'OnDemandContentRating', 'SCR': 'ScheduledContentRating', 'BC': 'BlockChannels', 'BA': 'BlockApplications', 'BTW': 'BlockContentTimeWindow'},
        'feature_conformance': {'ST': [{'kind': 'optionalConform'}], 'PM': [{'kind': 'optionalConform'}], 'BU': [{'kind': 'optionalConform'}], 'OCR': [{'kind': 'optionalConform'}], 'SCR': [{'kind': 'optionalConform'}], 'BC': [{'kind': 'optionalConform'}], 'BA': [{'kind': 'optionalConform'}], 'BTW': [{'kind': 'optionalConform'}]},
        'properties': {
            'Enabled': {'conformance': [{'kind': 'mandatoryConform'}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': False, 'default': None},
            'OnDemandRatingThreshold': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'OCR'}]}], 'value_type': 'string', 'initial_value': '', 'constraints': [], 'writable': False, 'default': None},
            'ScheduledContentRatingThreshold': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SCR'}]}], 'value_type': 'string', 'initial_value': '', 'constraints': [], 'writable': False, 'default': None},
            'BlockUnrated': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'BU'}]}], 'value_type': 'boolean', 'initial_value': False, 'constraints': [], 'writable': False, 'default': None},
        },
        'commands': {
            'UpdatePIN': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PM'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'OldPIN', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'NewPIN', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
            ]},
            'ResetPIN': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'PM'}]}], 'arguments': []},
            'Enable': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'Disable': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': []},
            'BlockUnratedContent': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'BU'}]}], 'arguments': []},
            'UnblockUnratedContent': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'BU'}]}], 'arguments': []},
            'SetOnDemandRatingThreshold': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'OCR'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Rating', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
            ]},
            'SetScheduledContentRatingThreshold': {'conformance': [{'kind': 'mandatoryConform', 'terms': [{'kind': 'feature', 'name': 'SCR'}]}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Rating', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
            ]},
        },
    },
    '0x0510': {
        'name': 'Content App Observer',
        'features': {},
        'feature_conformance': {},
        'properties': {
        },
        'commands': {
            'ContentAppMessage': {'conformance': [{'kind': 'mandatoryConform'}], 'arguments': [
                {'conformance': [{'kind': 'mandatoryConform'}], 'name': 'Data', 'required': True, 'value_type': 'string', 'initial_value': '', 'constraints': []},
                {'conformance': [{'kind': 'optionalConform'}], 'name': 'EncodingHint', 'required': False, 'value_type': 'string', 'initial_value': '', 'constraints': []},
            ]},
        },
    },
}

