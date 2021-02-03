from dftparse.core import BlockParser


def _parse_gpaw_version(line, lines):
    """Parse the GPAW version from the stdout.

    Sample section of stdout:
     ___ ___ ___ _ _ _
    |   |   |_  | | | |
    | | | | | . | | | |
    |__ |  _|___|_____|  19.8.1
    |___|_|
    """
    return {"gpaw_version": line.strip().split()[-1]}


def _parse_username(line, lines):
    """Parse the username from the stdout.

    Sample section of stdout:
    User:   lkavalsk@c009
    """
    return {"username": line.strip().split()[-1]}


def _parse_python_version(line, lines):
    """Parse the python version from the stdout.

    Sample section of stdout:
    Python: 3.7.7
    """
    return {"python_version": line.strip().split()[-1]}


def _parse_gpaw_package(line, lines):
    """Parse the location of the GPAW python package and binaries.

    Sample section of stdout:
    gpaw:   /home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/gpaw
    _gpaw:  /home/lkavalsk/.conda/envs/gp2/bin/gpaw-python
    """
    parsed = {"gpaw_pkg_location": line.strip().split()[-1]}
    newline = next(lines)
    if "_gpaw: " in newline:
        parsed.update({"gpaw_bin_location": newline.strip().split()[-1]})
    return parsed


def _parse_ase_package(line, lines):
    """Parse the location of the ASE package from the stdout.

    Sample section of stdout:
    ase:    /home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/ase (version 3.19.1)
    """
    toks = line.strip().split()
    return {"ase_pkg_location": toks[1], "ase_version": toks[-1].rstrip(")")}


def _parse_numpy_package(line, lines):
    """Parse the location of the numpy package from the stdout.

    Sample section of stdout:
    numpy:  /home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/numpy (version 1.18.1)
    """
    toks = line.strip().split()
    return {"numpy_pkg_location": toks[1], "numpy_version": toks[-1].rstrip(")")}


def _parse_scipy_package(line, lines):
    """Parse the location of the scipy package from the stdout.

    Sample section of stdout:
    scipy:  /home/lkavalsk/.conda/envs/gp2/lib/python3.7/site-packages/scipy (version 1.4.1)
    """
    toks = line.strip().split()
    return {"scipy_pkg_location": toks[1], "scipy_version": toks[-1].rstrip(")")}


def _parse_libxc_version(line, lines):
    """Parse the version of the LibXC package being used in GPAW.

    Sample section of stdout:
    libxc:  3.0.0
    """
    return {"libxc_version": line.strip().split()[-1]}


def _parse_ncores(line, lines):
    """Parse the number of cores the calculation was performed on.

    Sample section of stdout:
    cores:  32
    """
    return {"ncores": line.strip().split()[-1]}


def _parse_gpaw_setup_file(line, lines):
    """Parse the GPAW setup files used for each species in the calculation.

    Sample section of stdout:
      file: /home/azeeshan/software/gpaw-setups-0.9.20000/Pt.PBE.gz
    """
    return {"gpaw_setup_file": line.strip().split()[-1]}


def _parse_timings(line, lines):
    """Parse the runtimes for the various major steps in a DFT calculation
    and the total runtime, in seconds.

    Sample section of stdout:
    Timing:                                      incl.     excl.
    -------------------------------------------------------------------
    Density initialized from wave functions:     4.321     3.840   0.0% |
    Forces:                                    134.251   134.251   0.9% |
    Hamiltonian:                                68.707     0.002   0.0% |
    LCAO initialization:                         2.892     0.273   0.0% |
    SCF-cycle:                               15315.973   373.667   2.4% ||
     Davidson:                               13520.996  7032.321  44.6% |-----------------|
     Hamiltonian:                             1308.109     0.062   0.0% |
      XC 3D grid:                             1034.120   147.698   0.9% |
    Other:                                     244.268   244.268   1.5% ||
    -------------------------------------------------------------------
    Total:                                             15770.436 100.0%
    """
    timings = {}
    line = next(lines)
    while "Total: " not in line:
        if "wave functions" in line:
            timings["wf_initialization_time"] = line.strip().split(":")[-1].split()[0]
        elif "Forces" in line:
            timings["forces_time"] = line.strip().split(":")[-1].split()[0]
        elif "LCAO initial" in line:
            timings["lcao_initialization_time"] = line.strip().split(":")[-1].split()[0]
        elif "SCF" in line:
            timings["scf_cycle_time"] = line.strip().split(":")[-1].split()[0]
        elif "Other" in line:
            timings["other_time"] = line.strip().split(":")[-1].split()[0]
        line = next(lines)
    timings["total_time"] = line.strip().split(":")[-1].split()[0]
    return timings


def _parse_memory_usage(line, lines):
    """Parse the memory used for the GPAW run.

    Sample section of stdout:
    Memory usage: 446.11 MiB
    """
    return {"memory_usage": " ".join(line.strip().split()[2:])}


def _parse_run_date(line, lines):
    """Parse time and date when the calculation was run.

    Sample section of stdout:
    Date: Tue Sep  1 21:39:47 2020
    """
    return {"run_date": " ".join(line.strip().split()[1:])}


def _parse_mp_k_mesh(line, lines):
    """Parse the Monkhorst Pack k-mesh used.

    Sample section of stdout:
    16 k-points: 4 x 4 x 1 Monkhorst-Pack grid
    """
    toks = line.strip().split(":")[1].strip().split("Monkhorst-Pack grid")[0].strip()
    return {"mp_k_mesh": tuple(map(int, toks.split(" x ")))}


def _parse_xc(line, lines):
    """Parse the Exchange Correlation Functional used.

    Sample section of stdout:
    Using the BEEF-vdW Exchange-Correlation functional
    """
    return {"xc": line.split()[2]}


def _parse_dipole_correction(line, lines):
    """Parse if a dipole correction was applied

    Sample section of stdout:
    Dipole correction along z-axis
    """
    return {"dipole_correction": True}


base_rules = [
    (lambda x: "|__ |  _|___|_____|" in x, _parse_gpaw_version),
    (lambda x: "User: " in x, _parse_username),
    (lambda x: "Python: " in x, _parse_python_version),
    (lambda x: "gpaw: " in x, _parse_gpaw_package),
    (lambda x: "ase: " in x, _parse_ase_package),
    (lambda x: "numpy: " in x, _parse_numpy_package),
    (lambda x: "scipy: " in x, _parse_scipy_package),
    (lambda x: "libxc: " in x, _parse_libxc_version),
    (lambda x: "cores: " in x, _parse_ncores),
    (lambda x: "  file: " in x, _parse_gpaw_setup_file),
    (lambda x: "Timing: " in x, _parse_timings),
    (lambda x: "Memory usage: " in x, _parse_memory_usage),
    (lambda x: "Date: " in x, _parse_run_date),
    (lambda x: "Monkhorst-Pack" in x, _parse_mp_k_mesh),
    (lambda x: "Exchange-Correlation" in x, _parse_xc),
    (lambda x: "Dipole correction" in x, _parse_dipole_correction),
]


class GpawStdOutputParser(BlockParser):
    def __init__(self, rules=base_rules):
        BlockParser.__init__(self)
        for rule in rules:
            self.add_rule(rule)
