python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue1 --concurrency=1

python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue2 --concurrency=1

python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue3 --concurrency=1

python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue4 --concurrency=1

celery --broker=redis://192.168.1.137:6380/0 flower