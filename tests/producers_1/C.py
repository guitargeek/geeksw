from geeksw.framework import produces, consumes


@produces("win/win")
@consumes(foo="foo", jenkins="jenkins")
def produce(foo, jenkins):

    return "Win" + foo.title() + jenkins.title()
