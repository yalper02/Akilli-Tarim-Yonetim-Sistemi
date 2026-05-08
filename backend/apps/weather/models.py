from django.db import models


class WeatherCache(models.Model):
    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="weather_cache")
    fetched_at = models.DateTimeField(auto_now_add=True)
    forecast_data = models.JSONField()
    valid_until = models.DateTimeField()

    class Meta:
        db_table = "weather_cache"
