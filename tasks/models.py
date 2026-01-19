from django.db import models


class Task(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("em_progresso", "Em Progresso"),
        ("concluida", "Concluída"),
    ]

    PRIORITY_CHOICES = [
        ("baixa", "Baixa"),
        ("media", "Média"),
        ("alta", "Alta"),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descrição")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    due_date = models.DateField(
        null=True, blank=True, verbose_name="Data de Vencimento"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pendente", verbose_name="Status"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="media",
        verbose_name="Prioridade",
    )
    user_id = models.IntegerField(verbose_name="ID do Usuário (API)")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"

    def __str__(self):
        return self.title
