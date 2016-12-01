
class LTGeneric:

    def _write_header(self, descr):
        try:
            descr.write(self.imports + "\n")
        except AttributeError:
            pass
        header = self.name
        if self.ancestor_name:
            header = "{} inherits {}".format(self.name, self.ancestor_name)
        descr.write(header + "{\n")