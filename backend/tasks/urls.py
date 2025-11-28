from django.urls import path
from .views import analyze_tasks_view, suggest_tasks_view, dependency_graph_view

urlpatterns = [
    path("analyze/", analyze_tasks_view, name="analyze"),
    path("suggest/", suggest_tasks_view, name="suggest"),
    path("dependency-graph/", dependency_graph_view, name="dependency-graph"),
]