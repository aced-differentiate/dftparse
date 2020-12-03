import os

from dftparse.core import BlockParser


def _parse_header(line, lines):
    """
    Example:
        For a typical standard output header from PWscf like this:
        "     Program PWSCF v.6.1 (svn rev. 13591M) starts on\
        12Jul2017 at 10:17:52 \n"

        the parsed dictionary output looks like this:
        {'version': 'v.6.1', 'start_date': '12Jul2017', 'start_time':
        '10:17:52'}
    """
    toks = line.split()

    def _get_next_tok(toks, prev_tok):
        match = [toks[i] for i in range(len(toks)) if toks[i-1] == prev_tok]
        return match[0] if match else None

    return {
        'version': _get_next_tok(toks, 'PWSCF').strip('v.'),
        'start_date': _get_next_tok(toks, 'on'),
        'start_time': _get_next_tok(toks, 'at')
    }


def _parse_input_filename(line, lines):
    return {
        'input file': line.split()[-1]
    }


def _parse_pseudopotential(line, lines):
    newline = next(lines)
    return {
        'pseudopotential file': os.path.basename(newline.strip())
    }


def _parse_bravais_lattice(line, lines):
    return {
        'bravais-lattice index': int(line.partition('=')[2])
    }


def _parse_lattice_parameter(line, lines):
    toks = line.strip().split()
    return {
        'lattice parameter': float(toks[4]),
        'lattice parameter units': toks[-1],
    }


def _parse_cell_vectors(line, lines):
    def _parse_cv(line, ind1, ind2):
        return list(map(float, line.strip().split()[ind1:ind2]))
    units = line.strip().partition('(')[2].rstrip(')')
    cell_vectors = []
    if 'crystal axes' in line:
        for i in range(3):
            cell_vectors.append(_parse_cv(next(lines), -4, -1))
    elif 'CELL_PARAMETERS' in line:
        for i in range(3):
            cell_vectors.append(_parse_cv(next(lines), 0, 3))
    return {
        'cell vectors': cell_vectors,
        'cell vectors units': units,
    }


def _parse_unit_cell_volume(line, lines):
    toks = line.partition('=')[2].split()
    return {
        'unit-cell volume': float(toks[0]),
        'unit-cell volume units': toks[1]
    }


def _parse_n_atoms_per_cell(line, lines):
    return {
        'number of atoms/cell': int(line.strip().split()[-1])
    }


def _parse_n_atom_types(line, lines):
    return {
        'number of atom types': int(line.strip().split()[-1])
    }


def _parse_n_electrons(line, lines):
    return {
        'number of electrons': float(line.strip().split()[4])
    }


def _parse_kinetic_energy_cutoff(line, lines):
    toks = line.partition('=')[2].split()
    return {
        'kinetic-energy cutoff': float(toks[0]),
        'kinetic-energy cutoff units': toks[1],
    }


def _parse_charge_density_cutoff(line, lines):
    toks = line.partition('=')[2].split()
    return {
        'charge density cutoff': float(toks[0]),
        'charge density cutoff units': toks[1],
    }


def _parse_mixing_beta(line, lines):
    return {
        'mixing beta': float(line.partition('=')[2]),
    }


def _parse_scf_conv_threshold(line, lines):
    return {
        'scf convergence threshold': float(line.partition('=')[2]),
    }


def _parse_ionic_conv_threshold(line, lines):
    # NB: keys for backwards compatibility
    # NB: deprecate in the future?
    key_lookup = {
        'energy': ['ionic energy convergence threshold', 'energy criteria'],
        'force': ['forces convergence threshold', 'force criteria'],
        'cell': ['pressure convergence threshold', 'cell criteria']
    }
    toks = line.strip().split()
    if 'convergence thresholds' in line:
        results = {
            'ionic energy convergence threshold': float(toks[-4]),
            'forces convergence threshold': float(toks[-1]),
        }
    elif 'criteria: energy' in line:
        results = {}
        for i, tok in enumerate(toks):
            if tok in key_lookup:
                val = toks[i+2].strip(',').strip(')').strip('Ry').strip('Ry/Bohr').strip('kbar')
                for key in key_lookup[tok]:
                    results[key] = float(val)
    return results


