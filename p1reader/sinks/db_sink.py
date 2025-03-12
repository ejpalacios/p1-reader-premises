import logging
from datetime import datetime
from typing import Optional

import psycopg
from dsmr_parser import obis_references
from dsmr_parser.objects import Telegram
from psycopg_pool import ConnectionPool

import p1reader.sinks.db_operations as op
from p1reader.sinks.config import (
    ELECTRICITY_MEASUREMENTS,
    MAXIMUM_MEASUREMENTS_HISTORY,
    MAXIMUM_MEASUREMENTS_ON_GOING,
    MBUS_MEASUREMENTS,
)
from p1reader.sinks.data_sink import DataSink, DataSinkConfig

LOGGER = logging.getLogger(__name__)


class DBSinkConfig(DataSinkConfig):
    host: str
    port: int = 5432
    database: str = "premises"
    user: str = "postgres"
    password: str = "password"

    @property
    def output_stream(self) -> DataSink:
        return DBSink(
            f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode=allow"
        )


class DBSink(DataSink):
    _pool: ConnectionPool

    def __init__(self, connection_uri: Optional[str] = None) -> None:
        if connection_uri:
            print(connection_uri)
            DBSink._pool = ConnectionPool(
                conninfo=connection_uri,
                open=True,
                check=ConnectionPool.check_connection,
            )
            self.create_tables()
        else:
            raise ValueError("Connection URI has not been set yet")

    @classmethod
    def close(cls) -> None:
        if cls._pool is not None:
            cls._pool.close()

    @classmethod
    def create_tables(cls) -> None:
        cls.create_table_sql(op.ELEC)
        cls.create_table_sql(op.MBUS)
        cls.create_table_sql(op.PEAK)
        cls.create_table_sql(op.PEAK_HISTORY)

    @classmethod
    def create_table_sql(cls, sql_collection: dict) -> None:
        with cls._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_collection[op.CREATE])
                cur.execute(sql_collection[op.HYPER])

    @classmethod
    def insert_sql(cls, measurements: list, sql_collection: dict) -> None:
        try:
            with cls._pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.executemany(
                        sql_collection[op.INSERT],
                        measurements,
                    )
        except psycopg.Error as e:
            LOGGER.warning(f"Failed to insert rows.\n ERROR: {e}")

    @classmethod
    def query_sql(
        cls,
        device_id: str,
        start_date: datetime,
        end_date: datetime,
        sql_collection: dict,
        measurements: Optional[list] = None,
    ) -> dict:
        values: dict = dict()
        with cls._pool.connection() as conn:
            with conn.cursor() as cur:
                if measurements is not None:
                    for measure in measurements:
                        values[measure] = []
                        cur.execute(
                            sql_collection[op.READ],
                            (device_id, measure, start_date, end_date),
                        )
                        values[measure] = cur.fetchall()
                else:
                    cur.execute(
                        sql_collection[op.READ],
                        (device_id, start_date, end_date),
                    )
                    values["Default"] = cur.fetchall()
        return values

    @classmethod
    def delete_sql(
        cls,
        device_id: str,
        start_date: datetime,
        end_date: datetime,
        sql_collection: dict,
    ) -> dict:
        values: dict = dict()
        with cls._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql_collection[op.DELETE],
                    (device_id, start_date, end_date),
                )
        return values

    @classmethod
    def query_meter_ids(cls) -> list:
        query_ids = """
            SELECT DISTINCT(device_id) FROM elec_measurement LIMIT 1000;
        """
        ids = []
        with cls._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query_ids)
                result = cur.fetchall()
                for id_i in result:
                    ids.append(id_i[0])
        return ids

    @classmethod
    def query_mbus_ids(cls, device_id: str) -> list:
        query_ids = """
            SELECT DISTINCT(mbus_id) FROM mbus_measurement WHERE device_id = %s ;
        """
        ids = []
        with cls._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query_ids, [device_id])
                result = cur.fetchall()
                for id_i in result:
                    ids.append(id_i[0])
        return ids

    @classmethod
    def query_date_range(
        cls, device_id: str
    ) -> tuple[Optional[datetime], Optional[datetime]]:
        query_range = """
            SELECT min(time), max(time) FROM elec_measurement WHERE device_id = %s;
        """
        start_date: Optional[datetime]
        end_date: Optional[datetime]
        with cls._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query_range, [device_id])
                result = cur.fetchall()
                start_date = result[0][0]
                end_date = result[0][1]
        return start_date, end_date

    @classmethod
    def query_n_phases(cls, device_id: str) -> int:
        query_phase = """
            SELECT * FROM elec_measurement
            WHERE device_id = %s AND obis_name = 'P+(L3)' LIMIT 10;
        """
        phases = 1
        with cls._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query_phase, [device_id])
                result = cur.fetchall()
                if len(result) != 0:
                    phases = 3
        return phases

    @classmethod
    def process_telegram(cls, telegram: Telegram) -> None:
        elec = []
        mbus = []
        peak = []
        peak_history = []

        dt = telegram.P1_MESSAGE_TIMESTAMP.value
        device_id = bytearray.fromhex(
            telegram[obis_references.BELGIUM_EQUIPMENT_IDENTIFIER].value
        ).decode()
        for name, val in telegram:
            if name in ELECTRICITY_MEASUREMENTS.keys():
                elec.append(
                    (dt, device_id, ELECTRICITY_MEASUREMENTS[name], float(val.value))
                )
            elif name in MBUS_MEASUREMENTS:
                for device in val:
                    print(device)
                    mbus_id = bytearray.fromhex(
                        getattr(device, "MBUS_EQUIPMENT_IDENTIFIER").value
                    ).decode()
                    reading = getattr(device, "MBUS_METER_READING")
                    mbus.append(
                        (
                            reading.datetime,
                            device_id,
                            mbus_id,
                            float(reading.value),
                        )
                    )
            elif name in MAXIMUM_MEASUREMENTS_ON_GOING:
                if val.datetime is not None:
                    peak.append(
                        (
                            val.datetime,
                            device_id,
                            float(val.value),
                        )
                    )
            elif name in MAXIMUM_MEASUREMENTS_HISTORY:
                for entry in val:
                    if entry.datetime is not None:
                        peak_history.append(
                            (
                                entry.datetime,
                                device_id,
                                entry.occurred,
                                float(entry.value),
                            )
                        )
        cls.insert_sql(elec, op.ELEC)
        cls.insert_sql(mbus, op.MBUS)
        cls.insert_sql(peak, op.PEAK)
        cls.insert_sql(peak_history, op.PEAK_HISTORY)
