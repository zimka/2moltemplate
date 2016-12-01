from MDAnalysis import Universe


class NonUniqueTypesError(ValueError):
    pass



class MOL2Reader:
    def __init__(self, filename):
        u = Universe(filename)

        self.atoms = u.atoms
        self.bonds = u.bonds