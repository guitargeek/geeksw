from geeksw.core import produces, requires


@produces("jenkins")
@requires(foo="foo")
def produce(foo):

    return foo + "Jenkins"
