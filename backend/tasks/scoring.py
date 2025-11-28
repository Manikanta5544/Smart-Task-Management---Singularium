from datetime import datetime, date
from typing import List, Dict, Tuple
import math
from collections import defaultdict

STRATEGIES = {
    "smart_balance": {"urgency": 0.35, "importance": 0.35, "effort": 0.15, "dependency": 0.15},
    "fastest_wins": {"urgency": 0.10, "importance": 0.20, "effort": 0.60, "dependency": 0.10},
    "high_impact": {"urgency": 0.15, "importance": 0.60, "effort": 0.05, "dependency": 0.20},
    "deadline_driven": {"urgency": 0.60, "importance": 0.20, "effort": 0.10, "dependency": 0.10},
}

def detect_circular_dependencies(tasks: List[Dict]) -> Tuple[bool, List[List[str]]]:
    graph = {task['id']: set(task.get('dependencies', [])) for task in tasks}
    visited = set()
    active = set()
    cycles = []

    def dfs(node, path):
        if node in active:
            start = path.index(node)
            cycles.append(path[start:] + [node])
            return
        if node in visited:
            return

        visited.add(node)
        active.add(node)

        for nxt in graph.get(node, []):
            if nxt in graph:
                dfs(nxt, path + [nxt])

        active.remove(node)

    for node in graph:
        if node not in visited:
            dfs(node, [node])

    return len(cycles) > 0, cycles

def calculate_task_score(task: Dict, weights: Dict, blocking_counts: Dict, max_blockers: int) -> Dict:
    today = date.today()

    due_date = task.get('due_date')

    try:
        importance_val = int(task.get('importance')) if task.get('importance') is not None else 5
    except:
        importance_val = 5
    importance = max(1, min(10, importance_val))

    try:
        hours_val = float(task.get('estimated_hours')) if task.get('estimated_hours') is not None else 4.0
    except:
        hours_val = 4.0
    estimated_hours = max(0.5, hours_val)

    urgency_score = 0.1
    urgency_details = ""

    if due_date:
        try:
            due = datetime.strptime(due_date, '%Y-%m-%d').date()
            days_diff = (due - today).days
            if days_diff >= 0:
                urgency_score = math.exp(-days_diff / 7)
                urgency_details = f"Due in {days_diff} days"
            else:
                urgency_score = min(1.2, 1.0 + abs(days_diff) * 0.05)
                urgency_details = f"Overdue by {abs(days_diff)} days"
        except:
            urgency_details = "Invalid date"

    importance_score = (importance / 10.0) ** 0.9

    effort_score = 1.0 / (math.sqrt(estimated_hours) + 1.0)

    blocking_count = blocking_counts.get(task['id'], 0)
    dependency_score = math.log(1 + (blocking_count / max(1, max_blockers)) * 5) / math.log(6)

    weighted_score = (
        urgency_score * weights['urgency'] +
        importance_score * weights['importance'] +
        effort_score * weights['effort'] +
        dependency_score * weights['dependency']
    )

    priority_score = min(100, max(0, round(weighted_score * 100, 2)))

    explanation_parts = []
    if urgency_details:
        explanation_parts.append(urgency_details)
    explanation_parts.append(f"Importance: {importance}/10")
    explanation_parts.append(f"Effort: {estimated_hours}h")
    if blocking_count > 0:
        explanation_parts.append(f"Blocks {blocking_count} tasks")

    return {
        'priority_score': priority_score,
        'explanation': ' | '.join(explanation_parts),
        'urgency_score': round(urgency_score, 3),
        'importance_score': round(importance_score, 3),
        'effort_score': round(effort_score, 3),
        'dependency_score': round(dependency_score, 3)
    }

def analyze_tasks(tasks: List[Dict], strategy: str = "smart_balance") -> List[Dict]:
    if not tasks:
        return []

    if strategy not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy}")

    valid_tasks = []
    for task in tasks:
        if not task.get('id'):
            continue
        if not task.get('title'):
            task['title'] = f"Untitled Task {task['id']}"
        valid_tasks.append(task)

    if not valid_tasks:
        return []

    weights = STRATEGIES[strategy]

    blocking_counts = defaultdict(int)
    for task in valid_tasks:
        for dep in task.get('dependencies', []):
            blocking_counts[dep] += 1

    max_blockers = max(blocking_counts.values()) if blocking_counts else 1

    scored_tasks = []
    for task in valid_tasks:
        score_data = calculate_task_score(task, weights, blocking_counts, max_blockers)
        scored_tasks.append({**task, **score_data})

    def safe_due_date(d):
        if not d:
            return date.max
        try:
            return datetime.strptime(d, '%Y-%m-%d').date()
        except:
            return date.max

    scored_tasks.sort(key=lambda x: (-x['priority_score'], safe_due_date(x.get('due_date'))))
    return scored_tasks