def _parse_xc(line, lines):
    xc = line.partition('=')[2].partition('(')[0].split()
    return {
        'exchange-correlation': xc,
    }


def _parse_kpoints_block(line, lines):
    toks = line.strip().split()
    results = {
        'number of k-points': int(toks[4]),
    }
    # smearing information
    for ind, tok in enumerate(toks):
        if 'smearing' in tok:
            results['smearing type'] = toks[ind-1]
        if 'width' in tok:
            results['smearing width'] = float(toks[ind+2])
            results['smearing width units'] = 'Ry'

    newline = next(lines)
    # if # k-points > 100 they aren't printed when verbosity is `low`
    if not newline.strip() and 'print them' in next(lines):
        return results

    results['k-points coordinate system'] = newline.strip()
    # list of k-points and corresponding weights
    results['list of k-points'] = []
    results['list of k-point weights'] = []
    for i in range(results['number of k-points']):
        newline = next(lines)
        toks = newline.strip().split()
        kpoints = list(map(float, [t.strip('),') for t in toks[4:7]]))
        results['list of k-points'].append(kpoints)
        results['list of k-point weights'].append(float(toks[-1]))
    return results


def _parse_fermi_energy(line, lines):
    toks = line.strip().split()
    return {
        'fermi energy': float(toks[-2]),
        'fermi energy units': toks[-1],
    }


def _parse_total_energy(line, lines):
    total_energy = line.partition('=')[2].split()
    return {
        'total energy': float(total_energy[0]),
        'total energy units': total_energy[1]
    }


def _gen_energy_contrib(name):
    def _extract(line, lines):
        toks = line.partition('=')[2].split()
        return {
            '{} energy contribution'.format(name): float(toks[0]),
            '{} energy contribution units'.format(name): toks[1]
        }
    return (lambda x: '{} contrib'.format(name) in x, _extract)


def _parse_hubbard_energy(line, lines):
    toks = line.partition('=')[2].split()
    return {
        'Hubbard energy contribution': float(toks[0]),
        'Hubbard energy contribution units': toks[-1],
    }


def _parse_forces(line, lines):
    """Parse the forces block, including individual terms (e.g. Hubbard)"""
    units = line.split()[-1].rstrip('):').lstrip('(')
    next(lines)
    newline = next(lines)
    total = []
    non_local = []
    ionic = []
    local = []
    core_correction = []
    hubbard = []
    scf = []
    types = []
    while ('non-local contrib.' not in newline) and len(newline.split()) > 0:
        if '=' in newline:
            total.append([float(x) for x in newline.partition('=')[2].split()])
            types.append(int(newline.split()[3]))
        newline = next(lines)

    if len(newline.split()) > 0:
        while 'The ionic contribution' not in newline:
            if '=' in newline:
                non_local.append([float(x) for x in
                                  newline.partition('=')[2].split()])
            newline = next(lines)
        while 'The local contribution' not in newline:
            if '=' in newline:
                ionic.append([float(x) for x in
                              newline.partition('=')[2].split()])
            newline = next(lines)
        while 'The core correction contribution' not in newline:
            if '=' in newline:
                local.append([float(x) for x in
                              newline.partition('=')[2].split()])
            newline = next(lines)
        while 'The Hubbard contrib.' not in newline:
            if '=' in newline:
                core_correction.append([float(x) for x in
                                        newline.partition('=')[2].split()])
            newline = next(lines)
        while 'The SCF correction term' not in newline:
            if '=' in newline:
                hubbard.append([float(x) for x in
                                newline.partition('=')[2].split()])
            newline = next(lines)
        while len(newline.split()) > 0:
            if '=' in newline:
                scf.append([float(x) for x in
                            newline.partition('=')[2].split()])
            newline = next(lines)
    newline = next(lines)
    total_force = float(newline.split()[3])
    total_scf = float(newline.split()[8])
    return {
        'force units': units,
        'forces': total,
        'atomic forces': total,
        'non-local contribution to forces': non_local,
        'ionic contribution to forces': ionic,
        'local contribution to forces': local,
        'core corrections to forces': core_correction,
        'Hubbard contribution to forces': hubbard,
        'SCF correction term to forces': scf,
        'Atomic species index for forces': types,
        'atomic species index for forces': types,
        'total force': total_force,
        'total SCF correction': total_scf,
    }


