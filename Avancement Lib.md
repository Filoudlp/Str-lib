| folder               |            file            | Etat  |           Reste à faire           | Commentaire                                              |
| -------------------- | :------------------------: | :---: | :-------------------------------: | -------------------------------------------------------- |
| .                    |          LICENSE           | 100 % |                                   | MIT License ofr the librairy                             |
| .                    |         README.md          | 50 %  |                                   | explanation of the librairy                              |
| .                    |     Avancement Lib.md      | 50 %  |                                   | evolution of the Str Lib coding                          |
| .                    |       pyproject.toml       | 100 % |                                   | Installation of the librairy "-pip install ." to install |
| core                 |       coefficient.py       | 75 %  |           Good question           | I don't know if this class is usefull and how to use it  |
| core                 |         formula.py         | 100 % |                 /                 | File to create dict with the result of the calculation   |
| core /mat            |      mat_concrete.py       | 100 % |                 /                 | all property of concrete material                        |
| core /mat            |    mat_reinforcement.py    | 100 % |                 /                 | all property of reinforcement material                   |
| core /mat            |        mat_steel.py        | 100 % |                 /                 | all property of steel material                           |
| core /mat            |        materials.py        | 100 % |                 /                 | Base class for material property                         |
| core /sec            |        sec_i_h_u.py        | 100 % |                 /                 | all property of I section, H section, U section section  |
| core /sec            |         sec_rec.py         | 100 % |                 /                 | all property of rectangulaire section                    |
| core /sec            |         section.py         | 100 % |                 /                 | Base class for section property                          |
| core /sec_mat        |      sec_mat_i_h_u.py      | 95 %  | Convert __str__ to formula result | All property about the section and mat for steel section |
| core /sec_mat        |       sec_mat_rc.py        | 90 %  |     Return with formulaResult     | All property about the section and mat for RC            |
| data                 |                            |       |                                   |                                                          |
| norme/EC1            |                            |       |                                   |                                                          |
| norme/EC2            |                            |       |                                   |                                                          |
| norme/EC2/durability |        enrobage.py         |       |                                   |                                                          |
| norme/EC2/durability |       espacement.py        |       |                                   |                                                          |
| norme/EC2/els        |       contraintes.py       |       |                                   |                                                          |
| norme/EC2/els        |       fissuration.py       |       |                                   |                                                          |
| norme/EC2/els        |         flèche.py          |       |                                   |                                                          |
| norme/EC2/elu        |     bielles_tirants.py     |       |                                   |                                                          |
| norme/EC2/elu        |       compression.py       |       |                                   |                                                          |
| norme/EC2/elu        |    effort_tranchant.py     |       |                                   |                                                          |
| norme/EC2/elu        |         flexion.py         |       |                                   |                                                          |
| norme/EC2/elu        |     interaction_v_t.py     |       |                                   |                                                          |
| norme/EC2/elu        |      poiconnement.py       |       |                                   |                                                          |
| norme/EC2/elu        |         torsion.py         |       |                                   |                                                          |
| norme/EC3            |     classification.py      |       |                                   |                                                          |
| norme/EC3            |      imperfection.py       |       |                                   |                                                          |
| norme/EC3/buckling   |     buckling_curves.py     |       |                                   |                                                          |
| norme/EC3/buckling   |    flexural_buckling.py    |       |                                   |                                                          |
| norme/EC3/buckling   |     interaction_MN.py      |       |                                   |                                                          |
| norme/EC3/buckling   |    lateral_torsional.py    |       |                                   |                                                          |
| norme/EC3/element    |       steel_beam.py        |       |                                   |                                                          |
| norme/EC3/els        |       deflection.py        |       |                                   |                                                          |
| norme/EC3/els        |          drift.py          |       |                                   |                                                          |
| norme/EC3/els        |         limits.py          |       |                                   |                                                          |
| norme/EC3/els        |        vibration.py        |       |                                   |                                                          |
| norme/EC3/elu        |         bending.py         |       |                                   |                                                          |
| norme/EC3/elu        |        combined.py         |       |                                   |                                                          |
| norme/EC3/elu        |       compression.py       |       |                                   |                                                          |
| norme/EC3/elu        |          shear.py          |       |                                   |                                                          |
| norme/EC3/elu        |        traction.py         |       |                                   |                                                          |
| norme/EC4            |                            |       |                                   |                                                          |
| norme/EC5            |                            |       |                                   |                                                          |
| norme/EC6            |                            |       |                                   |                                                          |
| norme/EC7            |                            |       |                                   |                                                          |
| norme/EC8            |                            |       |                                   |                                                          |
| rdm                  |             ?              |       |       Missing 2D/3D element       | The FEM package only do beam for now                     |
| rdm                  |         element.py         | 100 % |                                   | Only include 1D element (barre element)                  |
| rdm                  |          loads.py          | 80 %  | Check thermal and prestress load  | All load that can be use for FEM                         |
| rdm                  |          mesh.py           | 100 % |                                   | Only include 1D element (barre element)                  |
| rdm                  |          model.py          | 100 % |                                   | Only include 1D element (barre element)                  |
| rdm                  |          node.py           | 100 % |                 /                 | Class to create node for the FEM package                 |
| rdm                  |         solver.py          | 100%  |                                   | Only include 1D element (barre element)                  |
| rdm                  |          test.py           | 100 % |                 /                 | Class to test the Rdm package                            |
| ressource            |          chs.json          | 100 % |                 /                 | CHS section                                              |
| ressource            |          HD.json           | 100 % |                 /                 | HD section                                               |
| ressource            |          HE.json           | 100 % |                 /                 | HE section                                               |
| ressource            |          HL.json           | 100 % |                 /                 | HL section                                               |
| ressource            |          HP.json           | 100 % |                 /                 | HP section                                               |
| ressource            |          IPE.json          | 100 % |                 /                 | IPE section                                              |
| ressource            |          IPN.json          | 100 % |                 /                 | IPN section                                              |
| ressource            |          Le.json           | 100 % |                 /                 | Cornière ail égale                                       |
| ressource            |          Lie.json          | 100 % |                 /                 | Cornière ail inégale                                     |
| ressource            |        rhs_shs.json        | 100 % |                 /                 | RHS/SHS section                                          |
| ressource            | section-arcelor-mital.xlsx | 100 % |                 /                 | tableau excel des profilés                               |
| ressource            |     Sections_MB_*.pdf      | 100 % |                 /                 | Catalogue arcelors mital                                 |
| ressource            |           U.json           | 100 % |                 /                 | U section                                                |
| ressource            |          UPE.json          | 100 % |                 /                 | UPE section                                              |
| ressource            |          UPN.json          | 100 % |                 /                 | UPN section                                              |
| utility              |       excel2json.py        | 100 % |                 /                 | converte excel file to Json                              |
| utility              |      lookupinjson.py       | 100 % |                 /                 | get data from json                                       |

