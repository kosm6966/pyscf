import unittest 
import numpy as np

from pyscf.pbc import gto as pbcgto
from pyscf.pbc import scf as pbchf
import pyscf.pbc.tools
import pyscf.pbc.tools.pyscf_ase as pyscf_ase

import ase
import ase.lattice
import ase.dft.kpoints

def make_primitive_cell(ngs):
    from ase.lattice import bulk
    ase_atom = bulk('C', 'diamond', a=3.5668)

    cell = pbcgto.Cell()
    cell.unit = 'A'
    cell.atom = pyscf_ase.ase_atoms_to_pyscf(ase_atom)
    cell.h = ase_atom.cell

    cell.basis = 'gth-szv'
    cell.pseudo = 'gth-pade'
    cell.gs = np.array([ngs,ngs,ngs])

    #cell.verbose = 4
    cell.build()
    return cell

class KnowValues(unittest.TestCase):
    def test_kpt_vs_supercell(self):
        ngs = 3
        nk = (3, 1, 1)
        cell = make_primitive_cell(ngs)
        scaled_kpts = ase.dft.kpoints.monkhorst_pack(nk)
        abs_kpts = cell.get_abs_kpts(scaled_kpts)
        kmf = pbchf.KRHF(cell, abs_kpts)
        #kmf.verbose = 7
        ekpt = kmf.scf()

        supcell = pyscf.pbc.tools.super_cell(cell, nk)
        supcell.gs = np.array([nk[0]*ngs + (nk[0]-1)//2, 
                               nk[1]*ngs + (nk[1]-1)//2,
                               nk[2]*ngs + (nk[2]-1)//2])
        #supcell.verbose = 7
        supcell.build()

        scaled_gamma = ase.dft.kpoints.monkhorst_pack((1,1,1))
        gamma = supcell.get_abs_kpts(scaled_gamma)
        mf = pbchf.KRHF(supcell, gamma)
        #mf.verbose = 7
        esup = mf.scf()/np.prod(nk)

        print "kpt sampling energy =", ekpt
        print "supercell energy    =", esup
        print "difference          =", ekpt-esup
        self.assertAlmostEqual(ekpt, esup, 8)

if __name__ == '__main__':
    print("Full Tests for pbc.dft.krks")
    unittest.main()
