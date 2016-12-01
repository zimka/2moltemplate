from tran2lt import MOL2Reader, LTRepresent


if __name__ == "__main__":
    atom_mapping = {
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
    mol2 = MOL2Reader("aligned_H.mol2")
    lt = LTRepresent(mol2.atoms, mol2.bonds)
    lt.set_mappings(mappings=mapping)
    lt.set_name("Wedge inherits OPLSAA")
    lt.set_imports('import "oplsaa.lt"    # <-- defines the "OPLSAA" force field\n')
    lt.write_moltemplate("../wedge_test.lt")
    a = lt.atoms[65]
    b = a.bonds.to_indices()[0]
    #print(a.type, a.position, data.atoms[b[0]].type, data.atoms[b[1]].type)
    #print(data.atoms[67])
    print(lt.atoms_types)
    #print(data.atoms.types)
