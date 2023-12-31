import pytz

TZ_LOCAL = pytz.timezone("Europe/Brussels")

# Subset of BELGIUM_FLUVIUS measurements and short names
ELECTRICITY_MEASUREMENTS = {
    "ELECTRICITY_USED_TARIFF_1": "A+(T1)",
    "ELECTRICITY_USED_TARIFF_2": "A+(T2)",
    "ELECTRICITY_DELIVERED_TARIFF_1": "A-(T1)",
    "ELECTRICITY_DELIVERED_TARIFF_2": "A-(T2)",
    # "ELECTRICITY_ACTIVE_TARIFF": "T",
    # "BELGIUM_CURRENT_AVERAGE_DEMAND": "A(AVG)",
    "CURRENT_ELECTRICITY_USAGE": "P+",
    "CURRENT_ELECTRICITY_DELIVERY": "P-",
    "INSTANTANEOUS_VOLTAGE_L1": "U(L1)",
    "INSTANTANEOUS_VOLTAGE_L2": "U(L2)",
    "INSTANTANEOUS_VOLTAGE_L3": "U(L3)",
    "INSTANTANEOUS_CURRENT_L1": "I(L1)",
    "INSTANTANEOUS_CURRENT_L2": "I(L2)",
    "INSTANTANEOUS_CURRENT_L3": "I(L3)",
    "INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE": "P+(L1)",
    "INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE": "P+(L2)",
    "INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE": "P+(L3)",
    "INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE": "P-(L1)",
    "INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE": "P-(L2)",
    "INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE": "P-(L3)",
    # "ACTUAL_SWITCH_POSITION": "SWT",
    # "BELGIUM_MAX_POWER_PER_PHASE": "PMAX",
    # "BELGIUM_MAX_CURRENT_PER_PHASE": "IMAX",
    # "TEXT_MESSAGE": "SMS" # For future use, empty for now
}

MAXIMUM_MEASUREMENTS_HISTORY = ["BELGIUM_MAXIMUM_DEMAND_13_MONTHS"]

MAXIMUM_MEASUREMENTS_ON_GOING = ["BELGIUM_MAXIMUM_DEMAND_MONTH"]

MBUS_MEASUREMENTS = ["MBUS_DEVICES"]
