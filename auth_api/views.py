from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .services import APIService
from .forms import RegisterForm, LoginForm


class RegisterView(View):
    def get(self, request):
        return render(request, "auth/register.html")

    def post(self, request):
        # Obter dados do formulário
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        print(f"🔍 DEBUG - Dados do request.POST:")
        print(f"  first_name: '{first_name}'")
        print(f"  last_name: '{last_name}'")
        print(f"  username: '{username}'")
        print(f"  email: '{email}'")
        print(f"  Todos os campos POST: {dict(request.POST)}")

        # Validação básica no cliente
        errors = []

        if not all(
            [username, email, password, password_confirm, first_name, last_name]
        ):
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
            "first_name": first_name,
            "last_name": last_name,
        }

        # Chamar API
        response = APIService.register_user(user_data)

        if response:
            if response.status_code == 201:
                messages.success(
                    request, "✅ Conta criada com sucesso! Faça login para continuar."
                )
                return redirect("login")
            else:
                # Tratar erros da API
                try:
                    error_data = response.json()
                    print(f"📥 Erro da API: {error_data}")

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
            messages.error(request, "❌ Erro de conexão com o servidor de autenticação")

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
                    print(f"✅ Login bem-sucedido! Dados recebidos: {data.keys()}")

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

                    # IMPORTANTE: A API não retorna user_id na resposta de login?
                    # Vamos buscar usando o token
                    print(f"🔍 Buscando informações do usuário com token...")

                    # Primeiro, vamos tentar obter a lista de usuários
                    user_response = APIService.get_user_profile(access_token)

                    if user_response and user_response.status_code == 200:
                        user_info = user_response.json()
                        print(f"📊 Informações do usuário recebidas: {type(user_info)}")

                        # A API retorna uma lista de usuários
                        if isinstance(user_info, list):
                            print(f"📋 Lista com {len(user_info)} usuários")
                            # Procurar o usuário pelo email
                            user_found = None
                            for user in user_info:
                                print(f"  👤 Usuário: {user.get('email')}")
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
                                    "first_name": user_found.get("first_name"),
                                    "last_name": user_found.get("last_name"),
                                }
                                print(f"✅ Usuário encontrado: ID {user_id}")
                            else:
                                print(
                                    f"❌ Usuário com email {email} não encontrado na lista"
                                )
                                # Se não encontrou, usar um ID temporário
                                request.session["user_id"] = "temp_id"
                                request.session["user_data"] = {
                                    "email": email,
                                    "first_name": "Usuário",
                                }
                        else:
                            print(f"⚠️ Resposta inesperada: {user_info}")
                            messages.error(
                                request, "Formato de resposta inesperado da API"
                            )
                            return render(request, "auth/login.html")
                    else:
                        print(
                            f"❌ Erro ao buscar perfil: {user_response.status_code if user_response else 'No response'}"
                        )
                        # Mesmo sem perfil, podemos continuar com os tokens
                        request.session["user_id"] = "unknown"
                        request.session["user_data"] = {
                            "email": email,
                        }

                    messages.success(request, "Login realizado com sucesso!")
                    print(f"🎉 Redirecionando para task_list...")
                    return redirect("task_list")

                except Exception as e:
                    print(f"❌ Erro ao processar resposta: {e}")
                    import traceback

                    traceback.print_exc()
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
            return redirect("login")

        access_token = request.session.get("access_token")
        user_id = request.session.get("user_id")

        response = APIService.get_user_profile(access_token, user_id)

        if response and response.status_code == 200:
            user_data = response.json()
            return render(request, "auth/profile.html", {"user_data": user_data})

        messages.error(request, "Erro ao carregar perfil")
        return redirect("task_list")


class SessionDebugView(View):
    def get(self, request):
        if "access_token" not in request.session:
            return redirect("login")

        # Tentar buscar dados do usuário da API
        access_token = request.session.get("access_token")
        user_response = APIService.get_user_profile(access_token)

        session_data = {
            "access_token_exists": "access_token" in request.session,
            "access_token_length": (
                len(request.session.get("access_token", ""))
                if "access_token" in request.session
                else 0
            ),
            "refresh_token_exists": "refresh_token" in request.session,
            "user_id": request.session.get("user_id"),
            "user_data": request.session.get("user_data", {}),
        }

        api_data = None
        if user_response:
            api_data = {
                "status_code": user_response.status_code,
                "response": (
                    user_response.json()
                    if user_response.status_code == 200
                    else user_response.text
                ),
            }

        return render(
            request,
            "auth/debug_session.html",
            {
                "session_data": session_data,
                "api_data": api_data,
            },
        )
