import json
from django.contrib.auth import get_user_model


class DummyResponse:
    def __init__(self, status_code, data=None, text=None):
        self.status_code = status_code
        self._data = data or {}
        self.text = text if text is not None else json.dumps(self._data)

    def json(self):
        return self._data


class APIService:
    @staticmethod
    def _get_headers(token=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    @staticmethod
    def register_user(user_data):
        UserModel = get_user_model()
        username = (user_data.get("username") or "").strip()
        email = (user_data.get("email") or "").strip()
        password = user_data.get("password") or ""

        errors = {}
        if not username or not email or not password:
            errors["non_field_errors"] = ["Todos os campos são obrigatórios"]
        if len(password) < 8:
            errors["password"] = ["A senha deve ter pelo menos 8 caracteres"]
        if UserModel.objects.filter(username__iexact=username).exists():
            errors["username"] = ["Este usuário já existe"]
        if UserModel.objects.filter(email__iexact=email).exists():
            errors["email"] = ["Este e-mail já está em uso"]

        if errors:
            return DummyResponse(400, errors)

        user = UserModel.objects.create_user(username=username, email=email, password=password)
        return DummyResponse(201, {"id": user.pk, "username": user.username, "email": user.email})

    @staticmethod
    def login_user(credentials):
        UserModel = get_user_model()
        email = (credentials.get("email") or "").strip()
        password = credentials.get("password") or ""

        user = UserModel.objects.filter(email__iexact=email).first()
        if not user or not user.check_password(password):
            return DummyResponse(401, {"detail": "Email ou senha incorretos"})

        return DummyResponse(
            200,
            {
                "access": f"local-access-{user.pk}",
                "refresh": f"local-refresh-{user.pk}",
            },
        )

    @staticmethod
    def refresh_token(refresh_token):
        return DummyResponse(200, {"access": refresh_token, "refresh": refresh_token})

    @staticmethod
    def get_user_profile(access_token, user_id=None):
        UserModel = get_user_model()

        if user_id:
            try:
                user = UserModel.objects.get(pk=user_id)
            except UserModel.DoesNotExist:
                return DummyResponse(404, {"detail": "Usuário não encontrado"})
            return DummyResponse(
                200,
                [
                    {
                        "id": user.pk,
                        "username": user.username,
                        "email": user.email,
                    }
                ],
            )

        users = list(UserModel.objects.values("id", "username", "email"))
        return DummyResponse(200, users)

    @staticmethod
    def update_user(access_token, user_id, user_data):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return DummyResponse(404, {"detail": "Usuário não encontrado"})

        username = (user_data.get("username") or "").strip()
        email = (user_data.get("email") or "").strip()

        if username:
            user.username = username
        if email:
            user.email = email
        user.save(update_fields=["username", "email"])

        return DummyResponse(200, {"id": user.pk, "username": user.username, "email": user.email})

    @staticmethod
    def delete_user(access_token, user_id):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return DummyResponse(404, {"detail": "Usuário não encontrado"})

        user.delete()
        return DummyResponse(204, {})
