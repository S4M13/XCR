from multiprocessing.managers import BaseManager
import pickle

class Context:
    references = []

    def __init__(self, socket=('127.0.0.1', 37845), password=b'password'):
        self.manager = BaseManager(socket, password)
        self.manager.register("get")
        self.manager.register("set")
        self.manager.connect()

        for ref in Context.references:
            self.manager.set(ref, None)

    @classmethod
    def add_var(cls, var):

        def temp_get(self):
            resp = self.manager.get(var)
            return pickle.loads(resp._getvalue())

        def temp_set(self, value):
            self.manager.set(var, pickle.dumps(value))

        prop = property(temp_get)
        setattr(cls, var, prop)

        prop = prop.setter(temp_set)
        setattr(cls, var, prop)

        cls.references.append(var)

    @classmethod
    def add_multiple_vars(cls, variables):
        for var in variables:
            cls.add_var(var)


Context.add_multiple_vars(["CONFIG",
                           "SERVER_NAME",
                           "STUDENTS_DATASTORE",
                           "CLUBS_DATASTORE",
                           "DATABASE_ANALYSIS",
                           "DATABASE_LAST_ANALYSIS",
                           "DATABASE_ANALYZING",
                           "LOGIN_ATTEMPTS"
                           ])

GlobalContext = Context()

GlobalContext.CONFIG = {}
GlobalContext.SERVER_NAME = ""

GlobalContext.STUDENTS_DATASTORE = None
GlobalContext.CLUBS_DATASTORE = None

GlobalContext.DATABASE_ANALYSIS = {}
GlobalContext.DATABASE_LAST_ANALYSIS = 0
GlobalContext.DATABASE_ANALYZING = False

GlobalContext.LOGIN_ATTEMPTS = {}