def get_top_recommendations(tasks: List[Dict], strategy: str = "smart_balance", limit: int = 3):
    analyzed_tasks = analyze_tasks(tasks, strategy)

    recommendations = []
    for i, task in enumerate(analyzed_tasks[:limit], 1):
        reasoning = generate_recommendation_reasoning(task, i)
        recommendations.append({
            'rank': i,
            'task': {
                'id': task['id'],
                'title': task['title'],
                'priority_score': task['priority_score'],
                'due_date': task.get('due_date'),
                'estimated_hours': task.get('estimated_hours'),
                'importance': task.get('importance')
            },
            'explanation': task['explanation'],
            'reasoning': reasoning
        })

    return {
        'recommendations': recommendations,
        'strategy_used': strategy,
        'total_tasks_analyzed': len(analyzed_tasks),
        'timestamp': datetime.now().isoformat()
    }

def generate_recommendation_reasoning(task: Dict, rank: int) -> str:
    factors = []
    if task['urgency_score'] > 0.8:
        factors.append("High urgency")
    elif task['urgency_score'] > 0.6:
        factors.append("Approaching deadline")
    if task['importance_score'] > 0.8:
        factors.append("Critical importance")
    elif task['importance_score'] > 0.6:
        factors.append("High impact")
    if task['effort_score'] > 0.7:
        factors.append("Quick win")
    if task['dependency_score'] > 0.5:
        factors.append("Blocks other work")
    if not factors:
        factors.append("Well-balanced")
    return f"Rank #{rank} - Score: {task['priority_score']}/100. Key factors: {', '.join(factors)}"

def validate_task_data(task: Dict) -> Tuple[bool, str]:
    if not task.get('id'):
        return False, "Task missing 'id'"
    if not task.get('title'):
        return False, "Task missing 'title'"
    return True, "Valid"

def analyze_dependency_graph(tasks):
    graph = {task['id']: set(task.get('dependencies', [])) for task in tasks}
    reverse_graph = defaultdict(set)

    for t, deps in graph.items():
        for d in deps:
            if d in graph:
                reverse_graph[d].add(t)

    blocking_counts = {task_id: len(reverse_graph.get(task_id, set())) for task_id in graph}

    strongly_connected = _find_strongly_connected_components(graph)

    return {
        'nodes': [
            {
                'id': task_id,
                'label': next((t['title'] for t in tasks if t['id'] == task_id), task_id),
                'group': _get_node_group(task_id, graph, reverse_graph, blocking_counts),
                'value': blocking_counts[task_id] + 1,
                'title': f"Blocks {blocking_counts[task_id]} tasks"
            }
            for task_id in graph
        ],
        'edges': [
            {
                'from': dep,
                'to': task,
                'arrows': 'to',
                'color': {'color': '#e63946'} if _is_circular_edge(task, dep, strongly_connected)
                        else {'color': '#2B7CE9'}
            }
            for task, deps in graph.items()
            for dep in deps
            if dep in graph
        ],
        'analysis': {
            'total_tasks': len(graph),
            'total_dependencies': sum(len(deps) for deps in graph.values()),
            'critical_tasks': [t for t, c in blocking_counts.items() if c >= 3],
            'independent_tasks': [t for t in graph if not graph[t] and not reverse_graph.get(t)],
            'leaf_tasks': [t for t in graph if not reverse_graph.get(t)],
            'root_tasks': [t for t in graph if not graph[t]],
            'circular_dependencies': [c for c in strongly_connected if len(c) > 1],
            'cycle_count': len([c for c in strongly_connected if len(c) > 1])
        }
    }

def _find_strongly_connected_components(graph):
    index = 0
    stack = []
    on_stack = set()
    indices = {}
    lowlink = {}
    sccs = []

    def visit(node):
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for nxt in graph.get(node, []):
            if nxt not in indices:
                visit(nxt)
                lowlink[node] = min(lowlink[node], lowlink[nxt])
            elif nxt in on_stack:
                lowlink[node] = min(lowlink[node], indices[nxt])

        if lowlink[node] == indices[node]:
            comp = []
            while True:
                v = stack.pop()
                on_stack.remove(v)
                comp.append(v)
                if v == node:
                    break
            sccs.append(comp)

    for n in graph:
        if n not in indices:
            visit(n)

    return sccs

def _get_node_group(task_id, graph, reverse_graph, blocking_counts):
    blocks = blocking_counts[task_id]
    has_deps = bool(graph[task_id])
    is_blocked = bool(reverse_graph.get(task_id))

    if blocks >= 3:
        return 'critical'
    elif not has_deps and not is_blocked:
        return 'independent'
    elif not has_deps:
        return 'root'
    elif not is_blocked:
        return 'leaf'
    else:
        return 'normal'

def _is_circular_edge(child, parent, components):
    for comp in components:
        if child in comp and parent in comp and len(comp) > 1:
            return True
    return False
