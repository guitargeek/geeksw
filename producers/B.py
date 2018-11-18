class B:

    produces = ["jenkins"]
    requires = ["bar"]

    def __init__(self):
        pass

    def run(self, record): 
        record["jenkins"] = record["bar"] + "Jenkins"
