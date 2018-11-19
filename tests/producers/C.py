class C:

    produces = ["win"]
    requires = ["foo", "jenkins"]

    def __init__(self):
        pass

    def run(self, record): 
        record["win"] = "Win"+record["foo"].title()+record["jenkins"].title()