def _parse_stress_and_pressure(line, lines):
    pressure = float(line.strip().rpartition('=')[2])
    stress = []
    for i in range(3):
        newline = next(lines)
        stress.append([float(x) for x in newline.split()[3:]])
    return {
        'pressure': pressure,
        'pressure units': 'kbar',
        'stress': stress,
        'stress units': 'kbar',
    }


def _parse_ldau_parameters(line, lines):
    result = {
        'LDA+U l_max': int(line.split()[5].rstrip(')')),
        'LDA+U parameters': {},
    }
    next(lines)
    newline = next(lines).split()
    while len(newline) > 1:
        result['LDA+U parameters'][newline[0]] = {
            'L': int(newline[1]),
            'U': float(newline[2]),
            'alpha': float(newline[3]),
            'J0': float(newline[4]),
            'beta': float(newline[5])
        }
        newline = next(lines).split()
    return result


def _parse_n_bfgs_steps(line, lines):
    toks = line.split()
    return {
        'scf cycle count': int(toks[3]),
        'bfgs step count': int(toks[7])
    }


def _parse_n_steps_for_sc(line, lines):
    return {
        'number of electronic iterations for convergence': int(
            line.split()[5]),
        'number of iterations for self-consistency': int(line.split()[5]),
    }


def _parse_total_cpu_time(line, lines):
    return {
        'total CPU time': line.split('CPU')[0].split(':')[-1].strip()
    }


def _parse_initial_atomic_positions(line, lines):
    units = line.partition('(')[2].split()[0]
    newline = next(lines).split()
    atomic_species = []
    atomic_positions = []
    while len(newline) > 0:
        atomic_species.append(newline[1])
        atomic_positions.append(list(map(float, newline[6:9])))
        newline = next(lines).split()
    return {
        'list of atomic species': atomic_species,
        'list of atomic positions': atomic_positions,
        'atomic positions units': units,
    }


def _parse_atomic_positions_card(line, lines):
    units = line.partition('(')[2].strip(')')
    newline = next(lines).split()
    atomic_species = []
    atomic_positions = []
    while len(newline) == 4:
        atomic_species.append(newline[0])
        atomic_positions.append(list(map(float, newline[1:4])))
        newline = next(lines).split()
    return {
        'list of atomic species': atomic_species,
        'list of atomic positions': atomic_positions,
        'atomic positions units': units,
    }


def _parse_atomic_positions(line, lines):
    if 'atom                  positions' in line:
        return _parse_initial_atomic_positions(line, lines)
    elif 'ATOMIC_POSITIONS' in line:
        return _parse_atomic_positions_card(line, lines)


def _parse_starting_mag_structure(line, lines):
    next(lines)
    newline = next(lines).split()
    result = {
        'starting magnetic structure': {}
    }
    while len(newline) > 0:
        result['starting magnetic structure'][newline[0]] = \
            float(newline[-1].strip())
        newline = next(lines).split()
    return result


def _parse_total_magnetization(line, lines):
    toks = line.partition('=')[2].split()
    return {
        'total magnetization': float(toks[0]),
        'total magnetization units': ' '.join(toks[1:]),
    }


def _parse_absolute_magnetization(line, lines):
    toks = line.partition('=')[2].split()
    return {
        'absolute magnetization': float(toks[0]),
        'absolute magnetization units': ' '.join(toks[1:]),
    }


