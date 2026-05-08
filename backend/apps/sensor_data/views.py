from django.db import connection
from django.db.models import Max
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SensorReading
from .serializers import SensorReadingSerializer, TimeseriesPointSerializer

# time_bucket aralık haritası — SQL injection'a karşı whitelist
_BUCKET_MAP = {
    "minute": "1 minute",
    "hour": "1 hour",
    "day": "1 day",
    "week": "1 week",
}


class SensorDataViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SensorReadingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["device", "capability_type"]
    ordering = ["-time"]

    def get_queryset(self):
        qs = (
            SensorReading.objects.select_related("device")
            .filter(device__farm__memberships__user=self.request.user)
            .distinct()
        )

        params = self.request.query_params
        if params.get("device_id"):
            qs = qs.filter(device_id=params["device_id"])
        if params.get("capability"):
            qs = qs.filter(capability_type=params["capability"])
        if params.get("start"):
            qs = qs.filter(time__gte=params["start"])
        if params.get("end"):
            qs = qs.filter(time__lte=params["end"])
        return qs

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """Her (device, capability_type) çifti için en son okumayı döndür."""
        qs = self.get_queryset()
        latest_times = qs.values("device", "capability_type").annotate(latest=Max("time"))
        result = []
        for entry in latest_times:
            reading = qs.filter(
                device=entry["device"],
                capability_type=entry["capability_type"],
                time=entry["latest"],
            ).first()
            if reading:
                result.append(reading)
        return Response(SensorReadingSerializer(result, many=True).data)

    @action(detail=False, methods=["get"])
    def timeseries(self, request):
        """TimescaleDB time_bucket ile zaman serisi döndür."""
        aggregation = request.query_params.get("aggregation", "hour")
        if aggregation not in _BUCKET_MAP:
            return Response(
                {
                    "detail": "Geçersiz aggregation değeri. Seçenekler: minute, hour, day, week",
                    "code": "invalid_aggregation",
                },
                status=400,
            )

        bucket_interval = _BUCKET_MAP[aggregation]
        where_clauses = [
            "sr.device_id IN ("
            "  SELECT d.id FROM devices d"
            "  JOIN farm_memberships fm ON fm.farm_id = d.farm_id"
            "  WHERE fm.user_id = %s"
            ")"
        ]
        params = [request.user.id]

        p = request.query_params
        if p.get("device_id"):
            where_clauses.append("sr.device_id = %s")
            params.append(p["device_id"])
        if p.get("capability"):
            where_clauses.append("sr.capability_type = %s")
            params.append(p["capability"])
        if p.get("start"):
            where_clauses.append("sr.time >= %s")
            params.append(p["start"])
        if p.get("end"):
            where_clauses.append("sr.time <= %s")
            params.append(p["end"])

        where_sql = " AND ".join(where_clauses)
        sql = f"""
            SELECT
                time_bucket('{bucket_interval}', sr.time) AS bucket,
                sr.device_id,
                sr.capability_type,
                AVG(sr.value)  AS avg_value,
                MIN(sr.value)  AS min_value,
                MAX(sr.value)  AS max_value
            FROM sensor_readings sr
            WHERE {where_sql}
            GROUP BY bucket, sr.device_id, sr.capability_type
            ORDER BY bucket DESC
            LIMIT 1000
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(TimeseriesPointSerializer(rows, many=True).data)
