from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import FarmMembership, Role, User
from apps.devices.models import Device, DeviceCapability
from apps.farms.models import Crop, Farm

CROPS = [
    {
        "name": "Domates",
        "scientific_name": "Solanum lycopersicum",
        "optimal_soil_moisture_min": 60.0,
        "optimal_soil_moisture_max": 80.0,
        "optimal_temperature_min": 18.0,
        "optimal_temperature_max": 27.0,
        "irrigation_water_need_mm_per_day": 6.0,
        "optimal_ph_min": 6.0,
        "optimal_ph_max": 6.8,
        "nitrogen_need_ppm": 150.0,
        "phosphorus_need_ppm": 40.0,
        "potassium_need_ppm": 200.0,
        "frost_sensitivity": "high",
    },
    {
        "name": "Buğday",
        "scientific_name": "Triticum aestivum",
        "optimal_soil_moisture_min": 40.0,
        "optimal_soil_moisture_max": 65.0,
        "optimal_temperature_min": 15.0,
        "optimal_temperature_max": 24.0,
        "irrigation_water_need_mm_per_day": 4.0,
        "optimal_ph_min": 6.0,
        "optimal_ph_max": 7.0,
        "nitrogen_need_ppm": 120.0,
        "phosphorus_need_ppm": 25.0,
        "potassium_need_ppm": 150.0,
        "frost_sensitivity": "low",
    },
    {
        "name": "Marul",
        "scientific_name": "Lactuca sativa",
        "optimal_soil_moisture_min": 60.0,
        "optimal_soil_moisture_max": 75.0,
        "optimal_temperature_min": 15.0,
        "optimal_temperature_max": 22.0,
        "irrigation_water_need_mm_per_day": 3.0,
        "optimal_ph_min": 6.0,
        "optimal_ph_max": 7.0,
        "nitrogen_need_ppm": 100.0,
        "phosphorus_need_ppm": 30.0,
        "potassium_need_ppm": 150.0,
        "frost_sensitivity": "medium",
    },
]

SENSOR_CAPABILITIES = [
    {"capability_type": "soil_moisture", "unit": "%", "min_value": 0.0, "max_value": 100.0},
    {"capability_type": "temperature", "unit": "°C", "min_value": -50.0, "max_value": 80.0},
    {"capability_type": "humidity", "unit": "%", "min_value": 0.0, "max_value": 100.0},
    {"capability_type": "ph_level", "unit": "pH", "min_value": 0.0, "max_value": 14.0},
    {"capability_type": "nitrogen_level", "unit": "ppm", "min_value": 0.0, "max_value": 1000.0},
    {"capability_type": "phosphorus_level", "unit": "ppm", "min_value": 0.0, "max_value": 500.0},
    {"capability_type": "potassium_level", "unit": "ppm", "min_value": 0.0, "max_value": 1000.0},
]


