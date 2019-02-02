from geeksw.framework import produces, consumes


@produces("jenkins")
@consumes(foo="foo")
def produce(foo):

    return foo + "Jenkins"
