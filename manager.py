from multiprocessing import Lock
from multiprocessing.managers import BaseManager


GlobalLock = Lock()

storage = {}


def getter(name):
    with GlobalLock:
        return storage[name]


def setter(name, value):
    with GlobalLock:
        storage[name] = value


ProcessManager = BaseManager(('127.0.0.1', 37845), b'password')
ProcessManager.register("get", getter)
ProcessManager.register("set", setter)
server = ProcessManager.get_server()

if __name__ == '__main__':
    print("[+] Manager running")
    server.serve_forever()
