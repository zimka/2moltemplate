import numpy as np
from .generic import LTGeneric
from functools import wraps


def check(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        self = args[0]
        self._check(self)
        f(*args, **kwargs)

    return wrap


class LTManipulate(LTGeneric):
    def __init__(self, name, axis=None, points=None, angles=None, variable_name="var"):
        self.name = name

        self.points = points
        self.angles = angles
        self.axis = axis
        self.variable_name = variable_name
        self._check()

    def set_points(self, points):
        self.points = points
        self._check()

    def set_variable(self, variable_name):
        self.variable_name = variable_name

    def set_angles(self, angles):
        self.angles = angles
        self._check()

    def set_axis(self, axis):
        self.axis= axis
        self._check()

    def set_single_axis(self,axis, ntimes=None):
        if not ntimes:
            ntimes = len(self.points)
        self.axis = np.tile(axis,(1, ntimes))
        self._check()

    def _check(self):
        try:
            if not(len(self.angles) == len(self.points) == len(self.axis)):
                raise ValueError("len angles: {}, len points:{}, len axis: {}".format(
                    len(self.angles), len(self.points), len(self.axis))
                )
        except AttributeError:
            return 0
        return 1

    def _write_lines(self, descr, prefix="  "):
        if not self._check():
            raise ValueError("Angles or points or axis are not defined")
        descr.write(prefix + "{var} = new {name}[{num}]\n".format(var = self.variable_name,
                                                       name=self.name,
                                                       num=len(self.points)))

        template = prefix + "{}".format(self.variable_name) + "[{num}].move({point}).rot({rot})\n"
        for num, angle in enumerate(self.angles):
            point = self.points[num]
            axis = self.axis[num]
            point_str = ",".join(str(x) for x in point)
            axis_str = ",".join(str(x) for x in axis)
            axis_str += ",{}".format(angle)
            descr.write(template.format(num=str(num), point=point_str, rot=axis_str))

    def write_lt(self, filename):
        out = open(filename, "w")
        #self._write_header(out)
        self._write_lines(out)
        #self._write_footer(out)