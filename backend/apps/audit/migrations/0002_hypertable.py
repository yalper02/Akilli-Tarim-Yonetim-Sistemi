from django.db import migrations

FORWARD_SQL = """
-- TimescaleDB requires the partition column (time) to be part of any PRIMARY KEY.
ALTER TABLE audit_logs DROP CONSTRAINT audit_logs_pkey;
ALTER TABLE audit_logs ADD PRIMARY KEY (time, id);
SELECT create_hypertable('audit_logs', 'time', if_not_exists => TRUE, migrate_data => TRUE);

-- Automatically drop audit chunks older than 2 years.
SELECT add_retention_policy('audit_logs', INTERVAL '2 years');
"""

REVERSE_SQL = """
SELECT remove_retention_policy('audit_logs', if_exists => TRUE);

ALTER TABLE audit_logs DROP CONSTRAINT audit_logs_pkey;
ALTER TABLE audit_logs ADD PRIMARY KEY (id);
"""


class Migration(migrations.Migration):
    # add_retention_policy cannot run inside a transaction block
    atomic = False

    dependencies = [
        ("audit", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(sql=FORWARD_SQL, reverse_sql=REVERSE_SQL),
    ]
