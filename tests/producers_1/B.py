from geeksw.core import Producer

class B(Producer):

    product = "jenkins"
    requires = ["foo"]

    def run(self, inputs):
        return inputs["foo"] + "Jenkins"
