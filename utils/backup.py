import argparse
from datetime import datetime, timedelta
from typing import cast

import pandas as pd

import p1reader.sinks.db_operations as op
from p1reader.sinks import DBSink, DBSinkConfig


def main() -> None:
    parser = argparse.ArgumentParser(
        conflict_handler="resolve", description="Back up from DB"
    )
    parser.add_argument("-H", "--hostname", type=str, default="localhost")
    parser.add_argument("-P", "--port", type=str, default=5432)
    parser.add_argument("-D", "--database", type=str, default="premises")
    parser.add_argument("-U", "--user", type=str, default="postgres")
    parser.add_argument("-p", "--password", type=str, default="password")
    parser.add_argument("-i", "--device_id", type=str)
    parser.add_argument("-s", "--start", type=str, default=None)
    parser.add_argument("-e", "--end", type=str, default=None)
    parser.add_argument("-o", "--output_path", type=str, default=".")
    args = parser.parse_args()

    HOSTNAME = args.hostname
    PORT = args.port
    DB = args.database
    USER = args.user
    PASSWORD = args.password
    PATH = args.output_path
    DEVICE_ID = args.device_id
    START = args.start
    END = args.end

    db_config = DBSinkConfig(
        host=HOSTNAME, port=PORT, database=DB, user=USER, password=PASSWORD
    )

    db = cast(DBSink, db_config.output_stream)

    ids = db.query_meter_ids()
    if DEVICE_ID not in ids:
        raise ValueError(f"{DEVICE_ID=} not found in {ids=}")

    START_DATE, END_DATE = db.query_date_range(DEVICE_ID)
    if START is not None:
        START_DATE = datetime.fromisoformat(START)
    if END is not None:
        END_DATE = datetime.fromisoformat(END)

    if START_DATE is not None and END_DATE is not None:
        print(f"{START_DATE.isoformat()}, {END_DATE.isoformat()}")
    else:
        raise ValueError("No data found in database")

    measurements = get_measurements_list(db.query_n_phases(DEVICE_ID))

    date_pointer = START_DATE
    while date_pointer < END_DATE:
        start_slice = START_DATE
        end_slice = START_DATE + timedelta(days=30)
        print(f"{start_slice.isoformat()}, {end_slice.isoformat()}")

        # Backup electrical measurements
        results = db.query_sql(DEVICE_ID, start_slice, end_slice, op.ELEC, measurements)
        df_elec = dict_to_df(results, 3)
        write_csv(df_elec, "elec", PATH, DEVICE_ID, start_slice, end_slice)

        # Backup mbus measurements
        mbus_ids = db.query_mbus_ids(DEVICE_ID)
        if len(mbus_ids) != 0:
            results = db.query_sql(DEVICE_ID, start_slice, end_slice, op.MBUS, mbus_ids)
            df_mbus = dict_to_df(results, 4)
            write_csv(df_mbus, "mbus", PATH, DEVICE_ID, start_slice, end_slice)

        date_pointer += timedelta(days=30)

    # Backup peak demand
    results = db.query_sql(DEVICE_ID, START_DATE, END_DATE, op.PEAK)
    df_peak = dict_to_df(results, 2)
    write_csv(df_peak, "peak", PATH, DEVICE_ID, START_DATE, END_DATE)

    # Backup peak demand history
    results = db.query_sql(DEVICE_ID, START_DATE, END_DATE, op.PEAK_HISTORY)
    df_peak_his = dict_to_df(results, 3)
    write_csv(df_peak_his, "peak_history", PATH, DEVICE_ID, START_DATE, END_DATE)

    value = input("Backup Completed. Would you like to deleted all data [N/y]: ")
    if value.lower().strip() == "y":
        value_confirm = input("This operation cannot be reversed are you sure [N/y]")
        if value_confirm.lower().strip() == "y":
            db.delete_sql(DEVICE_ID, START_DATE, END_DATE, op.ELEC)
            db.delete_sql(DEVICE_ID, START_DATE, END_DATE, op.MBUS)
            db.delete_sql(DEVICE_ID, START_DATE, END_DATE, op.PEAK)
            db.delete_sql(DEVICE_ID, START_DATE, END_DATE, op.PEAK_HISTORY)

    db.close()


def dict_to_df(results: dict, index_value: int, index_time: int = 0) -> pd.DataFrame:
    df = pd.DataFrame()
    for measure, values in results.items():
        readings = [value[index_value] for value in values]
        indexes = [value[index_time] for value in values]
        df_temp = pd.DataFrame(index=indexes, data=readings, columns=[measure])
        df = pd.concat([df, df_temp], axis=1)
    return df


def get_measurements_list(phases: int) -> list[str]:
    entries_phases = {
        1: [
            "U(L1)",
            "I(L1)",
            "P-",
            "P+",
        ],
        3: [
            "U(L1)",
            "U(L2)",
            "U(L3)",
            "I(L1)",
            "I(L2)",
            "I(L3)",
            "P+(L1)",
            "P+(L2)",
            "P+(L3)",
            "P-(L1)",
            "P-(L2)",
            "P-(L3)",
            "P-",
            "P+",
        ],
    }
    return entries_phases[phases]


def write_csv(
    df: pd.DataFrame,
    type_measurements: str,
    path: str,
    device_id: str,
    start_date: datetime,
    end_date: datetime,
) -> None:
    start_date_str = start_date.strftime("%Y_%m_%d_%H_%M_%S")
    end_date_str = end_date.strftime("%Y_%m_%d_%H_%M_%S")

    name = f"{path}/{start_date_str}-{end_date_str}-{device_id}-{type_measurements}.csv"
    print(f"Writing CSV file {name=}")
    df.to_csv(name)


if __name__ == "__main__":
    main()
