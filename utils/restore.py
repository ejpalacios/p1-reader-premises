import argparse
import pathlib
from typing import cast

import pandas as pd

import p1reader.sinks.db_operations as op
from p1reader.sinks import DBSink, DBSinkConfig


def main() -> None:
    parser = argparse.ArgumentParser(
        conflict_handler="resolve", description="Restore CSV files into DB"
    )
    parser.add_argument(
        "-H", "--hostname", type=str, default="localhost", help="DB host"
    )
    parser.add_argument("-P", "--port", type=str, default=5432, help="DB port")
    parser.add_argument(
        "-D", "--database", type=str, default="premises", help="DB name"
    )
    parser.add_argument(
        "-U", "--user", type=str, default="postgres", help="DB username"
    )
    parser.add_argument(
        "-p", "--password", type=str, default="password", help="DB password"
    )

    parser.add_argument("-i", "--device_id", type=str, help="Meter identifier (EAN)")
    parser.add_argument(
        "-f",
        "--input_folder",
        type=str,
        default=".",
        help="Input folder with CSV files",
    )

    parser.add_argument(
        "--all", action=argparse.BooleanOptionalAction, help="Restore all data"
    )
    parser.add_argument(
        "--elec", action=argparse.BooleanOptionalAction, help="Restore electricity data"
    )
    parser.add_argument(
        "--mbus",
        action=argparse.BooleanOptionalAction,
        help="Restore mbus devices data",
    )
    parser.add_argument(
        "--peak",
        action=argparse.BooleanOptionalAction,
        help="Restore peak consumption data",
    )
    parser.add_argument(
        "--peak_history",
        action=argparse.BooleanOptionalAction,
        help="Restore peak consumption history data",
    )
    args = parser.parse_args()

    HOSTNAME = args.hostname
    PORT = args.port
    DB = args.database
    USER = args.user
    PASSWORD = args.password
    PATH = args.input_folder
    DEVICE_ID = args.device_id
    ELEC = args.elec
    MBUS = args.mbus
    PEAK = args.peak
    PEAK_HISTORY = args.peak_history
    if args.all:
        ELEC = True
        MBUS = True
        PEAK = True
        PEAK_HISTORY = True

    db_config = DBSinkConfig(
        host=HOSTNAME, port=PORT, database=DB, user=USER, password=PASSWORD
    )

    db = cast(DBSink, db_config.output_stream)

    # Restore electrical measurements
    if ELEC:
        elec_files = get_file_list(PATH, DEVICE_ID, "elec")
        for elec_file in elec_files:
            save_elec_file(db, elec_file, DEVICE_ID)

    # Restore mbus measurements
    if MBUS:
        mbus_files = get_file_list(PATH, DEVICE_ID, "mbus")
        for mbus_file in mbus_files:
            save_mbus_file(db, mbus_file, DEVICE_ID)

    # Restore peak consumption
    if PEAK:
        peak_files = get_file_list(PATH, DEVICE_ID, "peak")
        for peak_file in peak_files:
            save_peak_file(db, peak_file, DEVICE_ID)

    # Restore peak consumption history
    if PEAK_HISTORY:
        peak_history_files = get_file_list(PATH, DEVICE_ID, "peak_history")
        for peak_history_file in peak_history_files:
            save_peak_history_file(db, peak_history_file, DEVICE_ID)

    db.close()


def get_file_list(base_path: str, device_id: str, type: str) -> list:
    base = pathlib.Path(base_path)
    files = base.glob(f"*-{device_id}-{type}.csv")
    return [file for file in files]


def save_elec_file(db: DBSink, file_path: pathlib.Path, device_id: str) -> None:
    df = pd.read_csv(
        file_path,
        parse_dates=True,
        index_col=0,
    )
    print(f"Saving file {file_path} ...")
    for column in df.columns:
        print(f"Saving measurement {column} ...")
        index = df.index
        values = df[column].values
        measurements = [
            (dt, device_id, column, value) for dt, value in zip(index, values)
        ]
        db.insert_sql(measurements, op.ELEC)


def save_mbus_file(db: DBSink, file_path: pathlib.Path, device_id: str) -> None:
    df = pd.read_csv(
        file_path,
        parse_dates=True,
        index_col=0,
    )
    print(f"Saving file {file_path} ...")
    for column in df.columns:
        print(f"Saving measurement {column} ...")
        index = df.index
        values = df[column].values
        measurements = [
            (dt, device_id, column, value) for dt, value in zip(index, values)
        ]
        db.insert_sql(measurements, op.MBUS)


def save_peak_file(db: DBSink, file_path: pathlib.Path, device_id: str) -> None:
    df = pd.read_csv(
        file_path,
        parse_dates=True,
        index_col=0,
    )
    print(f"Saving file {file_path} ...")
    index = df.index
    values = df["Default"].values
    measurements = [(dt, device_id, value) for dt, value in zip(index, values)]
    db.insert_sql(measurements, op.PEAK)


def save_peak_history_file(db: DBSink, file_path: pathlib.Path, device_id: str) -> None:
    df = pd.read_csv(
        file_path,
        parse_dates=True,
        index_col=0,
    )
    print(f"Saving file {file_path} ...")
    index = df.index
    values = df["Default"].values
    measurements = [(dt, device_id, dt, value) for dt, value in zip(index, values)]
    db.insert_sql(measurements, op.PEAK_HISTORY)


if __name__ == "__main__":
    main()
