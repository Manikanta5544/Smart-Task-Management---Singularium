from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .scoring import (
    analyze_dependency_graph,
    analyze_tasks,
    get_top_recommendations,
    detect_circular_dependencies
)

@csrf_exempt
@require_http_methods(["POST"])
def analyze_tasks_view(request):
    try:
        data = json.loads(request.body)
        tasks = data.get('tasks', [])
        strategy = data.get('strategy', 'smart_balance')

        if not isinstance(tasks, list):
            return JsonResponse({"error": "Tasks must be a list"}, status=400)

        if not tasks:
            return JsonResponse({"error": "No tasks provided"}, status=400)

        for task in tasks:
            if 'id' not in task or 'title' not in task:
                return JsonResponse({"error": "Each task must have id and title"}, status=400)
            if not isinstance(task.get('dependencies', []), list):
                return JsonResponse({"error": "Dependencies must be a list"}, status=400)

        has_cycle, cycles = detect_circular_dependencies(tasks)
        if has_cycle:
            return JsonResponse({"error": "Circular dependencies detected", "cycles": cycles}, status=400)

        analyzed = analyze_tasks(tasks, strategy)

        return JsonResponse({
            "strategy": strategy,
            "tasks": analyzed,
            "total_tasks": len(analyzed)
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Processing error: {str(e)}"}, status=500)

@require_http_methods(["GET"])
def suggest_tasks_view(request):
    try:
        tasks_json = request.GET.get('tasks')
        strategy = request.GET.get('strategy', 'smart_balance')
        limit = min(int(request.GET.get('limit', 3)), 10)

        if not tasks_json:
            return JsonResponse({"error": "Tasks parameter required"}, status=400)

        tasks = json.loads(tasks_json)

        if not isinstance(tasks, list):
            return JsonResponse({"error": "Tasks must be a list"}, status=400)

        has_cycle, cycles = detect_circular_dependencies(tasks)
        if has_cycle:
            return JsonResponse({"error": "Circular dependencies detected", "cycles": cycles}, status=400)

        result = get_top_recommendations(tasks, strategy, limit)

        return JsonResponse({
            "strategy": strategy,
            "recommendations": result['recommendations'],
            "total_considered": len(tasks)
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid tasks JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Processing error: {str(e)}"}, status=500)

@require_http_methods(["GET", "POST"])
def dependency_graph_view(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            tasks = data.get('tasks', [])
        else:
            tasks_json = request.GET.get('tasks')
            if not tasks_json:
                return JsonResponse({"error": "Tasks parameter required"}, status=400)
            tasks = json.loads(tasks_json)

        if not isinstance(tasks, list):
            return JsonResponse({"error": "Tasks must be a list"}, status=400)

        for task in tasks:
            if 'id' not in task or 'title' not in task:
                return JsonResponse({"error": "Each task must have id and title"}, status=400)
            if not isinstance(task.get('dependencies', []), list):
                return JsonResponse({"error": "Dependencies must be a list"}, status=400)

        graph = analyze_dependency_graph(tasks)

        return JsonResponse({
            "success": True,
            "graph": graph,
            "total_tasks": len(tasks)
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Processing error: {str(e)}"}, status=500)
