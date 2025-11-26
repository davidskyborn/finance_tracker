# задача номер 3. контекстный менеджер

import time

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc, tb):
        end = time.time()
        print("время выполнения: ", end - self.start)