def _parse_site_proj_quantities(line, lines):
    newline = next(lines).strip().split()
    results = {
        'site-projected charges': [],
        'site-projected magnetic moments': [],
    }
    while len(newline) > 0:
        results['site-projected charges'].append(float(newline[3]))
        results['site-projected magnetic moments'].append(float(newline[5]))
        newline = next(lines).strip().split()
    return results


def _parse_warning(line, lines):
    return {
        'warning': line.partition(':')[2].strip()
    }


base_rules = [
    (lambda x: 'Program PWSCF' in x, _parse_header),
    (lambda x: 'Reading input from' in x, _parse_input_filename),
    (lambda x: 'PseudoPot. #' in x, _parse_pseudopotential),
    (lambda x: 'bravais-lattice index' in x, _parse_bravais_lattice),
    (lambda x: 'lattice parameter' in x, _parse_lattice_parameter),
    (lambda x: 'crystal axes:' in x, _parse_cell_vectors),
    (lambda x: 'CELL_PARAMETERS ' in x, _parse_cell_vectors),
    (lambda x: 'unit-cell volume' in x, _parse_unit_cell_volume),
    (lambda x: 'number of atoms/cell' in x, _parse_n_atoms_per_cell),
    (lambda x: 'number of atomic types' in x, _parse_n_atom_types),
    (lambda x: 'number of electrons' in x, _parse_n_electrons),
    (lambda x: 'kinetic-energy cutoff' in x, _parse_kinetic_energy_cutoff),
    (lambda x: 'charge density cutoff' in x, _parse_charge_density_cutoff),
    (lambda x: 'mixing beta ' in x, _parse_mixing_beta),
    (lambda x: 'convergence threshold ' in x, _parse_scf_conv_threshold),
    (lambda x: 'convergence thresholds ' in x, _parse_ionic_conv_threshold),
    (lambda x: 'criteria: energy ' in x, _parse_ionic_conv_threshold),
    (lambda x: 'Exchange-correlation' in x, _parse_xc),
    (lambda x: 'number of k points=' in x, _parse_kpoints_block),
    (lambda x: 'Fermi energy is' in x, _parse_fermi_energy),
    (lambda x: '!    total energy' in x, _parse_total_energy),
    _gen_energy_contrib('one-electron'),
    _gen_energy_contrib('hartree'),
    _gen_energy_contrib('xc'),
    _gen_energy_contrib('ewald'),
    _gen_energy_contrib('smearing'),
    (lambda x: 'Hubbard energy' in x, _parse_hubbard_energy),
    (lambda x: 'Forces acting on atoms' in x, _parse_forces),
    (lambda x: 'total   stress' in x, _parse_stress_and_pressure),
    (lambda x: 'Simplified LDA+U calculation' in x, _parse_ldau_parameters),
    (lambda x: 'bfgs converged in' in x, _parse_n_bfgs_steps),
    (lambda x: 'convergence has been ' in x, _parse_n_steps_for_sc),
    (lambda x: 'PWSCF' and 'WALL' in x, _parse_total_cpu_time),
    (lambda x: 'atom                  pos' in x, _parse_atomic_positions),
    (lambda x: 'ATOMIC_POSITIONS' in x, _parse_atomic_positions),
    (lambda x: 'Starting magnetic ' in x, _parse_starting_mag_structure),
    (lambda x: 'total magnetization' in x, _parse_total_magnetization),
    (lambda x: 'absolute magnetization' in x, _parse_absolute_magnetization),
    (lambda x: 'Magnetic moment per site' in x, _parse_site_proj_quantities),
    (lambda x: 'warning' in x.lower(), _parse_warning),
]


class PwscfStdOutputParser(BlockParser):

    def __init__(self, rules=base_rules):
        BlockParser.__init__(self)
        for rule in rules:
            self.add_rule(rule)
