from django.db import migrations

HYPERTABLE_SQL = """
-- TimescaleDB requires the partition column (time) to be part of any PRIMARY KEY.
-- Drop Django's default single-column PK and replace with composite (time, id).
ALTER TABLE sensor_readings DROP CONSTRAINT sensor_readings_pkey;
ALTER TABLE sensor_readings ADD PRIMARY KEY (time, id);
SELECT create_hypertable('sensor_readings', 'time', if_not_exists => TRUE, migrate_data => TRUE);

ALTER TABLE device_telemetry DROP CONSTRAINT device_telemetry_pkey;
ALTER TABLE device_telemetry ADD PRIMARY KEY (time, id);
SELECT create_hypertable('device_telemetry', 'time', if_not_exists => TRUE, migrate_data => TRUE);
"""

REVERSE_HYPERTABLE_SQL = """
ALTER TABLE sensor_readings DROP CONSTRAINT sensor_readings_pkey;
ALTER TABLE sensor_readings ADD PRIMARY KEY (id);

ALTER TABLE device_telemetry DROP CONSTRAINT device_telemetry_pkey;
ALTER TABLE device_telemetry ADD PRIMARY KEY (id);
"""

CONTINUOUS_AGGREGATE_SQL = """
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    device_id,
    capability_type,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value
FROM sensor_readings
GROUP BY bucket, device_id, capability_type;
"""

REVERSE_CONTINUOUS_AGGREGATE_SQL = "DROP MATERIALIZED VIEW IF EXISTS sensor_readings_hourly;"


def create_continuous_aggregate(apps, schema_editor):
    # CREATE MATERIALIZED VIEW ... WITH DATA cannot run inside a transaction block.
    # psycopg3 opens an implicit transaction on first statement, so we must switch
    # to autocommit explicitly before running this DDL.
    conn = schema_editor.connection
    conn.set_autocommit(True)
    try:
        with conn.cursor() as cursor:
            cursor.execute(CONTINUOUS_AGGREGATE_SQL)
    finally:
        conn.set_autocommit(False)


def drop_continuous_aggregate(apps, schema_editor):
    conn = schema_editor.connection
    conn.set_autocommit(True)
    try:
        with conn.cursor() as cursor:
            cursor.execute(REVERSE_CONTINUOUS_AGGREGATE_SQL)
    finally:
        conn.set_autocommit(False)


class Migration(migrations.Migration):
    # Hypertable creation steps are transactional; continuous aggregate is not.
    # atomic=False prevents the schema editor from wrapping everything in BEGIN/COMMIT.
    atomic = False

    dependencies = [
        ("sensor_data", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(sql=HYPERTABLE_SQL, reverse_sql=REVERSE_HYPERTABLE_SQL),
        migrations.RunPython(create_continuous_aggregate, reverse_code=drop_continuous_aggregate),
    ]
