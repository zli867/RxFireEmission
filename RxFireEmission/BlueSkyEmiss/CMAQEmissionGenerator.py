from EmissionGeneratorHelper import verticalHourlyEmission
import netCDF4
import numpy as np

"""
The emission generator needs BlueSky output, MCIP CROS 3D and the anthropogenic emission for providing header of NetCDF
"""

output_name = 'emis_mole_surface_20200401_hires4_cmaq_saprc_bsp_test2.ncf'
sample_file_name = 'emis_mole_surface_20200401_hires4_cmaq_saprc_soa_2011ec_v6_11f.ncf'
emiss_dir = "/Volumes/ZONGRUN_BACKUP_2/CDC/20200401/"
metcros3d = "/Volumes/ZONGRUN_BACKUP_2/CDC/20200401/METCRO3D_hires4_20200401"
bsp_filename = "/Volumes/ZONGRUN_BACKUP_2/CDC/20200401/SE2020_04_01_out.json"
file1 = emiss_dir + sample_file_name
file2 = emiss_dir + output_name

# convert unit (us ton)
convert_to_g_s = (1000000)/3600


def convert_to_mole_s(molecule_weight):
    # convert to g/s -> moles/s
    return convert_to_g_s/molecule_weight


# SAPRC07
species_mapping = {
    'CO': [(1 * convert_to_mole_s(28), 'CO')],
    # SERA
    'NO2': [(0.35 * convert_to_mole_s(46), 'NOx')],
    'NO': [(0.65 * convert_to_mole_s(46), 'NOx')],
    'NH3': [(1 * convert_to_mole_s(17), 'NH3')],
    'SO2': [(1 * convert_to_mole_s(64), 'SO2')],
    'ACYE': [(0.084 * convert_to_mole_s(26.0373), 'VOC')],
    'ALK1': [(0.1047 * convert_to_mole_s(30.069), 'VOC')],
    'ALK2': [(0.0035 * convert_to_mole_s(44.0956), 'VOC')],
    'ALK3': [(0.004108 * convert_to_mole_s(60.8495), 'VOC')],
    'ALK4': [(0.0255 * convert_to_mole_s(101.5224), 'VOC')],
    'ALK5': [(0.2443 * convert_to_mole_s(166.6683), 'VOC')],
    'APIN': [(0.0143 * convert_to_mole_s(208.3353), 'VOC')],
    'ARO1': [(0.0263 * convert_to_mole_s(166.6883), 'VOC')],
    'ARO2': [(0.422 * convert_to_mole_s(187.5018), 'VOC')],
    'B124': [(0.002927 * convert_to_mole_s(187.5018), 'VOC')],
    'BDE13': [(0.0052 * convert_to_mole_s(54.0904), 'VOC')],
    'CH4': [(0.0982 * convert_to_mole_s(16.0425), 'VOC')],
    'CRES': [(0.002397 * convert_to_mole_s(145.8347), 'VOC')],
    'ETHE': [(0.1911 * convert_to_mole_s(28.0532), 'VOC')],
    'MVK': [(0.0003175 * convert_to_mole_s(83.3341), 'VOC')],
    'NROG': [(0.0206 * convert_to_mole_s(41.6671), 'VOC')],
    'OLE1': [(0.0451 * convert_to_mole_s(74.1464), 'VOC')],
    'OLE2': [(0.0163 * convert_to_mole_s(83.8603), 'VOC')],
    'PRD2': [(0.0174 * convert_to_mole_s(125.0012), 'VOC')],
    'PRPE': [(0.0393 * convert_to_mole_s(42.0797), 'VOC')],
    'TERP': [(0.0123 * convert_to_mole_s(208.3353), 'VOC')],
    'PAL': [(4.6 * (10 ** (-4)) * convert_to_g_s, 'PM2.5')],
    'PCA': [(7.2 * (10 ** (-4)) * convert_to_g_s, 'PM2.5')],
    'PCL': [(0.00239 * convert_to_g_s, 'PM2.5')],
    'PEC': [(0.109 * convert_to_g_s, 'PM2.5')],
    'PFE': [(4.45 * (10 ** (-4)) * convert_to_g_s, 'PM2.5')],
    'PK': [(0.00135 * convert_to_g_s, 'PM2.5')],
    'PMFINE': [(0.375 * convert_to_g_s, 'PM2.5')],
    'PMN': [(1.1 * (10 ** (-4)) * convert_to_g_s, 'PM2.5')],
    'PMOTHR': [(0.012995 * convert_to_g_s, 'PM2.5')],
    'PNA': [(0.00135 * convert_to_g_s, 'PM2.5')],
    'PNCOM': [(0.351 * convert_to_g_s, 'PM2.5')],
    'PNH4': [(0.00341 * convert_to_g_s, 'PM2.5')],
    'PNO3': [(0.0107 * convert_to_g_s, 'PM2.5')],
    'POC': [(0.502 * convert_to_g_s, 'PM2.5')],
    'PSI': [(1.0 * (10 ** (-4)) * convert_to_g_s, 'PM2.5')],
    'PSO4': [(0.0033 * convert_to_g_s, 'PM2.5')],
    'PTI': [(6.7 * (10 ** (-4)) * convert_to_g_s, 'PM2.5')],
    # SERA
    'PMC': [(1.2480483 * convert_to_g_s, 'PM2.5'), (-1 * convert_to_g_s, 'PM2.5')]
}


select_species = ["CO", "SO2", "NH3", "NOx", "PM2.5", "VOC"]
emission_tensor = verticalHourlyEmission(metcros3d, bsp_filename)
met_ds = netCDF4.Dataset(metcros3d)
# (species, MCIP time length, LAY, MCIP X length, MCIP Y length)

species_num, TIMESTEP, LAY, X, Y = emission_tensor.shape
# Write data to netcdf file
with netCDF4.Dataset(file1) as src, netCDF4.Dataset(file2, "w", format='NETCDF3_64BIT_OFFSET',diskless=True,persist=True) as dst:
    # copy global attributes all at once via dictionary
    globle_dict = src.__dict__
    globle_dict['NLAYS'] = LAY
    globle_dict['VGLVLS'] = met_ds.__dict__['VGLVLS']
    dst.setncatts(globle_dict)
    # copy dimensions
    for name, dimension in src.dimensions.items():
        if name == 'LAY':
            dst.createDimension(name, LAY)
        else:
            dst.createDimension(name, len(dimension))
    # copy all file data except for the excluded
    for name, variable in src.variables.items():
        var_tmp = dst.createVariable(name, variable.datatype, variable.dimensions)
        # REMEMBER DO NOT CHANGE ALL VARIABLES
        if name in species_mapping.keys():
            dst[name][:] = np.zeros(var_tmp.shape)
            # generate emission data
            # Daily emission data, hour is 25
            print("Mapping " + name + " into Emission File")
            emission_specie_name = name
            # Generate emiss based on mapping
            cmaq_emission_data = np.zeros(var_tmp.shape)
            for mapping_tuple in species_mapping[emission_specie_name]:
                specie_idx = select_species.index(mapping_tuple[1])
                cmaq_emission_data += mapping_tuple[0] * emission_tensor[specie_idx, :, :, :, :]
            dst[name][:] = cmaq_emission_data
        elif name == "TFLAG":
            # REMEMBER DO NOT CHANGE ALL VARIABLES
            print("Do not revise variable:" + name)
            dst[name][:] = src[name][:]
        else:
            print("Set the emission variable to zeros: " + name)
            dst[name][:] = np.zeros(var_tmp.shape)
        # # copy variable attributes all at once via dictionary
        dst[name].setncatts(src[name].__dict__)
