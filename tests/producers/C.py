from geeksw.core import Plot

class C:

    produces = ["win/win"]
    requires = ["foo", "jenkins"]

    def __init__(self):
        pass

    def run(self, record): 

        record.put("win/win", "Win"+record.get("foo").title()+record.get("jenkins").title())
