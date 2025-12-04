# демо синхронных функций
# для сравнения с асинхронными
# что такое time.time()
# если мы напишем start= time.time() в начале вычисления
# а в конце напишем end = time.time()
# и захотим вывести end-start то получим время которое ушло на код
import time

def load_page (name: str, delay: int) -> None:
    print(f'Loading page {name}...')
    time.sleep(delay)
    print(f'page {name} loaded')

start = time.time()

load_page('A', 2)
load_page('B', 3)
load_page('C', 4)

end = time.time()
print(f'Total time: {end - start:.2f} seconds')