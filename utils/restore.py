import argparse
import pathlib
from datetime import datetime
from typing import Any, Optional, cast

import pandas as pd

import p1reader.sinks.db_operations as op
from p1reader.sinks import DBSink, DBSinkConfig


def main() -> None:
    parser = argparse.ArgumentParser(conflict_handler="resolve")
    parser.add_argument("-H", "--hostname", type=str, default="localhost")
    parser.add_argument("-P", "--port", type=str, default=5432)
    parser.add_argument("-D", "--database", type=str, default="premises")
    parser.add_argument("-U", "--user", type=str, default="postgres")
    parser.add_argument("-p", "--password", type=str, default="password")
    parser.add_argument("-i", "--device_id", type=str)
    parser.add_argument("-f", "--input_folder", type=str, default=".")

    args = parser.parse_args()

    HOSTNAME = args.hostname
    PORT = args.port
    DB = args.database
    USER = args.user
    PASSWORD = args.password
    PATH = args.input_folder
    DEVICE_ID = args.device_id

    db_config = DBSinkConfig(
        host=HOSTNAME, port=PORT, database=DB, user=USER, password=PASSWORD
    )

    db = cast(DBSink, db_config.output_stream)
    elec_files = get_file_list(PATH, DEVICE_ID, "elec")
    for elec_file in elec_files:
        save_elec_file(db, elec_file, DEVICE_ID)
    # mbus_files = get_file_list(PATH, DEVICE_ID, "mbus")
    # peak_files = get_file_list(PATH, DEVICE_ID, "peak")
    # peak_history_files = get_file_list(PATH, DEVICE_ID, "peak_history")

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


if __name__ == "__main__":
    main()
