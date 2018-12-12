from geeksw.core import SingleDatasetProducer

class D(SingleDatasetProducer):

    produces = ["foo", "bar"]
    requires = []

    def __init__(self):
        pass

    def run(self, dataset, record): 
        record.put("foo", "foo")
        record.put("bar", "bar")
