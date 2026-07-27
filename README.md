# To-Do List

Task management web application built with Django, featuring session-based authentication, full task CRUD, and user profile management.

The project follows a two-app architecture: `auth_api` handles all authentication and user logic through a service layer, while `tasks` manages the task domain independently. Authentication is abstracted behind an `APIService` class — designed to work locally with a `DummyResponse` fallback, making the system fully functional without any external dependencies.

---

## Features

| Feature              | Description                                                                                  |
| -------------------- | -------------------------------------------------------------------------------------------- |
| Registration & Login | User creation and session-based authentication via email and password                        |
| Task CRUD            | Create, edit, view, and delete tasks with title, description, due date, status, and priority |
| Filtering            | Filter tasks by status (pending, in progress, completed) and priority (low, medium, high)    |
| User Profile         | View account info, task statistics, edit username/email, change password, and delete account |
| Session Management   | Authenticated session persists for 24 hours via Django session engine                        |
| Responsive UI        | Bootstrap 5 layout adapted for desktop, tablet, and mobile                                   |

---

## Screenshots

**Login**
![Login](docs/screenshots/login.png)

**Registration**
![Registration](docs/screenshots/registro.png)

**Task List**
![Task List](docs/screenshots/tela_inicial.png)

**Task List with Tasks**
![Task List with Tasks](docs/screenshots/tela_inicial_com_tarefa.png)

**Create Task**
![Create Task](docs/screenshots/cadastrar_tarefa.png)

**User Profile**
![Profile](docs/screenshots/perfil.png)

---

## Project Structure

```
├── auth_api/                  # Authentication and user management app
│   ├── services.py            # APIService — abstracts auth logic with local fallback
│   └── views.py               # Login, register, profile, password, and delete views
├── tasks/                     # Task domain app
│   ├── models.py              # Task model (title, description, due_date, status, priority)
│   ├── forms.py               # TaskForm with Bootstrap-compatible widgets
│   ├── views.py               # TaskListView, TaskCreateView, TaskUpdateView, TaskDeleteView
│   └── urls.py                # Task routes
├── templates/
│   ├── auth/                  # login.html, register.html, profile.html
│   └── tasks/                 # task_list.html, task_form.html
├── docs/
│   └── screenshots/           # Project screenshots
├── todolist_project/
│   ├── settings.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

---

## Technologies

**Backend**

- Python 3.12
- Django 5.2
- Django REST Framework 3.16
- django-crispy-forms + crispy-bootstrap5

**Frontend**

- Bootstrap 5.3
- Bootstrap Icons
- JavaScript (vanilla)

**Database**

- SQLite (local development)

**Server**

- Gunicorn

---

## How to Run

**1. Clone the repository**

```bash
git clone https://github.com/luccaszzzz/to_do_list.git
cd to_do_list
```

**2. Create and activate the virtual environment**

```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate
# Linux/Mac
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Apply migrations**

```bash
python manage.py migrate
```

**5. Create a superuser (optional)**

```bash
python manage.py createsuperuser
```

**6. Start the server**

```bash
python manage.py runserver
```

Access at `http://127.0.0.1:8000/`

---

## Author

Developed by Lucas Emanoel da Silva Freitas

---

[Leia em Português](README.pt-br.md)
