CREATE = "CREATE"
HYPER = "HYPER"
INSERT = "INSERT"
TEMPLATE = "TEMPLATE"
READ = "READ"

ELEC = {
    CREATE: """
    CREATE TABLE IF NOT EXISTS elec_measurement (
        time TIMESTAMPTZ NOT NULL,
        device_id TEXT NOT NULL,
        obis_name TEXT NOT NULL,
        value REAL,
        PRIMARY KEY (time, device_id, obis_name)
    );""",
    HYPER: "SELECT create_hypertable('elec_measurement', 'time', if_not_exists => TRUE);",
    INSERT: "INSERT INTO elec_measurement (time, device_id, obis_name, value) VALUES %s;",
    TEMPLATE: "(%s, %s, %s, %s)",
    READ: """
        SELECT * FROM elec_measurement 
        WHERE device_id = %s AND
        obis_name = %s AND
        time BETWEEN %s AND %s
        ORDER BY time ASC;
    """
}

MBUS = {
    CREATE: """
    CREATE TABLE IF NOT EXISTS mbus_measurement (
        time TIMESTAMPTZ NOT NULL,
        device_id TEXT NOT NULL,
        mbus_id TEXT NOT NULL,
        mbus_type TEXT,
        value REAL,
        PRIMARY KEY (time, device_id, mbus_id)
    );""",
    HYPER: "SELECT create_hypertable('mbus_measurement', 'time', if_not_exists => TRUE);",
    INSERT: "INSERT INTO mbus_measurement (time, device_id, mbus_id, mbus_type, value) VALUES %s ON CONFLICT DO NOTHING;",
    TEMPLATE: "(%s, %s, %s, %s, %s)",
    READ: """
        SELECT * FROM mbus_measurement 
        WHERE device_id = %s AND
        mbus_id = % AND
        time BETWEEN %s AND %s
        ORDER BY time ASC;
    """
}


PEAK = {
    CREATE: """
    CREATE TABLE IF NOT EXISTS peak_demand (
        time TIMESTAMPTZ NOT NULL,
        device_id TEXT,
        value REAL,
        PRIMARY KEY (time, device_id)
    );""",
    HYPER: "SELECT create_hypertable('peak_demand', 'time', if_not_exists => TRUE);",
    INSERT: "INSERT INTO peak_demand (time, device_id, value) VALUES %s ON CONFLICT DO NOTHING;",
    TEMPLATE: "(%s, %s, %s)",
    READ: """
        SELECT * FROM peak_demand 
        WHERE device_id = %s AND
        time BETWEEN %s AND %s
        ORDER BY time ASC;
    """
}


PEAK_HISTORY = {
    CREATE: """
    CREATE TABLE IF NOT EXISTS peak_demand_history (
        time TIMESTAMPTZ NOT NULL,
        device_id TEXT,
        occurred TIMESTAMPTZ,
        value REAL,
        PRIMARY KEY (time, device_id)
    );""",
    HYPER: "SELECT create_hypertable('peak_demand_history', 'time', if_not_exists => TRUE);",
    INSERT: "INSERT INTO peak_demand_history (time, device_id, occurred, value) VALUES %s ON CONFLICT DO NOTHING;",
    TEMPLATE: "(%s, %s, %s, %s)",
    READ: """
        SELECT * FROM peak_demand_history 
        WHERE device_id = %s AND
        time BETWEEN %s AND %s
        ORDER BY time ASC;
    """
}
