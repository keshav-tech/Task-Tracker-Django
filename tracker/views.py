from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Project, Task




@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """
    Simple JSON login for Postman / API testing.
    """
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JsonResponse({"error": "Username and password are required."}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid credentials."}, status=400)

    login(request, user) 
    return JsonResponse({"message": "Logged in successfully", "username": user.username})


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def logout_view(request):
    """
    Simple logout endpoint.
    """
    logout(request)
    return JsonResponse({"message": "Logged out"})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_project(request):
    try:
        data = json.loads(request.body)
        project = Project.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            owner=request.user
        )
        return JsonResponse({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'owner': project.owner.username,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat()
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def list_projects(request):
    projects = Project.objects.filter(owner=request.user)
    
    search = request.GET.get('search')
    if search:
        projects = projects.filter(name__icontains=search)
    
    data = [{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'owner': p.owner.username,
        'created_at': p.created_at.isoformat(),
        'updated_at': p.updated_at.isoformat()
    } for p in projects]
    
    return JsonResponse({'projects': data})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return JsonResponse({'error': 'Only project owner can create tasks'}, status=403)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    title = data.get('title')
    if not title:
        return JsonResponse({'error': 'Title is required.'}, status=400)

    # Priority (required + int + range handled in model)
    raw_priority = data.get('priority')
    if raw_priority is None:
        return JsonResponse({'error': 'Priority is required.'}, status=400)
    try:
        priority = int(raw_priority)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Priority must be an integer between 1 and 5.'}, status=400)

    # Due date (optional) – parse string to date
    due_date_str = data.get('due_date')
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({'error': 'due_date must be in YYYY-MM-DD format.'}, status=400)

    task = Task(
        project=project,
        title=title,
        description=data.get('description', ''),
        priority=priority,
        status=data.get('status', 'todo'),
        due_date=due_date
    )

    assignee_id = data.get('assignee_id')
    if assignee_id:
        try:
            task.assignee = User.objects.get(id=assignee_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid assignee_id.'}, status=400)

    try:
        task.save()
    except ValidationError as e:
        # Use first message for clarity
        msg = e.messages[0] if hasattr(e, 'messages') and e.messages else str(e)
        return JsonResponse({'error': msg}, status=400)

    return JsonResponse({
        'id': task.id,
        'project_id': task.project.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'assignee': task.assignee.username if task.assignee else None,
        'created_at': task.created_at.isoformat(),
        'updated_at': task.updated_at.isoformat()
    }, status=201)

@login_required
@require_http_methods(["GET"])
def list_tasks(request):
    tasks = Task.objects.filter(
        Q(project__owner=request.user) | Q(assignee=request.user)
    )
    
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)
    
    project_id = request.GET.get('project_id')
    if project_id:
        tasks = tasks.filter(project_id=project_id)
    
    due_before = request.GET.get('due_before')
    if due_before:
        tasks = tasks.filter(due_date__lt=due_before)
    
    data = [{
        'id': t.id,
        'project_id': t.project.id,
        'project_name': t.project.name,
        'title': t.title,
        'description': t.description,
        'status': t.status,
        'priority': t.priority,
        'due_date': t.due_date.isoformat() if t.due_date else None,
        'assignee': t.assignee.username if t.assignee else None,
        'created_at': t.created_at.isoformat(),
        'updated_at': t.updated_at.isoformat()
    } for t in tasks]
    
    return JsonResponse({'tasks': data})



@csrf_exempt
@login_required
@require_http_methods(["GET", "POST"])
def projects_view(request):
    if request.method == "GET":
        # List My Projects
        projects = Project.objects.filter(owner=request.user)
        search = request.GET.get('search')
        if search:
            projects = projects.filter(name__icontains=search)

        data = [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'owner': p.owner.username,
            'created_at': p.created_at.isoformat(),
            'updated_at': p.updated_at.isoformat()
        } for p in projects]
        return JsonResponse({'projects': data})

    # POST → Create Project
    try:
        data = json.loads(request.body or "{}")
        name = data.get('name')
        description = data.get('description', '')

        if not name:
            return JsonResponse({'error': 'Project name is required.'}, status=400)

        project = Project.objects.create(
            name=name,
            description=description,
            owner=request.user
        )
        return JsonResponse({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'owner': project.owner.username,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat()
        }, status=201)
    except IntegrityError:
        return JsonResponse({'error': 'You already have a project with this name.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

# summary-view-anchor
@login_required
@require_http_methods(["GET"])
def dashboard(request):
    total_projects = Project.objects.filter(owner=request.user).count()
    
    total_tasks = Task.objects.filter(project__owner=request.user).count()
    
    status_counts = Task.objects.filter(
        project__owner=request.user
    ).values('status').annotate(count=Count('id'))
    
    status_dict = {item['status']: item['count'] for item in status_counts}
    
    upcoming_tasks = Task.objects.filter(
        Q(project__owner=request.user) | Q(assignee=request.user),
        due_date__isnull=False
    ).exclude(status='done').order_by('due_date')[:5]
    
    if upcoming_tasks:
        upcoming_list = [{
            'id': t.id,
            'title': t.title,
            'due_date': t.due_date.isoformat(),
            'priority': t.priority,
            'status': t.status
        } for t in upcoming_tasks]
    else:
        upcoming_list = "No upcoming tasks!"
    
    return JsonResponse({
        'total_projects': total_projects,
        'total_tasks': total_tasks,
        'tasks_by_status': status_dict,
        'upcoming_tasks': upcoming_list
    })