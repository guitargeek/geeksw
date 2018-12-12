from geeksw.core import Producer

class D(Producer):

    product = "foo"
    requires = []

    def run(self, inputs):
        return "foo"
