from taskiq_redis import RedisAsyncResultBackend, ListQueueBroker
from taskiq import TaskiqEvents
from cobwebai.settings import settings
from .generate_note import generate_note
from .process_file import process_file
from .generate_test import generate_test
from .lifespan import startup, shutdown
from .utils import OperationMiddleware

broker = ListQueueBroker(url=settings.redis_url)
result_backend = RedisAsyncResultBackend(redis_url=settings.redis_url)

generate_note_task = broker.task(generate_note)
process_file_task = broker.task(process_file)
generate_test_task = broker.task(generate_test)

broker.on_event(TaskiqEvents.WORKER_STARTUP)(startup)
broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)(shutdown)

broker.add_middlewares(OperationMiddleware())
