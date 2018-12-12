from geeksw.core import SingleDatasetProducer

class C(SingleDatasetProducer):

    produces = ["win/win"]
    requires = ["foo", "jenkins"]

    def __init__(self):
        pass

    def run(self, dataset, record): 

        record.put("win/win", "Win"+record.get("foo").title()+record.get("jenkins").title())
