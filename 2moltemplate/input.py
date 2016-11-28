from MDAnalysis import Universe
from MDAnalysis.topology.core import guess_angles, guess_dihedrals
import MDAnalysis.core.topologyobjects as top


class NonUniqueTypesError(ValueError):
    pass


class LAMMPSData:
    def __init__(self, filename, name="YourNameHere"):
        self.name = name
        u = Universe(filename)

        self.atoms = u.atoms
        self.bonds = u.bonds
        angles_ind = guess_angles(self.bonds)
        self.angles = top.TopologyGroup.from_indices(set(angles_ind), self.atoms,
                                                     bondclass=top.Angle, guessed=True)

        dihedrals_ind = guess_dihedrals(self.angles)
        self.dihedrals = top.TopologyGroup.from_indices(set(dihedrals_ind), self.atoms,
                                                        bondclass=top.Dihedral, guessed=True)

        self.build_derivatives()

    def build_derivatives(self):
        """
        These values should be calculated after init
        :return:
        """

        def _con_unique(con):
            result = True
            for c in con:
                if c[::-1] in con:
                    if not c == c[::-1]:
                        result = False
            return result

        def _get_types(group):
            if not _con_unique(set(group)):
                raise NonUniqueTypesError("{} types are not unique".format(type(group)))
            return list(set(group))

        self.atoms_types = sorted(list(set(self.atoms.types)))
        self.bonds_types = _get_types(self.bonds.types())
        self.angles_types = _get_types(self.angles.types())
        self.dihedrals_types = _get_types(self.dihedrals.types())

        default_types_map = lambda x: dict((k, k) for k in x)
        self.atoms_types_map = default_types_map(self.atoms_types)
        self.bonds_types_map = default_types_map(self.bonds_types)
        self.angles_types_map = default_types_map(self.angles_types)
        self.dihedrals_types_map = default_types_map(self.dihedrals_types)

    @property
    def atom_names(self):
        try:
            return self._atom_names
        except AttributeError:
            counter = dict((k, 0) for k in self.atoms.types)
            names = []
            for atom in self.atoms:
                inner_type = atom.type
                name = "{}_{}".format(inner_type, counter[inner_type])
                names.append(name)
                counter[inner_type] += 1
            self._atom_names = names
            return names

    def _write_atoms(self, descr, prefix="  "):
        head = '{}write("Data Atoms")'.format(prefix) + '{\n'
        tail = prefix + '}\n\n'

        def string_template(atom):
            inner_type = atom.type
            name = self.atom_names[atom.index]
            x, y, z = atom.position
            charge = atom.charge
            outer_type = self.atoms_types_map[inner_type]
            mol = "..."
            return "$atom:{name}  $mol:{mol} @atom:{type}  {charge} {x} {y} {z}".format(
                name=name,
                mol=mol,
                type=outer_type,
                charge=charge,
                x=x,
                y=y,
                z=z
            )

        descr.write(head)
        prefix_innter = "  " + prefix
        for atom in self.atoms:
            string = string_template(atom)
            descr.write(prefix_innter + string + "\n")
        descr.write(tail)

    def _write_bonds(self, descr, prefix="  "):
        head = '{}write("Data Bond List")'.format(prefix) + '{\n'
        tail = prefix + '}\n\n'

        def string_bond_template(bond):
            inner_type = "_".join(s for s in bond.type)
            bond_name = "{}_{}".format(inner_type, counter)
            atom_0 = self.atom_names[bond.atoms[0].index]
            atom_1 = self.atom_names[bond.atoms[1].index]

            return "$bond:{bond_name} $atom:{atom_0} $atom:{atom_1}".format(
                bond_name=bond_name,
                atom_0=atom_0,
                atom_1=atom_1
            )

        descr.write(head)
        prefix_inner = "  " + prefix
        counter = 0

        for bond in self.bonds:
            string = string_bond_template(bond)
            counter += 1
            descr.write(prefix_inner + string + "\n")
        descr.write(tail)

    def _write_atoms_types(self, descr, prefix="  "):
        template = prefix + "#{} : {}\n"
        for t in self.atoms_types:
            descr.write(template.format(t, self.atoms_types_map[t]))

    def _write_header(self, descr):
        try:
            descr.write(self.header +"\n")
        except AttributeError:
            pass
        descr.write(self.name + "{\n")

    def write_moltemplate(self, filename):
        with open(filename, "w") as out:
            self._write_header(out)
            self._write_atoms_types(out)
            self._write_atoms(out)
            self._write_bonds(out)
            out.write("}\n")

    def set_header(self, header):
        self.header = header

    def set_name(self, name):
        self.name = name

    def set_mappings(self, mappings):
        """
        Mappings for groupt types, i.e. @atom:80 (in OPLSAA) instead of  @atom:C.3
        :param mappings:
        :return:
        """

        def _set_one_mapping(grouptype):
            if mappings.get(grouptype, False):
                setattr(self, "{}_types_map".format(str(grouptype)), mappings.get(grouptype))

        for grouptype in mappings:
            _set_one_mapping(grouptype)

    def replace_atoms_bonded_with_X(self):
        pass
atom_mapping = {
    # C.2
    # C.3
    # C.ar
    # H :
    # O.2
    # O.3
    # S.O2
    #"C.2": 88,  # 47    CM    "Alkene H2-C="                 6    12.011    3
    #"C.2": 86,#   47    CM    "Alkene R2-C="                 6    12.011    3
    "C.2": 3,#    3    C     "Acetic Acid -COOH (UA)"       6    12.011    3
    "C.3": 81,  # 13    CT    "Alkane -CH2-"                 6    12.011    4
    "H": 85,  # 46    HC    "Alkane H-C"                   1     1.008    1

    "C.ar": 90,  # 48    CA    "Aromatic C"                   6    12.011    3
    "H.ar": 91,  # 49    HA    "Aromatic H-C"                 1     1.008    1

    "O.2": 223,  # 4    O     "Ketone C=O"                   8    15.999    1
    "O.3": 122,  # 20    OS    "Dialkyl Ether -O-"            8    15.999    2

    "O.3H": 96,#    5    OH    "Alcohol -OH"                  8    15.999    2
    "HO.3": 97, #   7    HO    "Alcohol -OH"                  1     1.008    1

    "S.O2": 434,  # 79    SY    "Sulfone R-SO2-R"             16    32.060    4
    "O.2S": 435,#   23    OY    "Sulfone R-SO2-R"              8    15.999    1

}

mapping = {"atoms":atom_mapping}

data = LAMMPSData("../aligned_H.mol2")
data.set_mappings(mappings=mapping)
data.set_name("Wedge inherits OPLSAA")
data.set_header('import "oplsaa.lt"    # <-- defines the "OPLSAA" force field\n')
data.write_moltemplate("../../moltemplate_files/wedge.lt")
a = data.atoms[65]
b = a.bonds.to_indices()[0]
#print(a.type, a.position, data.atoms[b[0]].type, data.atoms[b[1]].type)
#print(data.atoms[67])
print(data.atoms_types)
#print(data.atoms.types)
