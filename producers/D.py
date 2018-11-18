class D:

    produces = ["foo", "bar"]
    requires = []

    def __init__(self):
        pass

    def run(self, record): 
        record["foo"] = "foo"
        record["bar"] = "bar"
