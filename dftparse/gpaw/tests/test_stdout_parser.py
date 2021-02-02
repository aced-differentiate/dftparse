import os
import unittest

from dftparse.util import remove_empty_dicts
from dftparse.gpaw.stdout_parser import GpawStdOutputParser


class TestGpawStdOutputParser(unittest.TestCase):
    """Unit tests for parsing the standard output from GPAW runs
    (:class:`dftparse.gpaw.stdout_parser.GpawStdOutputParser`)."""

    def setUp(self):
        self.parser = GpawStdOutputParser()

    def test_parse_gpaw_version(self):
        raw_stdout = """
  ___ ___ ___ _ _ _
 |   |   |_  | | | |
 | | | | | . | | | |
 |__ |  _|___|_____|  19.8.1
 |___|_|
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]["gpaw_version"], "19.8.1")

    def test_parse_username(self):
        raw_stdout = """

User:   lkavalsk@c009
Date:   Tue Sep  1 17:16:57 2020
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]["username"], "lkavalsk@c009")

    def test_parse_python_version(self):
        raw_stdout = """
Pid:    31729
Python: 3.7.7
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]["python_version"], "3.7.7")

    def test_parse_gpaw_package(self):
        raw_stdout = """
Python: 3.7.7
gpaw:   /home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/gpaw
_gpaw:  /home/lkavalsk/.conda/envs/gp2/bin/gpaw-python
ase:    /home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/ase (version 3.19.1)
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(
            results[1]["gpaw_pkg_location"],
            "/home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/gpaw",
        )
        self.assertEqual(
            results[1]["gpaw_bin_location"],
            "/home/lkavalsk/.conda/envs/gp2/bin/gpaw-python",
        )

    def test_parse_ase_package(self):
        raw_stdout = """
ase:    /home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/ase (version 3.19.1)
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(
            results[0]["ase_pkg_location"],
            "/home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/ase",
        )
        self.assertEqual(results[0]["ase_version"], "3.19.1")

    def test_parse_numpy_package(self):
        raw_stdout = """
numpy:  /home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/numpy (version 1.18.1)
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(
            results[0]["numpy_pkg_location"],
            "/home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/numpy",
        )
        self.assertEqual(results[0]["numpy_version"], "1.18.1")

    def test_parse_scipy_package(self):
        raw_stdout = """
scipy:  /home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/scipy (version 1.4.1)
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(
            results[0]["scipy_pkg_location"],
            "/home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/scipy",
        )
        self.assertEqual(results[0]["scipy_version"], "1.4.1")

    def test_parse_libxc_version(self):
        raw_stdout = """
scipy:  /home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/scipy (version 1.4.1)
libxc:  3.0.0
units:  Angstrom and eV
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[1]["libxc_version"], "3.0.0")

    def test_parse_ncores(self):
        raw_stdout = """
units:  Angstrom and eV
cores:  32

"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]["ncores"], "32")

    def test_parse_gpaw_setup_files(self):
        raw_stdout = """