class Command(BaseCommand):
    help = "Seed the database with demo data for development and jury presentation."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing seed data before re-creating it.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset()

        roles = self._create_roles()
        admin = self._create_admin()
        farmer = self._create_farmer()
        crops = self._create_crops()
        farms = self._create_farms(admin, crops)
        self._create_memberships(admin, farmer, farms, roles)
        self._create_devices(farms)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
        self.stdout.write("  Admin login: admin / admin1234")
        self.stdout.write("  Farmer login: farmer1 / farmer1234")

    # ------------------------------------------------------------------

    def _reset(self):
        self.stdout.write("Resetting seed data...")
        Device.objects.filter(device_uid__startswith="seed-").delete()
        Farm.objects.filter(name__in=["Akdeniz Çiftliği", "Ege Tarlaları"]).delete()
        Crop.objects.filter(name__in=["Domates", "Buğday", "Marul"]).delete()
        User.objects.filter(username__in=["admin", "farmer1"]).delete()

    def _create_roles(self):
        roles = {}
        for name, _ in Role.ROLE_CHOICES:
            role, _ = Role.objects.get_or_create(name=name)
            roles[name] = role
        self.stdout.write(f"  Roles: {list(roles.keys())}")
        return roles

    def _create_admin(self):
        if User.objects.filter(username="admin").exists():
            self.stdout.write("  Admin user already exists, skipping.")
            return User.objects.get(username="admin")
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@akilli-tarim.local",
            password="admin1234",
            first_name="Sistem",
            last_name="Yöneticisi",
        )
        self.stdout.write("  Created admin user.")
        return admin

    def _create_farmer(self):
        if User.objects.filter(username="farmer1").exists():
            self.stdout.write("  Farmer user already exists, skipping.")
            return User.objects.get(username="farmer1")
        farmer = User.objects.create_user(
            username="farmer1",
            email="farmer1@akilli-tarim.local",
            password="farmer1234",
            first_name="Ali",
            last_name="Yılmaz",
        )
        self.stdout.write("  Created farmer user.")
        return farmer

    def _create_crops(self):
        crops = []
        for data in CROPS:
            crop, created = Crop.objects.get_or_create(name=data["name"], defaults=data)
            crops.append(crop)
            if created:
                self.stdout.write(f"  Created crop: {crop.name}")
        return crops  # [domates, bugday, marul]

    def _create_farms(self, owner, crops):
        domates, bugday, _ = crops

        farm1, created1 = Farm.objects.get_or_create(
            name="Akdeniz Çiftliği",
            defaults={
                "location": "Antalya, Türkiye",
                "latitude": 36.8969,
                "longitude": 30.7133,
                "area_hectares": 12.5,
                "crop": domates,
                "owner": owner,
            },
        )
        if created1:
            self.stdout.write(f"  Created farm: {farm1.name}")

        farm2, created2 = Farm.objects.get_or_create(
            name="Ege Tarlaları",
            defaults={
                "location": "İzmir, Türkiye",
                "latitude": 38.4192,
                "longitude": 27.1287,
                "area_hectares": 25.0,
                "crop": bugday,
                "owner": owner,
            },
        )
        if created2:
            self.stdout.write(f"  Created farm: {farm2.name}")

        return [farm1, farm2]

    def _create_memberships(self, admin, farmer, farms, roles):
        farm1, farm2 = farms
        entries = [
            (admin, farm1, roles[Role.FARM_MANAGER]),
            (admin, farm2, roles[Role.FARM_MANAGER]),
            (farmer, farm1, roles[Role.FARMER]),
        ]
        for user, farm, role in entries:
            _, created = FarmMembership.objects.get_or_create(
                user=user, farm=farm, defaults={"role": role}
            )
            if created:
                self.stdout.write(f"  Membership: {user.username} -> {farm.name} ({role.name})")

    def _create_devices(self, farms):
        farm1, farm2 = farms

        device_specs = [
            # farm, uid, name, type, capabilities
            (
                farm1,
                "seed-sensor-001",
                "Toprak Sensörü 1 (F1)",
                Device.COMBINED,
                SENSOR_CAPABILITIES,
            ),
            (
                farm1,
                "seed-sensor-002",
                "Toprak Sensörü 2 (F1)",
                Device.SENSOR,
                [
                    c
                    for c in SENSOR_CAPABILITIES
                    if c["capability_type"] in ("soil_moisture", "temperature")
                ],
            ),
            (
                farm1,
                "seed-valve-001",
                "Sulama Vanası 1 (F1)",
                Device.ACTUATOR,
                [
                    {
                        "capability_type": "valve_control",
                        "unit": "",
                        "min_value": 0.0,
                        "max_value": 1.0,
                    }
                ],
            ),
            (
                farm2,
                "seed-sensor-003",
                "Toprak Sensörü 1 (F2)",
                Device.COMBINED,
                SENSOR_CAPABILITIES,
            ),
            (
                farm2,
                "seed-sensor-004",
                "Toprak Sensörü 2 (F2)",
                Device.SENSOR,
                [
                    c
                    for c in SENSOR_CAPABILITIES
                    if c["capability_type"] in ("soil_moisture", "temperature", "humidity")
                ],
            ),
        ]

        for farm, uid, name, dtype, capabilities in device_specs:
            device, created = Device.objects.get_or_create(
                device_uid=uid,
                defaults={
                    "farm": farm,
                    "name": name,
                    "device_type": dtype,
                    "mqtt_username": uid,
                },
            )
            if created:
                for cap in capabilities:
                    DeviceCapability.objects.get_or_create(
                        device=device, capability_type=cap["capability_type"], defaults=cap
                    )
                self.stdout.write(
                    f"  Created device: {device.name} ({len(capabilities)} capabilities)"
                )
