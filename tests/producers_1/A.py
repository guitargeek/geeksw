from geeksw.framework import produces, consumes


@produces("lin")
@consumes(foo="foo", jenkins="jenkins")
def produce(foo, jenkins):

    return "Lin" + foo.title() + jenkins.title()
