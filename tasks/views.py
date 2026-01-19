from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .models import Task
from .forms import TaskForm # type: ignore


class TaskListView(View):
    def get(self, request):
        if "access_token" not in request.session:
            return redirect("login")

        user_id = request.session.get("user_id")
        tasks = Task.objects.filter(user_id=user_id)

        status_filter = request.GET.get("status")
        priority_filter = request.GET.get("priority")

        if status_filter:
            tasks = tasks.filter(status=status_filter)
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)

        return render(
            request,
            "tasks/task_list.html",
            {"tasks": tasks, "user_data": request.session.get("user_data", {})},
        )


class TaskCreateView(View):
    def get(self, request):
        if "access_token" not in request.session:
            return redirect("login")

        form = TaskForm()
        return render(
            request, "tasks/task_form.html", {"form": form, "title": "Nova Tarefa"}
        )

    def post(self, request):
        if "access_token" not in request.session:
            return redirect("login")

        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user_id = request.session.get("user_id")
            task.save()
            messages.success(request, "Tarefa criada com sucesso!")
            return redirect("task_list")

        return render(
            request, "tasks/task_form.html", {"form": form, "title": "Nova Tarefa"}
        )


class TaskUpdateView(View):
    def get(self, request, pk):
        if "access_token" not in request.session:
            return redirect("login")

        task = get_object_or_404(Task, pk=pk, user_id=request.session.get("user_id"))
        form = TaskForm(instance=task)
        return render(
            request,
            "tasks/task_form.html",
            {"form": form, "title": "Editar Tarefa", "task": task},
        )

    def post(self, request, pk):
        if "access_token" not in request.session:
            return redirect("login")

        task = get_object_or_404(Task, pk=pk, user_id=request.session.get("user_id"))
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Tarefa atualizada com sucesso!")
            return redirect("task_list")

        return render(
            request,
            "tasks/task_form.html",
            {"form": form, "title": "Editar Tarefa", "task": task},
        )


class TaskDeleteView(View):
    def post(self, request, pk):
        if "access_token" not in request.session:
            return redirect("login")

        task = get_object_or_404(Task, pk=pk, user_id=request.session.get("user_id"))
        task.delete()
        messages.success(request, "Tarefa excluída com sucesso!")
        return redirect("task_list")
