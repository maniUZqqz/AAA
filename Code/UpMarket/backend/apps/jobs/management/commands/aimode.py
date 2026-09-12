"""`python manage.py aimode` — prints `api` or `local`, nothing else.

start.bat needs to know whether this machine has to launch Ollama and ComfyUI
at all. Parsing .env from batch is fragile (carets, quoting, empty values), and
worse, it would be a *second* place that decides the mode — free to drift from
what Django actually does.

So the launcher asks Django instead. One source of truth: settings +
services.ai.providers.api_mode().
"""
from django.core.management.base import BaseCommand

from services.ai import providers


class Command(BaseCommand):
    help = "چاپ حالت هوش مصنوعی: api یا local (برای start.bat)"

    def handle(self, *args, **options):
        # bare print: the launcher captures stdout, so no styling, no newline noise
        self.stdout.write("api" if providers.api_mode() else "local", ending="")
