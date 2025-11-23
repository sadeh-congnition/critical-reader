import subprocess
import djclick as click
from django.contrib.auth import get_user_model
import os


@click.command()
def reset_db():
    if os.environ["DEPLOYMENT_ENV"] not in (
        "dev",
        "test",
        "testing",
        "DEV",
        "TEST",
        "TESTING",
    ):
        raise Exception("This command is only for development")

    subprocess.run("rm db.sqlite3", shell=True)
    subprocess.run("uv run manage.py makemigrations", shell=True)
    subprocess.run("uv run manage.py migrate", shell=True)
    User = get_user_model()
    User.objects.create_superuser(username="motk", password="mokt")
