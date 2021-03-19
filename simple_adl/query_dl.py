#!/usr/bin/env python
"""
Generic python script.
"""
__author__ = "Sidney Mau"

import numpy as np
from dl import queryClient as qc

#-------------------------------------------------------------------------------

# Redenning coefficients
R_g = 3.185
R_r = 2.140
R_i = 1.571

def query(profile, ra, dec, radius=1.0, gmax=23.5, stars=True, galaxies=False):
    """Return data queried from datalab
    Parameters
    ----------
    profile : Profile for data lab query [str]
    ra      : Right Ascension [deg]
    dec     : Declination [deg]
    radius  : radius around (ra, dec) [deg]

    Returns
    -------
    data : numpy recarray of data
    """

    if profile:
        qc.set_profile(profile)

    sql_stars = f'''
        SELECT ra,
               dec,
               wavg_mag_psf_g as gmag,
               wavg_mag_psf_g-{R_g}*ebv AS gmag_dered, -- dereddend magnitude
               wavg_magerr_psf_g as gerr,
               wavg_mag_psf_r-{R_r}*ebv AS rmag_dered, -- dereddend magnitude
               wavg_mag_psf_r as rmag,
               wavg_magerr_psf_r as rerr,
               ebv
        FROM delve_dr1.objects
        WHERE q3c_radial_query(ra,dec,{ra},{dec},{radius})
              AND 0 <= EXTENDED_CLASS_G AND EXTENDED_CLASS_G <= 1 -- for star-galaxy separation
              AND wavg_mag_psf_g < 90        -- for quality
              AND wavg_mag_psf_r < 90        -- for quality
              AND wavg_mag_psf_g < {gmax}    -- for quality
    '''

    sql_galaxies = f'''
        SELECT ra,
               dec,
               wavg_mag_psf_g as gmag,
               wavg_mag_psf_g-{R_g}*ebv AS gmag_dered, -- dereddend magnitude
               wavg_magerr_psf_g as gerr,
               wavg_mag_psf_r-{R_r}*ebv AS rmag_dered, -- dereddend magnitude
               wavg_mag_psf_r as rmag,
               wavg_magerr_psf_r as rerr,
               ebv
        FROM delve_dr1.objects
        WHERE q3c_radial_query(ra,dec,{ra},{dec},{radius})
              AND 2 <= EXTENDED_CLASS_G   -- for star-galaxy separation
              AND wavg_mag_psf_g < 90     -- for quality
              AND wavg_mag_psf_r < 90     -- for quality
              AND wavg_mag_psf_g < {gmax} -- for quality
    '''

    if stars:
        query_stars = qc.query(sql=sql_stars,fmt='structarray')
    if galaxies:
        query_galaxies = qc.query(sql=sql_galaxies,fmt='structarray')

    if stars and not galaxies:
        return(query_stars)
    elif not stars and galaxies:
        return(query_galaxies)
    elif stars and galaxies:
        return(query_stars, query_galaxies)
    else:
        return(None)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile',type=str,required=False,
                        help='Profile for data lab query [str]')
    parser.add_argument('--ra',type=float,required=True,
                        help='Right Ascension of target position [deg]')
    parser.add_argument('--dec',type=float,required=True,
                        help='Declination of target position [deg]')
    parser.add_argument('--radius',type=float,default=1.0,
                        help='Radius around target position [deg]')
    parser.add_argument('--gmax',type=float,default=23.5,
                        help='Maximum g-band magnitude [mag]')
    args = parser.parse_args()
    data = query(args.profile, args.ra, args.dec, args.radius, args.gmax)
    import pdb;pdb.set_trace()
