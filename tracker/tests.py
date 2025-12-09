from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta
from .models import Project, Task

class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
    
    def test_duplicate_project_name_same_owner(self):
        Project.objects.create(name='Project A', owner=self.user)
        with self.assertRaises(IntegrityError):
            Project.objects.create(name='Project A', owner=self.user)

class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project = Project.objects.create(name='Test Project', owner=self.user)
    
    def test_done_task_with_future_due_date(self):
        future_date = date.today() + timedelta(days=5)
        task = Task(
            project=self.project,
            title='Test Task',
            status='done',
            priority=3,
            due_date=future_date
        )
        with self.assertRaises(ValidationError):
            task.save()

class TaskListViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        
        self.project1 = Project.objects.create(name='Project 1', owner=self.user1)
        self.project2 = Project.objects.create(name='Project 2', owner=self.user2)
        
        self.task1 = Task.objects.create(
            project=self.project1,
            title='Task 1',
            priority=3
        )
        self.task2 = Task.objects.create(
            project=self.project2,
            title='Task 2',
            priority=2
        )
        self.task3 = Task.objects.create(
            project=self.project2,
            title='Task 3',
            priority=1,
            assignee=self.user1
        )
    
    def test_task_list_filters_by_user(self):
        self.client.login(username='user1', password='pass1')
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        task_ids = [task['id'] for task in data['tasks']]
        
        self.assertIn(self.task1.id, task_ids)
        self.assertNotIn(self.task2.id, task_ids)
        self.assertIn(self.task3.id, task_ids)