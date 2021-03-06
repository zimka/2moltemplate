from .generic import LTGeneric
from .utils import NonUniqueTypesError, MOL2Reader


class LTRepresent(LTGeneric):

    def __init__(self, atoms, bonds, name="YourNameHere", ancestor_name=None, imports=None):
        self.name = name
        self.ancestor_name = ancestor_name
        self.atoms = atoms
        self.bonds = bonds
        self.imports = imports
        self._build_derivatives()

    def _build_derivatives(self):
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

        default_types_map = lambda x: dict((k, k) for k in x)
        self.atoms_types_map = default_types_map(self.atoms_types)
        self.bonds_types_map = default_types_map(self.bonds_types)

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

    def write_lt(self, filename):
        with open(filename, "w") as out:
            self._write_header(out)
            self._write_atoms_types(out)
            self._write_atoms(out)
            self._write_bonds(out)
            self._write_footer(out)

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

