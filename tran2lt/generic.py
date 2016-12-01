
class LTGeneric:

    def set_name(self, name):
        self.name = name

    def set_imports(self, imports):
        self.imports = imports

    def _write_header(self, descr):
        try:
            descr.write(self.imports + "\n")
        except AttributeError:
            pass
        header = self.name
        try:
            if self.ancestor_name:
                header = "{} inherits {}".format(self.name, self.ancestor_name)

        except AttributeError:
            pass
        descr.write(header + "{\n")

    def _write_footer(self, descr):
        descr.write("}\n")