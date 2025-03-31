import os

# The arguments to setdefault must match the configuration in the main() function in your manage.py file

environ=os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carstrucx.settings')

# Import the app variable from your Django project wsgi file

from carstrucx.wsgi import application
application = application