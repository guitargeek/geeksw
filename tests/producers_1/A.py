from geeksw.core import produces, requires


@produces("lin")
@requires(foo="foo", jenkins="jenkins")
def produce(foo, jenkins):

    return "Lin" + foo.title() + jenkins.title()
