from celery import Celery
import os
import requests
import time
import subprocess
from .util import GpuAvail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eai.settings')
app = Celery('eai')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.enable_utc = False

app.autodiscover_tasks()

@app.task
def adjust_concurrency():
  gpu_checker_url = 'http://127.0.0.1:7000/gpu/' 
  res = requests.get(gpu_checker_url)
  
  if res.status_code == 200:
    data = res.json()
    inspector = app.control.inspect()
    stats = inspector.stats()
    list_gpu = data['gpu']
    gpu_ids = []
    for i in list_gpu:
       gpu_ids.append(i['id'])
    GpuAvail.set_gpu(gpu_ids)

    if stats:
      current_concurrency = list(stats.values())[0]['pool']['max-concurrency']
      print(f'Current concurrency: {current_concurrency}')
      available_gpu = data['total_gpu_available']
      print(f'Avaibale gpu: {available_gpu}')
      
      if available_gpu != current_concurrency:

        os.system("pkill -f 'celery worker'")
        time.sleep(5)  # Adjust delay as needed
        print('no worker alive')

        # Start a new Celery worker with the specified concurrency
        command = f"celery -A eai worker --concurrency={available_gpu} &"
        subprocess.call(command, shell=True)
        print('worker alive')

        if available_gpu > current_concurrency:
          n = available_gpu - current_concurrency
          print(f'Increase concurrency by {n}')
        else:
          n = current_concurrency - available_gpu
          print(f'Decrease concurrency by {n}')
        time.sleep(5)

        # Check the updated concurrency
        updated_stats = inspector.stats()
        if updated_stats:
          new_concurrency = list(updated_stats.values())[0]['pool']['max-concurrency']
          print(f'Updated concurrency: {new_concurrency}')
        else:
          print("No running workers or unable to fetch updated stats.")
    else:
        print("No running workers or unable to fetch stats.")

  