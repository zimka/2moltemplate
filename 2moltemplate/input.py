from MDAnalysis import Universe
from MDAnalysis.topology.core import guess_angles, guess_dihedrals
import MDAnalysis.core.topologyobjects as top


class NonUniqueTypesError(ValueError):
    pass


class LAMMPSData:
    def __init__(self, filename):
        u = Universe(filename)

        self.atoms = u.atoms
        self.bonds = u.bonds
        angles_ind = guess_angles(self.bonds)
        self.angles = top.TopologyGroup.from_indices(set(angles_ind), self.atoms,
                                                bondclass=top.Angle, guessed=True)

        dihedrals_ind = guess_dihedrals(self.angles)
        self.dihedrals = top.TopologyGroup.from_indices(set(dihedrals_ind), self.atoms,
                                                   bondclass=top.Dihedral, guessed=True)

        def _con_unique(con):
            result = True
            for c in con:
                if c[::-1] in con:
                    if not c == c[::-1]:
                        result = False
            return result

        def _get_types(group):
            if not _con_unique(set(group)):
                raise NonUniqueTypesError("{} types not unique".format(type(group)))
            return list(set(group))

        self.atoms_types = self.atoms.types
        self.bonds_types = _get_types(self.bonds.types())
        self.angles_types = _get_types(self.angles.types())
        self.dihedrals_types = _get_types(self.dihedrals.types())

def iinput(filename):
    u = Universe("../aligned.mol2")

    atoms = u.atoms
    bonds = u.bonds
    angles_ind = guess_angles(bonds)
    angles = top.TopologyGroup.from_indices(set(angles_ind), atoms,
                                            bondclass=top.Angle, guessed=True)

    dihedrals_ind = guess_dihedrals(angles)
    dihedrals = top.TopologyGroup.from_indices(set(dihedrals_ind), atoms,
                                            bondclass=top.Dihedral, guessed=True)

    print(atoms)
    print(bonds)
    print(angles)
    print(dihedrals)

LAMMPSData("../aligned.mol2")
