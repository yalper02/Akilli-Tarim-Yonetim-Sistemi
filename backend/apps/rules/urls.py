from django.urls import path

from .views import RuleViewSet

urlpatterns = [
    # Çiftliğe bağlı kural listesi ve oluşturma
    path(
        "farms/<int:farm_id>/rules/",
        RuleViewSet.as_view({"get": "list", "post": "create"}),
        name="farm-rule-list",
    ),
    # Tek kural işlemleri
    path(
        "rules/<int:pk>/",
        RuleViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}),
        name="rule-detail",
    ),
    path(
        "rules/<int:pk>/toggle/",
        RuleViewSet.as_view({"post": "toggle"}),
        name="rule-toggle",
    ),
    path(
        "rules/<int:pk>/test/",
        RuleViewSet.as_view({"post": "test"}),
        name="rule-test",
    ),
]
