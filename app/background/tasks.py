from .celery import app

@app.task(bind = True)
def generate_report(self, *args, **kwargs):
    pass