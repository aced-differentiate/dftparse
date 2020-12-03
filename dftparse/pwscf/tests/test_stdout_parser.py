import unittest

from dftparse.pwscf.stdout_parser import PwscfStdOutputParser


class TestPwscfStdOutputParser(unittest.TestCase):
    """Unit tests for parsing the standard output from PWscf runs
    (:class:`dftparse.pwscf.stdout_parser.PwscfStdOutputParser`)."""

    def setUp(self):
        self.parser = PwscfStdOutputParser()

    def test_parse_header(self):
        """Test parsing the header of a PWscf standard output file."""
        # a "regular" header
        lines = ['   Program PWSCF v.6.2.2 starts on  9May2018 at 12:36:24']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]['version'], '6.2.2')
        self.assertEqual(results[0]['start_date'], '9May2018')
        self.assertEqual(results[0]['start_time'], '12:36:24')

        # a header with SVN branch info (and messy timestamp)
        lines = ['     Program PWSCF v.6.1 (svn rev. 13591M) starts on '
                 '12Jul2017 at 10:20: 0']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]['version'], '6.1')
        self.assertEqual(results[0]['start_date'], '12Jul2017')
        self.assertEqual(results[0]['start_time'], '10:20:')

    def test_parse_input_filename(self):
        """Test parsing the name of the input file."""
        lines = ['     Reading input from vc-relax2.in    ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]['input file'], 'vc-relax2.in')

    def test_parse_pseudopotential(self):
        """Test parsing pseudopotential information."""
        lines = """
            PseudoPot. # 1 for O  read from file:
            /home/giannozz/trunk/espresso/test-suite/..//pseudo/O.pz-rrkjus.UPF
            MD5 check sum: 24fb942a68ef5d262e498166c462ef4a
            Pseudo is Ultrasoft, Zval =  6.0
            l(3) =   1
            l(4) =   1
            Q(r) pseudized with 0 coefficients


            PseudoPot. # 2 for Fe read from file:
            /home/giannozz/trunk/espresso/test-suite/..//pseudo/Fe.pz-nd-rrkjus.UPF
        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        list_of_psps = [r['pseudopotential file'] for r in results]
        self.assertTrue('O.pz-rrkjus.UPF' in list_of_psps)
        self.assertTrue('Fe.pz-nd-rrkjus.UPF' in list_of_psps)

    def test_parse_bravais_lattice(self):
        """Test parsing the bravais-lattice index."""
        lines = ['    bravais-lattice index     =            0\n']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]['bravais-lattice index'], 0)

    def test_parse_lattice_parameter(self):
        """Test parsing the lattice parameter and units."""
        lines = ['    lattice parameter (alat)  =       8.1900  a.u.']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['lattice parameter'], 8.1900)
        self.assertEqual(results[0]['lattice parameter units'], 'a.u.')

    def test_parse_cell_vectors(self):
        """Test parsing the cell vectors."""
        # from the crystal axes block
        lines = """
            crystal axes: (cart. coord. in units of alat)
               a(1) = (   1.000000   0.000000   0.000000 )
               a(2) = (   0.495175   0.868793   0.000000 )
               a(3) = (   0.495175   0.287729   0.819765 )
        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]['cell vectors units'],
                         'cart. coord. in units of alat')
        self.assertAlmostEqual(results[0]['cell vectors'][1][0], 0.495175)
        self.assertAlmostEqual(results[0]['cell vectors'][2][2], 0.819765)

        # from the CELL PARAMETERS card
        lines = """
            CELL_PARAMETERS (alat=  7.01033623)
               1.030899271  -0.007085701  -0.005022645
               0.504319227   0.899146860  -0.005022223
               0.504319091   0.293042380   0.850068704

            CELL_PARAMETERS (alat=  7.01033623)
               1.052821713   0.008877209   0.006292278
               0.529043139   0.910288488   0.006292512
               0.529043092   0.307408443   0.856834348
        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]['cell vectors units'], 'alat=  7.01033623')
        self.assertAlmostEqual(results[1]['cell vectors'][0][0], 1.052821713)
        self.assertAlmostEqual(results[1]['cell vectors'][1][1], 0.910288488)
        self.assertAlmostEqual(results[1]['cell vectors'][2][1], 0.307408443)

    def test_parse_unit_cell_volume(self):
        """Test parsing the unit-cell volume."""
        # initial unit-cell volume
        lines = ['   unit-cell volume          =     245.3705 (a.u.)^3  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['unit-cell volume'], 245.3705)
        self.assertEqual(results[0]['unit-cell volume units'], '(a.u.)^3')

        # subsequent unit-cell volumes (e.g. in a vc-relax calculation)
        lines = """
            new unit-cell volume =    232.0702 (a.u.)^3
                new unit-cell volume =   232.07022 a.u.^3 (   34.38926 Ang^3 )
        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['unit-cell volume'], 232.0702)
        self.assertAlmostEqual(results[1]['unit-cell volume'], 232.07022)
        self.assertEqual(results[0]['unit-cell volume units'], '(a.u.)^3')
        self.assertEqual(results[1]['unit-cell volume units'], 'a.u.^3')

    def test_parse_n_atoms_per_cell(self):
        """Test parsing the number of atoms/unit-cell."""
        lines = ['  number of atoms/cell      =            2  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]['number of atoms/cell'], 2)

    def test_parse_n_atom_types(self):
        """Test parsing the number of atom types in the structure."""
        lines = ['  number of atomic types    =            4  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]['number of atom types'], 4)

    def test_parse_n_electrons(self):
        """Test parsing the number of electrons in the calculation."""
        lines = ['  number of electrons       =        10.00  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['number of electrons'], 10.00)
        # spin-polarized case
        lines = [' number of electrons  =  16.00 (up: 8.00, down: 8.00) ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['number of electrons'], 16.00)

    def test_parse_kinetic_energy_cutoff(self):
        """Test parsing the kinetic energy cutoff and units."""
        lines = ['  kinetic-energy cutoff     =      25.0000  Ry  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['kinetic-energy cutoff'], 25.0)
        self.assertEqual(results[0]['kinetic-energy cutoff units'], 'Ry')

    def test_parse_charge_density_cutoff(self):
        """Test parsing the charge density cutoff and units."""
        lines = ['  charge density cutoff     =     100.0000  Ry  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['charge density cutoff'], 100.0)
        self.assertEqual(results[0]['charge density cutoff units'], 'Ry')

    def test_parse_mixing_beta(self):
        """Test parsing the mixing beta value."""
        lines = ['  mixing beta               =       0.7000  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['mixing beta'], 0.7)

    def test_parse_scf_conv_threshold(self):
        """Test parsing the electronic (scf) convergence threshold."""
        lines = ['  convergence threshold     =      1.0E-07  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['scf convergence threshold'], 1E-7)

    def test_parse_ionic_conv_threshold(self):
        """Test parsing the energy, force, and stress convergence thresholds
        for variable cell relaxations."""
        # Wentzcovitch damped cell dynamics minimization
        lines = """
               Wentzcovitch Damped Cell Dynamics Minimization:
                   convergence thresholds EPSE = 1.00E-04  EPSF = 1.00E-03
        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(
            results[0]['ionic energy convergence threshold'], 1E-4)
        self.assertAlmostEqual(
            results[0]['forces convergence threshold'], 1E-3)

        # BFGS geometry optimization
        lines = [' (criteria: energy <  1.0E-08 Ry, force <  1.0E-04Ry/Bohr,'
                 ' cell <  5.0E-01kbar)',
                 ' (criteria: energy < 0.10E-03, force < 0.10E-02,']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(
            results[0]['ionic energy convergence threshold'], 1E-8)
        self.assertAlmostEqual(
            results[0]['forces convergence threshold'], 1E-4)
        self.assertAlmostEqual(
            results[0]['pressure convergence threshold'], 0.5)
        self.assertAlmostEqual(
            results[1]['ionic energy convergence threshold'], 1E-4)
        self.assertAlmostEqual(
            results[1]['forces convergence threshold'], 1E-3)
        self.assertTrue('cell criteria' not in results[1])

    def test_parse_xc(self):
        """Test parsing the exchange-correlation related information."""
        lines = ['   Exchange-correlation      =  SLA  PZ   '
                 'NOGX NOGC ( 1  1  0  0 0 0)']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertListEqual(results[0]['exchange-correlation'],
                             ['SLA', 'PZ', 'NOGX', 'NOGC'])

    def test_parse_kpoints_block(self):
        """Testing parsing the list of k-points used and their weights."""
        lines = """
            number of k points= 10  gaussian smearing, width (Ry)= 0.0050
                           cart. coord. in units 2pi/alat
            k(   1) = (   0.0000000   0.0000000   0.1534638), wk =   0.0625000
            k(   2) = (  -0.1436461  -0.2488023   0.2557731), wk =   0.1875000
            k(   3) = (   0.2872922   0.4976046  -0.0511547), wk =   0.1875000
            k(   4) = (   0.1436461   0.2488023   0.0511546), wk =   0.1875000
            k(   5) = (  -0.2872922   0.0000000   0.3580823), wk =   0.1875000
            k(   6) = (   0.1436461   0.7464070   0.0511546), wk =   0.3750000
            k(   7) = (   0.0000000   0.4976046   0.1534638), wk =   0.3750000
            k(   8) = (   0.5745844   0.0000000  -0.2557731), wk =   0.1875000
            k(   9) = (   0.0000000   0.0000000   0.4603915), wk =   0.0625000
            k(  10) = (   0.4309383   0.7464070   0.1534638), wk =   0.1875000

        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]['number of k-points'], 10)
        self.assertEqual(results[0]['k-points coordinate system'],
                         'cart. coord. in units 2pi/alat')
        self.assertEqual(len(results[0]['list of k-points']), 10)
        self.assertAlmostEqual(results[0]['list of k-points'][0][2], 0.1534638)
        self.assertEqual(len(results[0]['list of k-point weights']), 10)
        self.assertAlmostEqual(results[0]['list of k-point weights'][5], 0.375)
        self.assertEqual(results[0]['smearing type'], 'gaussian')
        self.assertAlmostEqual(results[0]['smearing width'], 0.005)
        self.assertEqual(results[0]['smearing width units'], 'Ry')
        # low verbosity case when k-points are not printed
        lines = """
    number of k points=   146  Methfessel-Paxton smearing, width (Ry)=  0.0037

    Number of k-points >= 100: set verbosity='high' to print them.

    Dense  grid:   692393 G-vectors     FFT dimensions: (  50,  50, 625)
    """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]['number of k-points'], 146)
        self.assertTrue('list of k-points' not in results[0])

    def test_parse_fermi_energy(self):
        """Test parsing the Fermi energy."""
        lines = ['    the Fermi energy is    13.1968 ev  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['fermi energy'], 13.1968)
        self.assertEqual(results[0]['fermi energy units'], 'ev')

    def test_parse_total_energy(self):
        """Test parsing the (self-consistent) total energy(/ies)."""
        lines = """
            !    total energy              =     -25.44012218 Ry
                 Harris-Foulkes estimate   =     -25.44012218 Ry
                 estimated scf accuracy    <       0.00000001 Ry
                The total energy is the sum of the following terms:
                total energy              =     -25.47727525 Ry
                total energy              =     -25.48675494 Ry
            !    total energy              =     -25.48654757 Ry
            !    total energy              =     -25.49507167 Ry
            !    total energy              =     -25.50089935 Ry
        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        # check that only scf total energies are parsed
        self.assertEqual(len(results), 4)
        self.assertAlmostEqual(results[3]['total energy'], -25.50089935)
        self.assertEqual(results[2]['total energy units'], 'Ry')

    def test_gen_energy_contrib(self):
        """Test parsing various contributions to the total energy."""
        lines = """
            !    total energy              =    -439.62704582 Ry
                 Harris-Foulkes estimate   =    -439.62704606 Ry
                 estimated scf accuracy    <       0.00000033 Ry

                 The total energy is the sum of the following terms:

                 one-electron contribution =     -13.58082604 Ry
                 hartree contribution      =      68.24717960 Ry
                 xc contribution           =    -123.45729278 Ry
                 ewald contribution        =    -370.83610660 Ry
                 smearing contrib. (-TS)   =       0.00652398 Ry

                 convergence has been achieved in   8 iterations
        """.split("\n")
        results = list(self.parser.parse(lines))
        flattened = {}
        for r in results:
            flattened.update(r)
        self.assertAlmostEqual(flattened['total energy'], -439.62704582)
        self.assertEqual(flattened['total energy units'], 'Ry')
        self.assertAlmostEqual(
            flattened['one-electron energy contribution'], -13.58082604)
        self.assertEqual(
            flattened['one-electron energy contribution units'], 'Ry')
        self.assertAlmostEqual(
            flattened['smearing energy contribution'], 0.00652398)
        self.assertEqual(flattened['smearing energy contribution units'], 'Ry')

    def test_parse_hubbard_energy(self):
        """Test parsing the Hubbard energy contribution to total energy."""
        lines = """
            Hubbard energy            =       0.31375716 Ry
            smearing contrib. (-TS)   =      -0.00404068 Ry

        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['Hubbard energy contribution'],
                               0.31375716)
        self.assertEqual(results[0]['Hubbard energy contribution units'],
                         'Ry')

    def test_parse_force_short(self):
        """Test parsing forces without contributions."""
        lines = """
            Forces acting on atoms (Ry/au):

            atom    1 type  1   force =  -0.00147138   0.00084950  0.00000000
            atom    2 type  1   force =   0.00137999  -0.00079673  0.00000000
            atom    3 type  1   force =   0.00147138  -0.00084950  0.00000000
            atom    4 type  1   force =  -0.00137999   0.00079673  0.00000000

            Total force =     0.003294     Total SCF correction =     0.000014
        """.split("\n")
        results = list(self.parser.parse(lines))
        flattened = {}
        for r in results:
            flattened.update(r)
        self.assertEqual(flattened['force units'], 'Ry/au')
        self.assertAlmostEqual(flattened['total force'], 0.003294)
        self.assertAlmostEqual(flattened['total SCF correction'], 0.000014)
        self.assertAlmostEqual(flattened['atomic forces'][3][0], -0.00137999)
        self.assertEqual(flattened['atomic species index for forces'][3], 1)

    def test_parse_forces(self):
        """Test parsing forces acting on atoms (including contributions)."""
        lines = """
            Forces acting on atoms (Ry/au):

            atom    1 type  1   force =   0.00000000  0.00000000   0.00000000
            atom    2 type  2   force =   0.00000000  0.00000000   0.00000054
            The non-local contrib.  to forces
            atom    1 type  1   force =   0.00000000  0.00000000   0.00000000
            atom    2 type  2   force =   0.00000000  0.00000000  -0.00000016
            The ionic contribution  to forces
            atom    1 type  1   force =   0.00000000  0.00000000   0.00000000
            atom    2 type  2   force =   0.00000000  0.00000000   0.00000000
            The local contribution  to forces
            atom    1 type  1   force =   0.00000000  0.00000000   0.00000000
            atom    2 type  2   force =   0.00000000  0.00000000   0.00000187
            The core correction contribution to forces
            atom    1 type  1   force =   0.00000000  0.00000000   0.00000000
            atom    2 type  2   force =   0.00000000  0.00000000   0.00000000
            The Hubbard contrib.    to forces
            atom    1 type  1   force =   0.00000000  0.00000000   0.00000000
            atom    2 type  2   force =   0.00000000  0.00000000   0.00000000
            The SCF correction term to forces
            atom    1 type  1   force =   0.00000000  0.00000000   0.00000000
            atom    2 type  2   force =   0.00000000  0.00000000  -0.00000117

            Total force =     0.011752   Total SCF correction =     0.000072
        """.split("\n")
        results = list(self.parser.parse(lines))
        flattened = {}
        for r in results:
            flattened.update(r)
        self.assertEqual(flattened['force units'], 'Ry/au')
        self.assertAlmostEqual(flattened['total force'], 0.011752)
        self.assertAlmostEqual(flattened['total SCF correction'], 0.000072)
        self.assertAlmostEqual(flattened['atomic forces'][1][2], 0.00000054)
        self.assertAlmostEqual(
            flattened['non-local contribution to forces'][1][2], -0.00000016)
        self.assertAlmostEqual(
            flattened['SCF correction term to forces'][1][2], -0.00000117)
        self.assertEqual(flattened['atomic species index for forces'][1], 2)

    def test_parse_stress_and_pressure(self):
        """Test parsing the stress tensor and hydrostatic pressure."""
        lines = """
               total   stress  (Ry/bohr**3)             (kbar)     P=  -77.72
            -0.00055293   0.00000000   0.00000000  -81.34      0.00      0.00
             0.00000000  -0.00055293   0.00000000    0.00    -81.34      0.00
             0.00000000   0.00000000  -0.00047917    0.00      0.00    -70.49
          """.split("\n")
        results = list(self.parser.parse(lines))
        flattened = {}
        for r in results:
            flattened.update(r)
        self.assertAlmostEqual(flattened['pressure'], -77.72)
        self.assertEqual(flattened['pressure units'], 'kbar')
        self.assertEqual(len(flattened['stress']), 3)
        self.assertAlmostEqual(flattened['stress'][1][1], -81.34)
        self.assertEqual(flattened['stress units'], 'kbar')

    def test_parse_ldau_parameters(self):
        """Test parsing simplified LDA+parameters used."""
        lines = """
            Simplified LDA+U calculation (l_max = 2) with parameters (eV):
            atomic species    L          U    alpha       J0     beta
               Fe1            2     4.3000   0.0000   0.0000   0.0000
               Fe2            2     4.3000   0.0000   0.0000   0.0000
        """.split("\n")
        results = list(self.parser.parse(lines))
        flattened = {}
        for r in results:
            flattened.update(r)
        self.assertEqual(flattened['LDA+U l_max'], 2)
        self.assertEqual(flattened['LDA+U parameters']['Fe1']['L'], 2)
        self.assertEqual(flattened['LDA+U parameters']['Fe1']['U'], 4.3)
        self.assertEqual(flattened['LDA+U parameters']['Fe2']['L'], 2)
        self.assertEqual(flattened['LDA+U parameters']['Fe2']['U'], 4.3)

    def test_parse_n_bfgs_steps(self):
        """Test parsing the # BFGS steps required for convergence."""
        lines = ['   bfgs converged in  11 scf cycles and  10 bfgs steps  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]['scf cycle count'], 11)
        self.assertEqual(results[0]['bfgs step count'], 10)

    def test_parse_n_steps_for_sc(self):
        """Test parsing the # iterations to achieve self-consistency."""
        lines = ['    convergence has been achieved in   6 iterations  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(
            results[0]['number of iterations for self-consistency'], 6)

    def test_parse_total_cpu_time(self):
        """Test parsing the total CPU time for the run."""
        lines = ['   PWSCF        :    43.87s CPU        44.49s WALL  ',
                 '   PWSCF        : 57m21.02s CPU    58m38.74s WALL   ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(results[0]['total CPU time'], '43.87s')
        self.assertEqual(results[1]['total CPU time'], '57m21.02s')

    def test_parse_atomic_positions(self):
        """Test parsing the atomic positions, initial and from cards."""
        # initial positions
        lines = """
            Cartesian axes

            site n.  atom                  positions (alat units)
                1    O1  tau( 1) = (   0.5000000   0.5000000   0.5000000  )
                2    O1  tau( 2) = (   1.5000000   1.5000000   1.5000000  )
                3    Fe1 tau( 3) = (   0.0000000   0.0000000   0.0000000  )
                4    Fe2 tau( 4) = (   1.0000000   1.0000000   1.0000000  )

        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        self.assertListEqual(results[0]['list of atomic species'],
                             ['O1', 'O1', 'Fe1', 'Fe2'])
        self.assertAlmostEqual(results[0]['list of atomic positions'][1][2],
                               1.5)
        self.assertEqual(results[0]['atomic positions units'], 'alat')

        # from the ATOMIC_POSITIONS cards
        lines = """
            ATOMIC_POSITIONS (crystal)
            As       0.282619597   0.282619664   0.282619694
            As      -0.282619597  -0.282619664  -0.282619694

            ATOMIC_POSITIONS (bohr)
            As       0.272273145   0.272273159   0.272273146
            As      -0.272273145  -0.272273159  -0.272273146
            End final coordinates
        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        self.assertListEqual(results[0]['list of atomic species'],
                             ['As', 'As'])
        self.assertAlmostEqual(results[0]['list of atomic positions'][1][0],
                               -0.282619597)
        self.assertEqual(results[0]['atomic positions units'], 'crystal')
        self.assertAlmostEqual(results[0]['list of atomic positions'][1][0],
                               -0.282619597)
        self.assertAlmostEqual(results[1]['list of atomic positions'][0][1],
                               0.272273159)
        self.assertEqual(results[1]['atomic positions units'], 'bohr')

    def test_parse_starting_mag_structure(self):
        """Test parsing the starting magnetic structure."""
        lines = """
            Starting magnetic structure
            atomic species   magnetization
                O1           0.000
                Fe1          0.500
                Fe2         -0.500
        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(
            results[0]['starting magnetic structure']['O1'], 0.0)
        self.assertAlmostEqual(
            results[0]['starting magnetic structure']['Fe2'], -0.5)

    def test_parse_total_magnetization(self):
        """Test parsing the total magnetization per cell."""
        lines = ['   total magnetization       =    -0.16 Bohr mag/cell  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['total magnetization'], -0.16)
        self.assertEqual(results[0]['total magnetization units'],
                         'Bohr mag/cell')

    def test_parse_absolute_magnetization(self):
        """Test parsing the absolute magnetization per cell."""
        lines = ['   absolute magnetization    =     7.36 Bohr mag/cell  ']
        results = [r for r in self.parser.parse(lines) if r]
        self.assertAlmostEqual(results[0]['absolute magnetization'], 7.36)
        self.assertEqual(results[0]['absolute magnetization units'],
                         'Bohr mag/cell')

    def test_parse_site_proj_quantities(self):
        """Test parsing site-projected magnetic moment and charges."""
        lines = """
            Magnetic moment per site:
            atom:  1    charge:  5.8393    magn:  -0.0001    constr:  0.0000
            atom:  2    charge:  5.8393    magn:  -0.0001    constr:  0.0000
            atom:  3    charge:  5.6861    magn:   3.3448    constr:  0.0000
            atom:  4    charge:  5.6871    magn:  -3.3441    constr:  0.0000

        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(len(results[0]['site-projected charges']), 4)
        self.assertAlmostEqual(results[0]['site-projected charges'][2], 5.6861)
        self.assertAlmostEqual(
            results[0]['site-projected magnetic moments'][3], -3.3441)

    def test_parse_warning(self):
        """Test parsing warnings."""
        lines = """
            WARNING: bfgs curvature condition failed, Theta= 0.865
            Warning: card &IONS ignored
            WARNING:     1 eigenvalues not converged in regterg

        """.split('\n')
        results = [r for r in self.parser.parse(lines) if r]
        self.assertEqual(len(results), 3)
        self.assertTrue('card &IONS ignored' in results[1]['warning'])
        self.assertTrue('eigenvalues not converged' in results[2]['warning'])


if __name__ == '__main__':
    unittest.main()
