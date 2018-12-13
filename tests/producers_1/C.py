from geeksw.core import Producer

class C(Producer):

    product = "win/win"
    requires = ["foo", "jenkins"]

    def run(self, inputs):

        return "Win" + inputs["foo"].title() + inputs["jenkins"].title()
