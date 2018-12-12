from geeksw.core import SingleDatasetProducer

class B(SingleDatasetProducer):

    produces = ["jenkins"]
    requires = ["bar"]

    def __init__(self):
        pass

    def run(self, dataset, record): 
        record.put("jenkins", record.get("bar") + "Jenkins")
