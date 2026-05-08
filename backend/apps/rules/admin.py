from django.contrib import admin

from .models import Rule, RuleAction, RuleCondition, RuleWeatherConstraint


class RuleConditionInline(admin.TabularInline):
    model = RuleCondition
    extra = 1


class RuleActionInline(admin.TabularInline):
    model = RuleAction
    extra = 1


class RuleWeatherConstraintInline(admin.StackedInline):
    model = RuleWeatherConstraint
    extra = 0
    max_num = 1


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("name", "farm", "is_active", "created_by", "created_at")
    list_filter = ("is_active", "farm")
    search_fields = ("name",)
    inlines = [RuleConditionInline, RuleActionInline, RuleWeatherConstraintInline]


@admin.register(RuleCondition)
class RuleConditionAdmin(admin.ModelAdmin):
    list_display = ("rule", "capability_type", "operator", "threshold_value")


@admin.register(RuleAction)
class RuleActionAdmin(admin.ModelAdmin):
    list_display = ("rule", "action_type", "device", "priority")


@admin.register(RuleWeatherConstraint)
class RuleWeatherConstraintAdmin(admin.ModelAdmin):
    list_display = ("rule", "max_rain_probability_pct", "check_hours_ahead")
