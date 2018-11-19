class D:

    produces = ["foo", "bar"]
    requires = []

    def __init__(self):
        pass

    def run(self, record): 
        record.put("foo", "foo")
        record.put("bar", "bar")
