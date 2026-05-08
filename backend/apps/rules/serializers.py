from rest_framework import serializers

from .models import Rule, RuleAction, RuleCondition, RuleWeatherConstraint


class RuleConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleCondition
        fields = ["id", "capability_type", "operator", "threshold_value"]
        read_only_fields = ["id"]


class RuleActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleAction
        fields = ["id", "action_type", "device", "parameters", "priority"]
        read_only_fields = ["id"]


class RuleWeatherConstraintSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleWeatherConstraint
        fields = ["id", "max_rain_probability_pct", "check_hours_ahead"]
        read_only_fields = ["id"]


class RuleSerializer(serializers.ModelSerializer):
    conditions = RuleConditionSerializer(many=True)
    actions = RuleActionSerializer(many=True)
    weather_constraint = RuleWeatherConstraintSerializer(
        required=False, allow_null=True, default=None
    )
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Rule
        fields = [
            "id",
            "farm",
            "name",
            "description",
            "is_active",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
            "conditions",
            "actions",
            "weather_constraint",
        ]
        read_only_fields = ["id", "farm", "created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        conditions_data = validated_data.pop("conditions", [])
        actions_data = validated_data.pop("actions", [])
        weather_data = validated_data.pop("weather_constraint", None)

        rule = Rule.objects.create(**validated_data)

        for c in conditions_data:
            RuleCondition.objects.create(rule=rule, **c)
        for a in actions_data:
            RuleAction.objects.create(rule=rule, **a)
        if weather_data:
            RuleWeatherConstraint.objects.create(rule=rule, **weather_data)

        return rule

    def update(self, instance, validated_data):
        conditions_data = validated_data.pop("conditions", None)
        actions_data = validated_data.pop("actions", None)
        # weather_constraint: None keyi yoksa sentinel ile ayırt et
        weather_data = validated_data.pop("weather_constraint", ...)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if conditions_data is not None:
            instance.conditions.all().delete()
            for c in conditions_data:
                RuleCondition.objects.create(rule=instance, **c)

        if actions_data is not None:
            instance.actions.all().delete()
            for a in actions_data:
                RuleAction.objects.create(rule=instance, **a)

        if weather_data is not ...:
            RuleWeatherConstraint.objects.filter(rule=instance).delete()
            if weather_data:
                RuleWeatherConstraint.objects.create(rule=instance, **weather_data)

        return instance
