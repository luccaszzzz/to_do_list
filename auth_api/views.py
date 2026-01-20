from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .services import APIService
from django.http import JsonResponse
from tasks.models import Task

class RegisterView(View):
    def get(self, request):
        return render(request, "auth/register.html")

    def post(self, request):
        # Obter dados do formulário
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        # Validação básica no cliente
        errors = []

        if not all([username, email, password, password_confirm]):
            errors.append("Todos os campos são obrigatórios")

        if password != password_confirm:
            errors.append("As senhas não coincidem")

        if len(password) < 8:
            errors.append("A senha deve ter pelo menos 8 caracteres")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "auth/register.html")

        # Preparar dados para API
        user_data = {
            "username": username,
            "email": email,
            "password": password,
        }

        # Chamar API
        response = APIService.register_user(user_data)

        if response:
            if response.status_code == 201:
                messages.success(
                    request, "Conta criada com sucesso! Faça login para continuar."
                )
                return redirect("login")
            else:
                # Tratar erros da API
                try:
                    error_data = response.json()
                    print(f"Erro da API: {error_data}")

                    if "email" in error_data:
                        messages.error(request, f"Email: {error_data['email'][0]}")
                    elif "username" in error_data:
                        messages.error(request, f"Usuário: {error_data['username'][0]}")
                    elif "password" in error_data:
                        messages.error(request, f"Senha: {error_data['password'][0]}")
                    elif "detail" in error_data:
                        messages.error(request, f"Erro: {error_data['detail']}")
                    elif "non_field_errors" in error_data:
                        messages.error(request, error_data["non_field_errors"][0])
                    else:
                        messages.error(request, f"Erro ao criar conta: {response.text}")

                except Exception as e:
                    messages.error(
                        request, f"Erro ao processar resposta da API: {str(e)}"
                    )
        else:
            messages.error(request, "Erro de conexão com o servidor de autenticação")

        return render(request, "auth/register.html")


class LoginView(View):
    def get(self, request):
        if "access_token" in request.session:
            return redirect("task_list")
        return render(request, "auth/login.html")

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Email e senha são obrigatórios")
            return render(request, "auth/login.html")

        credentials = {
            "email": email,
            "password": password,
        }

        response = APIService.login_user(credentials)

        if response:
            if response.status_code == 200:
                try:
                    data = response.json()

                    # Extrair tokens
                    access_token = data.get("access")
                    refresh_token = data.get("refresh")

                    if not access_token or not refresh_token:
                        messages.error(
                            request, "Resposta da API inválida: tokens não encontrados"
                        )
                        return render(request, "auth/login.html")

                    # Salvar tokens na sessão
                    request.session["access_token"] = access_token
                    request.session["refresh_token"] = refresh_token

                    # Buscar informações do usuário
                    user_response = APIService.get_user_profile(access_token)

                    if user_response and user_response.status_code == 200:
                        user_info = user_response.json()

                        # A API retorna uma lista de usuários
                        if isinstance(user_info, list):
                            # Procurar o usuário pelo email
                            user_found = None
                            for user in user_info:
                                if user.get("email") == email:
                                    user_found = user
                                    break

                            if user_found:
                                user_id = user_found.get("id")
                                request.session["user_id"] = user_id
                                request.session["user_data"] = {
                                    "id": user_id,
                                    "username": user_found.get("username"),
                                    "email": user_found.get("email"),
                                }
                            else:
                                # Se não encontrou, usar um ID temporário
                                request.session["user_id"] = "temp_id"
                                request.session["user_data"] = {
                                    "email": email,
                                }
                        else:
                            messages.error(
                                request, "Formato de resposta inesperado da API"
                            )
                            return render(request, "auth/login.html")
                    else:
                        # Mesmo sem perfil, podemos continuar com os tokens
                        request.session["user_id"] = "unknown"
                        request.session["user_data"] = {
                            "email": email,
                        }

                    messages.success(request, "Login realizado com sucesso!")
                    return redirect("task_list")

                except Exception as e:
                    print(f"Erro ao processar resposta: {e}")
                    messages.error(request, f"Erro ao processar resposta: {str(e)}")
            else:
                # Erro de login
                error_msg = "Email ou senha incorretos"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    pass
                messages.error(request, error_msg)
        else:
            messages.error(request, "Erro de conexão com o servidor")

        return render(request, "auth/login.html")


class LogoutView(View):
    def get(self, request):
        request.session.flush()
        messages.success(request, "Logout realizado com sucesso!")
        return redirect("login")


