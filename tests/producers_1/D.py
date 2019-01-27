from geeksw.framework import produces, consumes


@produces("foo")
def produce():

    return "foo"
