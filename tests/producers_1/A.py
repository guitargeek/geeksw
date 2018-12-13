from geeksw.core import Producer

class A(Producer):

    product = "lin"
    requires = ["foo", "jenkins"]

    def run(self, inputs): 

        return "Lin" + inputs["foo"].title() + inputs["jenkins"].title()
