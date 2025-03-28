import os
import json
import base64
import numpy as np
import pandas as pd
from math import sin, radians, asin, degrees, pi, cos
from io import StringIO
from pymatgen.core import Structure, Lattice
from pymatgen.io.cif import CifParser
from pymatgen.analysis.diffraction.core import AbstractDiffractionPatternCalculator, DiffractionPattern, get_unique_families
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

# XRD wavelengths in angstroms.
WAVELENGTHS = {
    "CuKa": 1.54184,
    # Add additional radiations if needed.
}
selected_wavelength = "CuKa"

# Load atomic scattering parameters from JSON.
atomic_scattering_params_path = "atomic_scattering_params.json"
if not os.path.exists(atomic_scattering_params_path):
    raise FileNotFoundError("Required file 'atomic_scattering_params.json' not found.")
with open(atomic_scattering_params_path) as file:
    ATOMIC_SCATTERING_PARAMS = json.load(file)

class XRDCalculator(AbstractDiffractionPatternCalculator):
    AVAILABLE_RADIATION = tuple(WAVELENGTHS)

    def __init__(self, wavelength="CuKa", symprec: float = 0, debye_waller_factors=None):
        if isinstance(wavelength, (float, int)):
            self.wavelength = wavelength
        elif isinstance(wavelength, str):
            self.radiation = wavelength
            self.wavelength = WAVELENGTHS[wavelength]
        else:
            raise TypeError(f"{type(wavelength)} must be either float, int, or str")
        self.symprec = symprec
        self.debye_waller_factors = debye_waller_factors or {}

    def get_pattern(self, structure: Structure, scaled=True, two_theta_range=(0, 90)):
        if self.symprec:
            finder = SpacegroupAnalyzer(structure, symprec=self.symprec)
            structure = finder.get_refined_structure()

        wavelength = self.wavelength
        lattice = structure.lattice
        is_hex = lattice.is_hexagonal()

        min_r, max_r = (
            (0, 2 / wavelength)
            if two_theta_range is None
            else [2 * sin(radians(t / 2)) / wavelength for t in two_theta_range]
        )

        recip_lattice = lattice.reciprocal_lattice_crystallographic
        recip_pts = recip_lattice.get_points_in_sphere([[0, 0, 0]], [0, 0, 0], max_r)
        if min_r:
            recip_pts = [pt for pt in recip_pts if pt[1] >= min_r]

        _zs, _coeffs, _frac_coords, _occus, _dw_factors = [], [], [], [], []
        for site in structure:
            for sp, occu in site.species.items():
                _zs.append(sp.Z)
                try:
                    c = ATOMIC_SCATTERING_PARAMS[sp.symbol]
                except KeyError:
                    raise ValueError(f"No scattering coefficients for {sp.symbol}")
                _coeffs.append(c)
                _dw_factors.append(self.debye_waller_factors.get(sp.symbol, 0))
                _frac_coords.append(site.frac_coords)
                _occus.append(occu)
        zs = np.array(_zs)
        coeffs = np.array(_coeffs)
        frac_coords = np.array(_frac_coords)
        occus = np.array(_occus)
        dw_factors = np.array(_dw_factors)
        peaks = {}
        two_thetas = []

        for hkl, g_hkl, ind, _ in sorted(recip_pts, key=lambda i: (i[1], -i[0][0], -i[0][1], -i[0][2])):
            hkl = [int(round(i)) for i in hkl]
            if g_hkl != 0:
                theta = asin(wavelength * g_hkl / 2)
                s = g_hkl / 2
                s2 = s**2
                g_dot_r = np.dot(frac_coords, np.transpose([hkl])).T[0]
                fs = zs - 41.78214 * s2 * np.sum(
                    coeffs[:, :, 0] * np.exp(-coeffs[:, :, 1] * s2),
                    axis=1
                )
                dw_correction = np.exp(-dw_factors * s2)
                f_hkl = np.sum(fs * occus * np.exp(2j * pi * g_dot_r) * dw_correction)
                lorentz_factor = (1 + cos(2 * theta) ** 2) / (sin(theta) ** 2 * cos(theta))
                i_hkl = (f_hkl * f_hkl.conjugate()).real
                two_theta = degrees(2 * theta)
                if is_hex:
                    hkl = (hkl[0], hkl[1], -hkl[0] - hkl[1], hkl[2])
                ind = np.where(
                    np.abs(np.subtract(two_thetas, two_theta)) < AbstractDiffractionPatternCalculator.TWO_THETA_TOL
                )
                if len(ind[0]) > 0:
                    peaks[two_thetas[ind[0][0]]][0] += i_hkl * lorentz_factor
                    peaks[two_thetas[ind[0][0]]][1].append(tuple(hkl))
                else:
                    d_hkl = 1 / g_hkl
                    peaks[two_theta] = [i_hkl * lorentz_factor, [tuple(hkl)], d_hkl]
                    two_thetas.append(two_theta)
        max_intensity = max(v[0] for v in peaks.values())
        x = []
        y = []
        hkls = []
        d_hkls = []
        for k in sorted(peaks):
            v = peaks[k]
            fam = get_unique_families(v[1])
            if v[0] / max_intensity * 100 > AbstractDiffractionPatternCalculator.SCALED_INTENSITY_TOL:
                x.append(k)
                y.append(v[0])
                hkls.append([{"hkl": hkl, "multiplicity": mult} for hkl, mult in fam.items()])
                d_hkls.append(v[2])
        xrd = DiffractionPattern(x, y, hkls, d_hkls)
        if scaled:
            xrd.normalize(mode="max", value=100)
        return xrd

def normalize_structure(structure: Structure) -> Structure:
    """
    Normalize a structure by setting all site occupancies to 1.
    """
    species = []
    coords = []
    for site in structure:
        max_species = max(site.species.items(), key=lambda x: x[1])[0]
        species.append(max_species)
        coords.append(site.frac_coords)
    return Structure(structure.lattice, species, coords, coords_are_cartesian=False)

def parse_xy(contents):
    """
    Parse the contents of an uploaded .xy file.
    """
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    s = StringIO(decoded.decode('utf-8'))
    df = pd.read_csv(s, sep=r'\s+', header=None)  # Use a raw string for the separator
    df.columns = ['2_theta', 'intensity']
    return df


def parse_cif(contents):
    """
    Parse the contents of an uploaded .cif file and return a pymatgen Structure object.
    """
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    s = StringIO(decoded.decode('utf-8'))
    parser = CifParser(s)
    structures = parser.get_structures()
    return structures[0]