class ProfileView(View):
    def get(self, request):
        if "access_token" not in request.session:
            messages.error(request, "Faça login para acessar seu perfil")
            return redirect("login")

        access_token = request.session.get("access_token")
        user_id = request.session.get("user_id")

        # Buscar dados do usuário na API
        response = APIService.get_user_profile(access_token, user_id)

        if response and response.status_code == 200:
            user_data = response.json()
            
            # Buscar estatísticas de tarefas
            if user_id and user_id not in ["temp_id", "unknown"]:
                try:
                    user_tasks = Task.objects.filter(user_id=user_id)
                    total_tasks = user_tasks.count()
                    pending_tasks = user_tasks.filter(status='pendente').count()
                    completed_tasks = user_tasks.filter(status='concluida').count()
                    in_progress_tasks = user_tasks.filter(status='em_progresso').count()
                except:
                    total_tasks = pending_tasks = completed_tasks = in_progress_tasks = 0
            else:
                total_tasks = pending_tasks = completed_tasks = in_progress_tasks = 0

            context = {
                "user_data": user_data,
                "total_tasks": total_tasks,
                "pending_tasks": pending_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
            }
            
            return render(request, "auth/profile.html", context)

        messages.error(request, "Erro ao carregar perfil")
        return redirect("task_list")


class UpdateProfileView(View):
    def post(self, request):
        if "access_token" not in request.session:
            messages.error(request, "Faça login para atualizar seu perfil")
            return redirect("login")

        # Coletar dados do formulário
        username = request.POST.get("username")
        email = request.POST.get("email")
        user_id = request.session.get("user_id")
        access_token = request.session.get("access_token")

        # Validar dados
        if not all([username, email]):
            messages.error(request, "Todos os campos são obrigatórios")
            return redirect("profile")

        # Preparar dados para API
        user_data = {
            "username": username,
            "email": email,
        }

        # Atualizar via API
        response = APIService.update_user(access_token, user_id, user_data)

        if response:
            if response.status_code == 200:
                # Atualizar dados na sessão
                request.session["user_data"] = {
                    "id": user_id,
                    "username": username,
                    "email": email,
                }
                
                messages.success(request, "Perfil atualizado com sucesso!")
            else:
                try:
                    error_data = response.json()
                    error_msg = "Erro ao atualizar perfil"
                    if "detail" in error_data:
                        error_msg = error_data["detail"]
                    elif "email" in error_data:
                        error_msg = f"Email: {error_data['email'][0]}"
                    elif "username" in error_data:
                        error_msg = f"Usuário: {error_data['username'][0]}"
                    
                    messages.error(request, f"{error_msg}")
                except:
                    messages.error(request, "Erro ao atualizar perfil")
        else:
            messages.error(request, "Erro de conexão com a API")

        return redirect("profile")


class ChangePasswordView(View):
    def post(self, request):
        if "access_token" not in request.session:
            messages.error(request, "Faça login para alterar sua senha")
            return redirect("login")

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Validar
        if not all([current_password, new_password, confirm_password]):
            messages.error(request, "Todos os campos são obrigatórios")
            return redirect("profile")

        if new_password != confirm_password:
            messages.error(request, "As novas senhas não coincidem")
            return redirect("profile")

        if len(new_password) < 8:
            messages.error(request, "A nova senha deve ter pelo menos 8 caracteres")
            return redirect("profile")

        # Nota: Verifique se a API tem endpoint para alterar senha
        messages.info(request, "Alteração de senha via API ainda não implementada.")
        return redirect("profile")


class DeleteAccountView(View):
    def post(self, request):
        if "access_token" not in request.session:
            messages.error(request, "Faça login para excluir sua conta")
            return redirect("login")

        confirm_email = request.POST.get("confirm_email")
        user_email = request.session.get("user_data", {}).get("email")
        user_id = request.session.get("user_id")
        access_token = request.session.get("access_token")

        # Confirmar email
        if confirm_email != user_email:
            messages.error(request, "O email não corresponde ao da sua conta")
            return redirect("profile")

        # Excluir conta via API
        response = APIService.delete_user(access_token, user_id)

        if response and response.status_code == 204:
            # Limpar sessão e excluir tarefas locais
            if user_id and user_id not in ["temp_id", "unknown"]:
                try:
                    Task.objects.filter(user_id=user_id).delete()
                except:
                    pass
            request.session.flush()
            
            messages.success(request, "Sua conta foi excluída com sucesso!")
            return redirect("login")
        else:
            messages.error(request, "Erro ao excluir conta")
            return redirect("profile")