Pt-setup:
  name: Platinum
  id: 5ed695806aff0c961dba1a84acd7f4b2
  Z: 78
  valence: 16
  core: 62
  charge: 0.0
  file: /home/azeeshan/software/gpaw-setups-0.9.20000/Pt.PBE.gz
  compensation charges: gauss, rc=0.41, lmax=2
  cutoffs: 2.26(filt), 2.26(core),
  valence states:
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(
            results[0]["gpaw_setup_file"],
            "/home/azeeshan/software/gpaw-setups-0.9.20000/Pt.PBE.gz",
        )

    def test_parse_timings(self):
        raw_stdout = """
Timing:                                      incl.     excl.
-------------------------------------------------------------------
Density initialized from wave functions:     4.321     3.840   0.0% |
 Symmetrize density:                         0.481     0.481   0.0% |
Forces:                                    134.251   134.251   0.9% |
Hamiltonian:                                68.707     0.002   0.0% |
 Atomic:                                     0.007     0.007   0.0% |
  XC Correction:                             0.000     0.000   0.0% |
 Calculate atomic Hamiltonians:              0.008     0.008   0.0% |
 Communicate:                               10.368    10.368   0.1% |
 Hartree integrate/restrict:                 0.053     0.053   0.0% |
 Initialize Hamiltonian:                     0.000     0.000   0.0% |
 Poisson:                                    4.036     1.134   0.0% |
  Communicate bwd 0:                         0.319     0.319   0.0% |
  Communicate bwd 1:                         0.333     0.333   0.0% |
  Communicate fwd 0:                         0.198     0.198   0.0% |
  Communicate fwd 1:                         0.322     0.322   0.0% |
  fft:                                       1.606     1.606   0.0% |
  fft2:                                      0.125     0.125   0.0% |
 XC 3D grid:                                54.222     6.822   0.0% |
  VdW-DF integral:                          47.399     2.402   0.0% |
   Convolution:                              3.438     3.438   0.0% |
   FFT:                                      1.805     1.805   0.0% |
   gather:                                  17.984    17.984   0.1% |
   hmm1:                                     1.259     1.259   0.0% |
   hmm2:                                     1.257     1.257   0.0% |
   iFFT:                                     1.894     1.894   0.0% |
   potential:                               10.903     0.243   0.0% |
    collect:                                 1.756     1.756   0.0% |
    p1:                                      5.431     5.431   0.0% |
    p2:                                      2.022     2.022   0.0% |
    sum:                                     1.450     1.450   0.0% |
   splines:                                  6.456     6.456   0.0% |
 vbar:                                       0.011     0.011   0.0% |
LCAO initialization:                         2.892     0.273   0.0% |
 LCAO eigensolver:                           1.235     0.001   0.0% |
  Calculate projections:                     0.000     0.000   0.0% |
  DenseAtomicCorrection:                     0.000     0.000   0.0% |
  Distribute overlap matrix:                 0.788     0.788   0.0% |
  Orbital Layouts:                           0.444     0.444   0.0% |
  Potential matrix:                          0.000     0.000   0.0% |
  Sum over cells:                            0.002     0.002   0.0% |
 LCAO to grid:                               0.743     0.743   0.0% |
 Set positions (LCAO WFS):                   0.640     0.212   0.0% |
  Basic WFS set positions:                   0.001     0.001   0.0% |
  Basis functions set positions:             0.000     0.000   0.0% |
  P tci:                                     0.001     0.001   0.0% |
  ST tci:                                    0.041     0.041   0.0% |
  mktci:                                     0.384     0.384   0.0% |
Redistribute:                                0.020     0.020   0.0% |
SCF-cycle:                               15315.973   373.667   2.4% ||
 Davidson:                               13520.996  7032.321  44.6% |-----------------|
  Apply hamiltonian:                       365.017   365.017   2.3% ||
  Subspace diag:                           891.118     0.234   0.0% |
   calc_h_matrix:                          390.833   100.903   0.6% |
    Apply hamiltonian:                     289.931   289.931   1.8% ||
   diagonalize:                            319.279   319.279   2.0% ||
   rotate_psi:                             180.771   180.771   1.1% |
  calc. matrices:                         2858.009  1221.158   7.7% |--|
   Apply hamiltonian:                     1636.851  1636.851  10.4% |---|
  diagonalize:                            2044.229  2044.229  13.0% |----|
  rotate_psi:                              330.302   330.302   2.1% ||
 Density:                                   69.865     0.011   0.0% |
  Atomic density matrices:                  27.810    27.810   0.2% |
  Mix:                                      10.468    10.468   0.1% |
  Multipole moments:                         0.698     0.698   0.0% |
  Pseudo density:                           30.879    15.350   0.1% |
   Symmetrize density:                      15.529    15.529   0.1% |
 Hamiltonian:                             1308.109     0.062   0.0% |
  Atomic:                                    0.123     0.122   0.0% |
   XC Correction:                            0.002     0.002   0.0% |
  Calculate atomic Hamiltonians:             0.103     0.103   0.0% |
  Communicate:                             218.515   218.515   1.4% ||
  Hartree integrate/restrict:                1.344     1.344   0.0% |
  Poisson:                                  53.567    23.629   0.1% |
   Communicate bwd 0:                        6.283     6.283   0.0% |
   Communicate bwd 1:                        7.108     7.108   0.0% |
   Communicate fwd 0:                        3.979     3.979   0.0% |
   Communicate fwd 1:                        7.957     7.957   0.1% |
   fft:                                      2.140     2.140   0.0% |
   fft2:                                     2.472     2.472   0.0% |
  XC 3D grid:                             1034.120   147.698   0.9% |
   VdW-DF integral:                        886.422    45.589   0.3% |
    Convolution:                            64.035    64.035   0.4% |
    FFT:                                    34.434    34.434   0.2% |
    gather:                                430.076   430.076   2.7% ||
    hmm1:                                   25.121    25.121   0.2% |
    hmm2:                                   24.383    24.383   0.2% |
    iFFT:                                   34.945    34.945   0.2% |
    potential:                             227.836     4.600   0.0% |
     collect:                               37.394    37.394   0.2% |
     p1:                                   101.914   101.914   0.6% |
     p2:                                    38.076    38.076   0.2% |
     sum:                                   45.853    45.853   0.3% |
    splines:                                 0.003     0.003   0.0% |
  vbar:                                      0.274     0.274   0.0% |
 Orthonormalize:                            43.335     0.012   0.0% |
  calc_s_matrix:                             3.110     3.110   0.0% |
  inverse-cholesky:                         35.654    35.654   0.2% |
  projections:                               0.003     0.003   0.0% |
  rotate_psi_s:                              4.557     4.557   0.0% |
Set symmetry:                                0.005     0.005   0.0% |
Other:                                     244.268   244.268   1.5% ||
-------------------------------------------------------------------
Total:                                             15770.436 100.0%
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]["wf_initialization_time"], "4.321")
        self.assertEqual(results[0]["forces_time"], "134.251")
        self.assertEqual(results[0]["lcao_initialization_time"], "2.892")
        self.assertEqual(results[0]["scf_cycle_time"], "15315.973")
        self.assertEqual(results[0]["other_time"], "244.268")

    def test_parse_memory_usage(self):
        raw_stdout = """
Total:                                             15770.436 100.0%

Memory usage: 446.11 MiB
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]["memory_usage"], "446.11 MiB")

    def test_parse_run_date(self):
        raw_stdout = """
Date:   Tue Sep  1 17:16:57 2020
Arch:   x86_64
Date: Tue Sep  1 21:39:47 2020
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]["run_date"], "Tue Sep 1 17:16:57 2020")
        self.assertEqual(results[1]["run_date"], "Tue Sep 1 21:39:47 2020")

    def test_mp_k_mesh(self):
        raw_stdout = """
16 k-points: 4 x 4 x 1 Monkhorst-Pack grid
6 k-points in the irreducible part of the Brillouin zone
       k-points in crystal coordinates                weights
   0:     0.12500000   -0.12500000    0.00000000          2/16
   1:     0.12500000    0.12500000    0.00000000          2/16
   2:     0.37500000   -0.37500000    0.00000000          2/16
   3:     0.37500000   -0.12500000    0.00000000          4/16
   4:     0.37500000    0.12500000    0.00000000          4/16
   5:     0.37500000    0.37500000    0.00000000          2/16
"""
        lines = raw_stdout.split("\n")
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]["mp_k_mesh"], (4, 4, 1))


if __name__ == "__main__":
    unittest.main()
