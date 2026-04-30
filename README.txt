Team Task Manager
==================

A production-ready team collaboration and task management web application built
with Django 4.2, Django REST Framework, and Tailwind CSS.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROJECT OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Team Task Manager enables teams to:
- Create and manage projects with team members
- Assign tasks with priorities, due dates, and status tracking
- Role-based access (Admin vs Member)
- Real-time dashboard with statistics
- Full REST API with token authentication

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LOCAL SETUP STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Clone the repository:
   git clone <repo-url>
   cd Team_Task_Manager

2. Create and activate virtual environment:
   python -m venv venv
   venv\Scripts\activate          (Windows)
   source venv/bin/activate       (Mac/Linux)

3. Install dependencies:
   pip install -r requirements.txt

4. Create .env file:
   copy .env.example .env
   (Edit .env and set a proper SECRET_KEY)

5. Run database migrations:
   python manage.py migrate

6. Seed demo data:
   python manage.py seed_demo

7. Start development server:
   python manage.py runserver

8. Visit http://127.0.0.1:8000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEMO CREDENTIALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Admin:
  Email: admin@demo.com
  Password: Admin@123

Member 1:
  Email: member1@demo.com
  Password: Member@123

Member 2:
  Email: member2@demo.com
  Password: Member@123

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LIVE URL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

https://your-app.railway.app  (placeholder — update after deployment)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API ENDPOINTS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Authentication:
  POST  /api/v1/auth/token/         Obtain JWT token pair
  POST  /api/v1/auth/token/refresh/ Refresh access token

Users:
  GET   /api/v1/users/me/           Current user profile

Projects:
  GET   /api/v1/projects/           List all projects (admin) or my projects
  POST  /api/v1/projects/           Create a new project [Admin]
  GET   /api/v1/projects/<id>/      Project detail
  PUT   /api/v1/projects/<id>/      Update project [Admin]
  DELETE /api/v1/projects/<id>/     Delete project [Admin]

Tasks:
  GET   /api/v1/tasks/              List tasks (filter: ?project=, ?status=, ?assigned_to=)
  POST  /api/v1/tasks/              Create task
  GET   /api/v1/tasks/<id>/         Task detail
  PUT   /api/v1/tasks/<id>/         Update task
  PATCH /api/v1/tasks/<id>/         Partial update
  DELETE /api/v1/tasks/<id>/        Delete task [Admin]
  PATCH /api/v1/tasks/<id>/status/  Update task status only

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANAGEMENT COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  python manage.py seed_demo         Create demo users, projects, and tasks
  python manage.py mark_overdue_tasks Mark tasks past due date as overdue

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEPLOYMENT (Railway)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Required environment variables on Railway:
  SECRET_KEY=<strong-random-key>
  DEBUG=False
  ALLOWED_HOSTS=your-app.railway.app
  DATABASE_URL=<provided-by-railway-postgres-plugin>
