import numpy as np

from geeksw.core import Plot

class C:

    outputs  = ["win/win"]
    requires = ["foo", "jenkins"]

    def __init__(self):
        pass

    def run(self, record): 

        record.put("win/win", "Win"+record.get("foo").title()+record.get("jenkins").title())

        x = np.linspace(0, 5, 200)
        y = np.sin(x)
