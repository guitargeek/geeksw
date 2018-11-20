from geeksw.core import Plot

class A:

    produces = ["lin"]
    requires = ["foo", "jenkins"]

    def __init__(self):
        pass

    def run(self, record): 

        record.put("lin", "Lin"+record.get("foo").title()+record.get("jenkins").title())
