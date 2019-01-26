from geeksw.core import produces, requires


@produces("win/win")
@requires(foo="foo", jenkins="jenkins")
def produce(foo, jenkins):

    return "Win" + foo.title() + jenkins.title()
