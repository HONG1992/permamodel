# -*- coding: utf-8 -*-
"""  Kudryavtsev Model code adapted for the BMI version developed for the Topoflow model

     Author: Kang Wang, 03/29/2016
     Modified: Elchin Jafarov, 03/29/2016

Input:
    (1) Location:
        input_lat: Latitude
        input_lon: Longitude

    (2) Climate :
        Ta  : Mean annual air temperature (C)
        Aa  : Amplitude of air temperature (C)
        Hsn : Winter-Averaged Snow Depth (m)
        Rsn : Snow Density (kg/m3)
        vwc : Volumetric Water Content (m3 / m3)

    (3) Vegetation:
        Hvgf: Height of vegetation in frozen period (m)
        Hvgt: Height of vegetation in thawed period (m)
        Dvf : Thermal diffusivity of vegetation in frozen period (m2 s)
        Dvt : Thermal diffusivity of vegetation in thawed period (m2 s)

Output:
        1) Mean annual temperature on the top of permafrost (C)
        2) Active Layer Thickness (m)

References:

    Anisimov, O. A., Shiklomanov, N. I., & Nelson, F. E. (1997).
        Global warming and active-layer thickness: results from transient general circulation models.
        Global and Planetary Change, 15(3), 61-77.
    Romanovsky, V. E., & Osterkamp, T. E. (1997).
        Thawing of the active layer on the coastal plain of the Alaskan Arctic.
        Permafrost and Periglacial processes, 8(1), 1-22.
    Sazonova, T. S., & Romanovsky, V. E. (2003).
        A model for regional‐scale estimation of temporal and spatial variability of active layer thickness and mean annual ground temperatures.
        Permafrost and Periglacial Processes, 14(2), 125-139.
    Sturm, M., Holmgren, J., König, M., & Morris, K. (1997).
        The thermal conductivity of seasonal snow. Journal of Glaciology, 43(143), 26-41.
    Ling, F., & Zhang, T. (2004).
        A numerical model for surface energy balance and thermal regime of the active layer and permafrost containing unfrozen water.
        Cold Regions Science and Technology, 38(1), 1-15.
    Wieder, W.R., J. Boehnert, G.B. Bonan, and M. Langseth. (2014).
        Regridded Harmonized World Soil Database v1.2. Data set.
        Available on-line [http://daac.ornl.gov] from Oak Ridge National Laboratory Distributed Active Archive Center, Oak Ridge, Tennessee, USA.  http://dx.doi.org/10.3334/ORNLDAAC/1247  .

"""

import numpy as np
from permamodel.utils import model_input
from permamodel.components import perma_base

class Ku_method( perma_base.permafrost_component ):

    #-------------------------------------------------------------------
    _att_map = {
    # NOTE: this will change in the future
        'model_name':         'PermaModel_Kudryavtsev_method',
        'version':            '0.1',
        'author_name':        'Kang Wang and Elchin Jafarov',
        'grid_type':          'none',
        'time_step_type':     'fixed',
        'step_method':        'explicit',
        #-------------------------------------------------------------
        'comp_name':          'Ku_model',
        'model_family':       'PermaModel',
        'cfg_extension':      '_ku_model.cfg',
        'cmt_var_prefix':     '/input/',
        'gui_yaml_file':      '/input/ku_model.yaml',
        'time_units':         'years' }

    _input_var_names = [
        'latitude',
        'longitude',
        'atmosphere_bottom_air__temperature',
        'atmosphere_bottom_air__temperature_amplitude',
        'snowpack__depth',
        'snowpack__density',
        'water-liquid__volumetric-water-content-soil',
        'vegetation__Hvgf',
        'vegetation__Hvgt',
        'vegetation__Dvf',
        'vegetation__Dvt' ]

    _output_var_names = [
        'soil__temperature',                                  # Tps
        'soil__active_layer_thickness' ]                      # Zal

    _var_name_map = {
    # NOTE: we need to look up for the corresponding standard names
        'latitude':                                           'lat',
        'longitude':                                          'lon',
        'atmosphere_bottom_air__temperature':                 'T_air',
        'atmosphere_bottom_air__temperature_amplitude':       'A_air',
        'snowpack__depth':                                    'h_snow',
        'snowpack__density':                                  'rho_snow',
        'water-liquid__volumetric-water-content-soil':        'vwc_H2O',
        'vegetation__Hvgf':                                   'Hvgf',
        'vegetation__Hvgt':                                   'Hvgt',
        'vegetation__Dvf':                                    'Dvf',
        'vegetation__Dvt':                                    'Dvt' }

    _var_units_map = {
    # NOTE: Kang please complete the vegetation info both on var names and units
        'latitude':                                           'lat',
        'longitude':                                          'lon',
        'atmosphere_bottom_air__temperature':                 'deg_C',
        'atmosphere_bottom_air__temperature_amplitude':       'deg_C',
        'snowpack__depth':                                    'm',
        'snowpack__density':                                  'kg m-3',
        'water-liquid__volumetric-water-content-soil':        'm3 m-3',
        'vegetation__Hvgf':                                   'm',
        'vegetation__Hvgt':                                   'm',
        'vegetation__Dvf':                                    'm2 s',
        'vegetation__Dvt':                                    'm2 s' }

    #-------------------------------------------------------------------
    def get_attribute(self, att_name):

        try:
            return self._att_map[ att_name.lower() ]
        except:
            print '###################################################'
            print ' ERROR: Could not find attribute: ' + att_name
            print '###################################################'
            print ' '

    #   get_attribute()
    #-------------------------------------------------------------------
    def get_input_var_names(self):

        #--------------------------------------------------------
        # Note: These are currently variables needed from other
        #       components vs. those read from files or GUI.
        #--------------------------------------------------------
        return self._input_var_names

    #   get_input_var_names()
    #-------------------------------------------------------------------
    def get_output_var_names(self):

        return self._output_var_names

    #   get_output_var_names()
    #-------------------------------------------------------------------
    def get_var_name(self, long_var_name):

        return self._var_name_map[ long_var_name ]

    #   get_var_name()
    #-------------------------------------------------------------------
    def get_var_units(self, long_var_name):

        return self._var_units_map[ long_var_name ]

    #   get_var_units()
    #-------------------------------------------------------------------
    def check_input_types(self):

        #--------------------------------------------------
        # Notes: rho_H2O, Cp_snow, rho_air and Cp_air are
        #        currently always scalars.
        #--------------------------------------------------
        are_scalars = np.array([
                          self.is_scalar('lat'),
                          self.is_scalar('lon'),
                          self.is_scalar('T_air'),
                          self.is_scalar('A_air'),
                          self.is_scalar('h_snow'),
                          self.is_scalar('rho_snow'),
                          self.is_scalar('vwc_H2O'),
                          self.is_scalar('Hvgf'),
                          self.is_scalar('Hvgt'),
                          self.is_scalar('Dvf'),
                          self.is_scalar('Dvt') ])

        self.ALL_SCALARS = np.all(are_scalars)

    #   check_input_types()
    #-------------------------------------------------------------------
    def open_input_files(self):
        # this function will work only if filename is not empty
    
        self.T_air_file       = self.in_directory + self.T_air_file
        self.A_air_file       = self.in_directory + self.A_air_file
        self.h_snow_file      = self.in_directory + self.h_snow_file
        self.rho_snow_file    = self.in_directory + self.rho_snow_file
        self.vwc_H2O_file     = self.in_directory + self.vwc_H2O_file
        self.Hvgf_file        = self.in_directory + self.Hvgf_file
        self.Hvgt_file        = self.in_directory + self.Hvgt_file
        self.Dvf_file         = self.in_directory + self.Dvf_file
        self.Dvt_file         = self.in_directory + self.Dvt_file
        self.lat_file         = self.in_directory + self.lat_file
        self.lon_file         = self.in_directory + self.lon_file

        self.T_air_unit       = model_input.open_file(self.T_air_type,  self.T_air_file)
        self.A_air_unit       = model_input.open_file(self.A_air_type,  self.A_air_file)
        self.h_snow_unit      = model_input.open_file(self.h_snow_type,  self.h_snow_file)
        self.rho_snow_unit    = model_input.open_file(self.rho_snow_type,  self.rho_snow_file)
        self.vwc_H2O_unit     = model_input.open_file(self.vwc_H2O_type,  self.vwc_H2O_file)
        self.Hvgf_unit        = model_input.open_file(self.Hvgf_type,  self.Hvgf_file)
        self.Hvgt_unit        = model_input.open_file(self.Hvgt_type,  self.Hvgt_file)
        self.Dvf_unit         = model_input.open_file(self.Dvf_type,  self.Dvf_file)
        self.Dvt_unit         = model_input.open_file(self.Dvt_type,  self.Dvt_file)
        self.lat_unit         = model_input.open_file(self.lat_type,  self.lat_file)
        self.lon_unit         = model_input.open_file(self.lon_type,  self.lon_file)

    #   open_input_files()
    #-------------------------------------------------------------------
    def read_input_files(self):

        #rti = self.rti # has a problem with loading rti: do not know where its been initialized

        #-------------------------------------------------------
        # All grids are assumed to have a data type of Float32.
        #-------------------------------------------------------    

        Lon_list = self.read_next_modified_KU(self.lon_file, self.lon_type)
        if Lon_list is not None: 
            self.lon = Lon_list
            n_Lon = len(Lon_list) 
        
        Lat_list = self.read_next_modified_KU(self.lat_file, self.lat_type)
        if (Lat_list is not None): 
            self.lat = Lat_list
            n_Lat = len(Lat_list) 
             
        T_air = self.read_next_modified_KU(self.T_air_file, self.T_air_type)
        if (T_air is not None): 
            self.T_air = T_air
            n_T_air = len(T_air)
            
        A_air = self.read_next_modified_KU(self.A_air_file, self.A_air_type)
        if (A_air is not None): 
            self.A_air = A_air
            n_A_air = len(A_air)
            
        h_snow = self.read_next_modified_KU(self.h_snow_file, self.h_snow_type)
        if (h_snow is not None): 
            self.h_snow = h_snow
            n_h_snow = len(h_snow) 
            
        rho_snow = self.read_next_modified_KU(self.rho_snow_file, self.rho_snow_type)
        if (rho_snow is not None): 
            self.rho_snow = rho_snow
            n_rho_snow = len(rho_snow)
        
        vwc_H2O = self.read_next_modified_KU(self.vwc_H2O_file, self.vwc_H2O_type)
        if (vwc_H2O is not None): 
            self.vwc_H2O = vwc_H2O
            n_vwc_H2O = len(vwc_H2O)
            
        Hvgf = self.read_next_modified_KU(self.Hvgf_file, self.Hvgf_type)
        if (Hvgf is not None): 
            self.Hvgf = Hvgf
            n_Hvgf = len(Hvgf)
            
        Hvgt = self.read_next_modified_KU(self.Hvgt_file, self.Hvgt_type)
        if (Hvgt is not None): 
            self.Hvgt = Hvgt
            n_Hvgt = len(Hvgt)
            
        Dvt = self.read_next_modified_KU(self.Dvt_file, self.Dvt_type)
        if (Dvt is not None): 
            self.Dvt = Dvt
            n_Dvt = len(Dvt)
            
        Dvf = self.read_next_modified_KU(self.Dvf_file, self.Dvf_type)
        if (Dvf is not None): 
            self.Dvf = Dvf
            n_Dvf = len(Dvf)
        
#        # Check the number of grid in input files:
#        
#        num_check= np.array([n_Lat, n_Lon, n_T_air, n_A_air, n_h_snow, 
#                             n_rho_snow, n_vwc_H2O, n_Hvgf, n_Hvgt,
#                             n_Dvf, n_Dvt])
#                             
#        num_unique = np.unique(num_check)                  
#                             
#        if len(num_unique)>1:
#            print "Warning: Dimensions of input must agree!"
#            exit
#        else:
#            self.n_grid = num_unique;
        
        
        
    #   read_input_files()
    #-------------------------------------------------------------------

    def update_soil_heat_capacity(self):

        #---------------------------------------------------------
        # Notes: we need a better documentation of this subroutine here
        #
        #
        #---------------------------------------------------------
        # Note: need to update frozen and thawed (Cf,Ct)
        #       heat capacities yearly
        #       this methods overriddes the method in the perma_base
        #
        #
        #--------------------------------------------------
        # I do not like this input file here need fix later
        #input_file = 'Parameters/Typical_Thermal_Parameters.csv'
        input_file = self.permafrost_dir + '/permamodel/components/Parameters/Typical_Thermal_Parameters.csv'
        s_data = np.genfromtxt(input_file, names = True, delimiter=',', dtype=None)

        Bulk_Density_Texture = s_data['Bulk_Density']
        Heat_Capacity_Texture = s_data['Heat_Capacity']

        # Adjusting percent of sand, silt, clay and peat ==
        tot_percent = self.p_sand+self.p_clay+self.p_silt+self.p_peat

        percent_sand = self.p_sand / tot_percent
        percent_clay = self.p_clay / tot_percent
        percent_silt = self.p_silt / tot_percent
        percent_peat = self.p_peat / tot_percent

        # Calculate heat capacity and bulk density of soil using exponential weighted.
        Heat_Capacity =  Heat_Capacity_Texture[2]*percent_clay + \
                         Heat_Capacity_Texture[1]*percent_sand + \
                         Heat_Capacity_Texture[0]*percent_silt + \
                         Heat_Capacity_Texture[3]*percent_peat       # Unit: J kg-1 C-1

        Bulk_Density  =  Bulk_Density_Texture[2]*percent_clay + \
                         Bulk_Density_Texture[1]*percent_sand + \
                         Bulk_Density_Texture[0]*percent_silt + \
                         Bulk_Density_Texture[3]*percent_peat        # Unit: kg m-3
                         
        # Estimate heat capacity for composed soil
        # based on the empirical approaches suggested by Anisimov et al. (1997)
        self.Ct = Heat_Capacity*Bulk_Density + 4190.*self.vwc_H2O # eq-15, Anisimov et al. 1997; Unit: J m-3 C-1
        self.Cf = Heat_Capacity*Bulk_Density + 2025.*self.vwc_H2O # eq-15, Anisimov et al. 1997; Unit: J m-3 C-1
       
    #   update_soil_heat_capacity()
    #-------------------------------------------------------------------

    def update_soil_thermal_conductivity(self):

        #---------------------------------------------------------
        # Notes: we need a better documentation of this subroutine here
        #
        #
        #---------------------------------------------------------
        # Note: need to update frozen and thawed (kf,kt)
        #       thermal conductivities yearly
        #       this methods overriddes the method in the perma_base
        #
        #
        #--------------------------------------------------
        #input_file = 'Parameters/Typical_Thermal_Parameters.csv'
        input_file = self.permafrost_dir + '/permamodel/components/Parameters/Typical_Thermal_Parameters.csv'
        s_data = np.genfromtxt(input_file, names = True, delimiter=',', dtype=None)

        Thermal_Conductivity_Thawed_Texture = s_data['Thermal_Conductivity_Thawed']
        Thermal_Conductivity_Frozen_Texture = s_data['Thermal_Conductivity_Frozen']

        # Adjusting percent of sand, silt, clay and peat ==
        tot_percent = self.p_sand+self.p_clay+self.p_silt+self.p_peat
        
        percent_sand = self.p_sand / tot_percent
        percent_clay = self.p_clay / tot_percent
        percent_silt = self.p_silt / tot_percent
        percent_peat = self.p_peat / tot_percent
        
        # Estimate thermal conductivity for composed soil
        Kt_Soil =  Thermal_Conductivity_Thawed_Texture[0]**percent_silt * \
               Thermal_Conductivity_Thawed_Texture[2]**percent_clay * \
               Thermal_Conductivity_Thawed_Texture[1]**percent_sand * \
               Thermal_Conductivity_Thawed_Texture[3]**percent_peat

        Kf_Soil =  Thermal_Conductivity_Frozen_Texture[0]**percent_silt * \
               Thermal_Conductivity_Frozen_Texture[2]**percent_clay * \
               Thermal_Conductivity_Frozen_Texture[1]**percent_sand * \
               Thermal_Conductivity_Frozen_Texture[3]**percent_peat

        # Consider the effect of water content on thermal conductivity
        vwc=self.vwc_H2O
        self.Kt = Kt_Soil**(1.0-vwc)*0.54**vwc #   Unit: (W m-1 C-1)
        self.Kf = Kf_Soil**(1.0-vwc)*2.35**vwc #   Unit: (W m-1 C-1)
        
    #   update_soil_thermal_conductivity()
    #-------------------------------------------------------------------
    def update_snow_thermal_properties(self):

        #---------------------------------------------------------
        # Notes: we need a better documentation of this subroutine here
        # Conductivity of snow:  eq-4, Sturm et al., 1997:
        # Capacity of snow:
        #   eq-30, Ling et al., 2004; OR Table-1, Goodrich, 1982.
        #---------------------------------------------------------
        # Note: need to update frozen and thawed (kf,kt)
        #       thermal conductivities yearly
        #       this methods overriddes the method in the perma_base
        #
        #
        #--------------------------------------------------
        rho_sn=self.rho_snow

        self.Ksn = (rho_sn/1000.)*(rho_sn/1000.)*3.233-1.01*(rho_sn/1000.)+0.138; # Unit: (W m-1 C-1)

        self.Csn = rho_sn *0.+ 2.09E3 ;                                                # Unit: J m-3 C-1

    #   update_ssnow_thermal_properties()
    #-------------------------------------------------------------------
    def update_TOP_temperatures(self):

        #---------------------------------------------------------
        #   1.  Estimating vegetation effect
        #       deta_Tsn -- eq-7, Anisimov et al. 1997
        #       deta_Asn -- eq-2, Sazonova et al., 2003
        #       Tvg -- mean annual temperature Page-129, Sazonova et al., 2003
        #       Avg -- amplitude bellow snow OR top of vegetation
        #--------------------------------------------------

        tao = self.T_air*0.0 + self.sec_per_year;        
        
        K_diffusivity = self.Ksn/(self.rho_snow*self.Csn)
        
        temp = np.exp(-1.0*self.h_snow*np.sqrt(np.pi/(tao*K_diffusivity)))
        deta_Tsn = self.A_air*(1.0 - temp);
        deta_Asn = 2.0/np.pi*deta_Tsn;

        Tvg = self.T_air + deta_Tsn;
        Avg = self.A_air - deta_Asn;

        #---------------------------------------------------------
        #   2.  Estimating Snow Effects
        #       deta_A1 -- winter vegetation thermal effects: eq-10, Anisimov et al. 1997
        #       deta_A2 -- summer vegetation thermal effects: eq-11, Anisimov et al. 1997
        #       deta_Av -- Effects of vegetation on seasonal amplitude of temperature, eq-8
        #       deta_Tv -- Effects of vegetation on an annual mean temperature, eq-9
        #       Tgs, Ags -- mean annual gs temperature and amplitude eq-13,14 Sazonova et al., 2003
        #--------------------------------------------------
        temp = 1.- np.exp(-1.*self.Hvgf*np.sqrt(np.pi/(self.Dvf*2.*self.tao1)))
        deta_A1 = (Avg - Tvg) * temp;

        temp = 1.- np.exp(-1.*self.Hvgt*np.sqrt(np.pi/(self.Dvt*2.*self.tao2)))
        deta_A2 = (Avg  + Tvg) * temp;

        deta_Av = (deta_A1*self.tao1+deta_A2*self.tao2) / tao;

        deta_Tv = (deta_A1*self.tao1-deta_A2*self.tao2) / tao * (2. / np.pi)

        Tgs = Tvg + deta_Tv;
        Ags = Avg - deta_Av;

        #---------------------------------------------------------
        #   3.  Calculates Tps_Numerator;
        #       eq-14, Anisimov et al. 1997
        #--------------------------------------------------
        Tps_numerator = 0.5*Tgs*(self.Kf+self.Kt)\
                            +(Ags*(self.Kt-self.Kf)/np.pi\
                            *(Tgs/Ags*np.arcsin(Tgs/Ags)\
                            +np.sqrt(1.-(np.pi**2.0/Ags**2.0))));

        #---------------------------------------------------------
        #   4.  Calculates temperature at the top of permafrost
        #       Tps -- eq-14 cont., Anisimov et al. 1997
        #--------------------------------------------------

        n_grid = np.size(self.lat)
        
        if n_grid >1 :               
        
            K_star = self.Kf
            K_star[np.where(Tps_numerator>0.0)] = self.Kt[np.where(Tps_numerator>0.0)];
            
        else:
            if Tps_numerator<=0.0:
                K_star = self.Kf
            else:
                K_star = self.Kt
            

        self.Tgs=Tgs
        self.Ags=Ags
        self.Tps_numerator=Tps_numerator

        self.Tps = self.Tps_numerator/K_star

    #   update_TOP_temperatures()
    #-------------------------------------------------------------------
    def update_ALT(self):

        #---------------------------------------------------------
        #       Calculates active layer thickness
        #       Aps  -- eq-4, Romanovsky et al. 1997
        #       Zs -- eq-5, Romanovsky et al. 1997
        #       Zal -- eq-3, Romanovsky et al. 1997
        #--------------------------------------------------

        tao = self.T_air*0.0 + self.sec_per_year;

        n_grid = np.size(self.lat) 

        if n_grid > 1:        
        
            K = self.Kf
            C = self.Cf       
                    
            K[np.where(self.Tps_numerator>0.0)] = self.Kt[np.where(self.Tps_numerator>0.0)]
            C[np.where(self.Tps_numerator>0.0)] = self.Ct[np.where(self.Tps_numerator>0.0)]
            
        else:
            
            if self.Tps_numerator<=0.0:
                K = self.Kf
                C = self.Cf
            else:
                K = self.Kt
                C = self.Ct
                
        Aps = (self.Ags - abs(self.Tps))/np.log((self.Ags+self.L/(2.*C)) / \
                    (abs(self.Tps)+self.L/(2.*C))) - self.L/(2.*C);

        Zc = (2.*(self.Ags - abs(self.Tps))*np.sqrt((K*tao*C)/np.pi)) / \
                    (2.*Aps*C + self.L);

        Zal = (2.*(self.Ags - abs(self.Tps))*np.sqrt(K*tao*C/np.pi) \
                +(2.*Aps*C*Zc+self.L*Zc)*self.L*np.sqrt(K*tao/(np.pi*C)) \
                /(2.*self.Ags*C*Zc + self.L*Zc +(2.*Aps*C+self.L)*np.sqrt(K*tao/(np.pi*C)))) \
                /(2.*Aps*C+ self.L);

        if n_grid > 1:        
        
            Zal[np.where(Zal<=0.)] = -999.99
            Zal[np.where(self.Tps_numerator>0.0)] = -999.99 # Seasonal Frozen Ground
            Zal[np.where(np.isnan(Zal))] = -999.99
            
        else:
            
            if self.Tps_numerator>0.0 or Zal<=0.0 or np.isnan(Zal):
                Zal = -999.99
                
        self.Zal = Zal;
        
    #   update_ALT()
    #-------------------------------------------------------------------
    def update_ground_temperatures(self):
        # in this method there is only one output the temperature at the top of permafrost
        # TTOP
        self.update_soil_heat_capacity()
        self.update_soil_thermal_conductivity()
        self.update_snow_thermal_properties()
        
        tao = self.T_air*0.0 + self.sec_per_year;

        # Update mean temperatures for warmes and coldest seasons similar to Nelson & Outcalt 87
        # Cold and Warm Season, Page-129, Sazonova, 2003
        self.tao1 = tao*(0.5 - 1./np.pi*np.arcsin(self.T_air/self.A_air));
        self.tao2 = tao - self.tao1;
        self.L=self.Lf*1000.*self.vwc_H2O

        self.update_TOP_temperatures()

    #   update_ground_temperatures()
    #-------------------------------------------------------------------
    def close_input_files(self):

        if (self.T_air_type     != 'Scalar'): self.T_air_unit.close()
        if (self.A_air_type     != 'Scalar'): self.A_air_unit.close()
        if (self.h_snow_type    != 'Scalar'): self.h_snow_unit.close()
        if (self.rho_snow_type  != 'Scalar'): self.rho_snow_unit.close()
        if (self.vwc_H2O_type   != 'Scalar'): self.vwc_H2O_unit.close()
        if (self.Hvgf_type      != 'Scalar'): self.Hvgf_unit.close()
        if (self.Hvgt_type      != 'Scalar'): self.Hvgt_unit.close()
        if (self.Dvf_type       != 'Scalar'): self.Dvf_unit.close()
        if (self.Dvt_type       != 'Scalar'): self.Dvt_unit.close()
        if (self.lat_type       != 'Scalar'): self.lat_unit.close()
        if (self.lon_type       != 'Scalar'): self.lon_unit.close()    

    #   close_input_files()
    #-------------------------------------------------------------------
    
    def Extract_Soil_Texture_Loops(self):
        
        p_clay_list = self.lon*0.;
        p_sand_list = self.lon*0.;
        p_silt_list = self.lon*0.;
        p_peat_list = self.lon*0.;
        
        n_grid = np.size(p_clay_list)    

        if n_grid > 1:        
        
            for i in range(n_grid):           
                
                input_lat   = self.lat[i]
                input_lon   = self.lon[i]
                
                [p_clay0, p_sand0, p_silt0, p_peat0] = self.Extract_Soil_Texture(input_lat, input_lon);
            
                p_clay_list[i] = p_clay0            
                p_sand_list[i] = p_sand0        
                p_silt_list[i] = p_silt0        
                p_peat_list[i] = p_peat0
        else:
            
            input_lat   = self.lat
            input_lon   = self.lon
                
            [p_clay0, p_sand0, p_silt0, p_peat0] = self.Extract_Soil_Texture(input_lat, input_lon);
            
            p_clay_list = p_clay0            
            p_sand_list = p_sand0        
            p_silt_list = p_silt0        
            p_peat_list = p_peat0
                         
                    
        self.p_clay = p_clay_list
        self.p_sand = p_sand_list
        self.p_silt = p_silt_list
        self.p_peat = p_peat_list
        

    def Extract_Soil_Texture(self, input_lat, input_lon): 
    
        """ 
        The function is to extract the grid value from matrix,
        according to input of latitude and longitude;
        
        INPUTs:
                input_lat: Latitude;
                input_lon: Longitude;
                lon_grid : Array of longitude
                lat_grid : Array of latitude
                p_data   : Matrix of data (from NetCDF file)
                
        OUTPUTs:
                q_data: grid value (SINGLE)   
                        
        DEPENDENTs:
                None 
        """
            
        import numpy as np
        
        lon_grid_scale = 0.05;
        lat_grid_scale = 0.05;
        
        lon_grid_top = self.lon_grid + lon_grid_scale / 2.0;
        lat_grid_top = self.lat_grid + lat_grid_scale / 2.0;
        
        lon_grid_bot = self.lon_grid - lon_grid_scale / 2.0;
        lat_grid_bot = self.lat_grid - lat_grid_scale / 2.0;
        
        # Get the index of input location acccording to lat and lon inputed
        
        idx_lon = np.where((input_lon <= lon_grid_top) & (input_lon >= lon_grid_bot))          
        idx_lat = np.where((input_lat <= lat_grid_top) & (input_lat >= lat_grid_bot))
        
        idx_lon = np.array(idx_lon)
        idx_lat = np.array(idx_lat)
        
        if np.size(idx_lon) >= 1 and np.size(idx_lat) >= 1:
            clay_perc  = self.Clay_percent[idx_lat[0,0], idx_lon[0,0]]
            sand_perc  = self.Sand_percent[idx_lat[0,0], idx_lon[0,0]]
            silt_perc  = self.Silt_percent[idx_lat[0,0], idx_lon[0,0]]
            peat_perc  = self.Peat_percent[idx_lat[0,0], idx_lon[0,0]]
        else:
            clay_perc  = np.nan;
            sand_perc  = np.nan;
            silt_perc  = np.nan;
            peat_perc  = np.nan;            
    
        return clay_perc, sand_perc, silt_perc, peat_perc


    def read_whole_soil_texture_from_GSD(self):
        
        Clay_file = self.get_param_nc4_filename("T_CLAY",
                                                self.permafrost_dir)
        Sand_file = self.get_param_nc4_filename("T_SAND",
                                                self.permafrost_dir)
        Silt_file = self.get_param_nc4_filename("T_SILT",
                                                self.permafrost_dir)
        Peat_file = self.get_param_nc4_filename("T_OC",
                                                self.permafrost_dir)
                                                
        lonname    = 'lon';
        latname    = 'lat';
        
        varname    = 'T_CLAY';                                        
        [lat_grid, lon_grid, Clay_percent] = self.import_ncfile(Clay_file, 
                                                lonname, latname, varname)
        varname    = 'T_SAND';                                        
        [lat_grid, lon_grid, Sand_percent] = self.import_ncfile(Sand_file, 
                                                lonname, latname, varname)
         
        varname    = 'T_SILT';                                        
        [lat_grid, lon_grid, Silt_percent] = self.import_ncfile(Silt_file, 
                                                lonname, latname, varname)
                                                
        varname    = 'T_OC';                                        
        [lat_grid, lon_grid, Peat_percent] = self.import_ncfile(Peat_file, 
                                                lonname, latname, varname)
        
        self.Clay_percent = Clay_percent;
        self.Sand_percent = Sand_percent;
        self.Silt_percent = Silt_percent;
        self.Peat_percent = Peat_percent;
        self.lon_grid     = lon_grid;
        self.lat_grid     = lat_grid;
    
    def import_ncfile(self, input_file, lonname,  latname,  varname): 
                                           
        from netCDF4 import Dataset
        
        # Read the nc file 
        
        fh = Dataset(input_file, mode='r')
        
        # Get the lat and lon
        
        lon_grid = fh.variables[lonname][:]; 
        lat_grid = fh.variables[latname][:];
        
        p_data  = fh.variables[varname][:];
        
        return lat_grid,lon_grid,p_data
        
    def initialize(self, cfg_file=None, mode="nondriver",
                   SILENT=False):

        #---------------------------------------------------------
        # Notes:  Need to make sure than h_swe matches h_snow ?
        #         User may have entered incompatible values.
        #---------------------------------------------------------
        # (3/14/07) If the Energy Balance method is used for ET,
        # then we must initialize and track snow depth even if
        # there is no snowmelt method because the snow depth
        # affects the ET rate.  Otherwise, return to caller.
        #---------------------------------------------------------
        if not(SILENT):
            print ' '
            print 'Ku model component: Initializing...'

        self.status     = 'initializing'  # (OpenMI 2.0 convention)
        self.mode       = mode
        self.cfg_file   = cfg_file
        #print mode, cfg_file

        #-----------------------------------------------
        # Load component parameters from a config file
        #-----------------------------------------------
        self.set_constants()
        self.initialize_config_vars()
        # At this stage we are going to ignore read_grid_info b/c
        # we do not have rti file associated with our model
        # we also skipping the basin_vars which calls the outlets
        #self.read_grid_info()
        #self.initialize_basin_vars()
        
        self.initialize_time_vars()

        if (self.comp_status == 'Disabled'):
            #########################################
            #  DOUBLE CHECK THIS; SEE NOTES ABOVE
            #########################################
               ####### and (ep.method != 2):  ??????
            if not(SILENT):
                print 'Permafrost component: Disabled.'
            self.lat    = self.initialize_scalar(0, dtype='float64')
            self.lon    = self.initialize_scalar(0, dtype='float64')
            self.T_air  = self.initialize_scalar(0, dtype='float64')
            self.h_snow = self.initialize_scalar(0, dtype='float64')
            self.vwc_H2O= self.initialize_scalar(0, dtype='float64')
            self.Hvgf   = self.initialize_scalar(0, dtype='float64')
            self.Hvgt   = self.initialize_scalar(0, dtype='float64')
            self.Dvf    = self.initialize_scalar(0, dtype='float64')
            self.Dvt    = self.initialize_scalar(0, dtype='float64')
            self.DONE   = True
            self.status = 'initialized'
            return

        #---------------------------------------------
        # Open input files needed to initialize vars
        #---------------------------------------------
        self.open_input_files()
        self.read_input_files()
        
        #---------------------------------------------
        # Extract soil texture from Grid Soil Database (Netcdf files)
        # according to locations
        #---------------------------------------------
        self.read_whole_soil_texture_from_GSD()  # import whole GSD      
        self.Extract_Soil_Texture_Loops()        # Extract soil texture for each cell.
        
        #---------------------------
        # Initialize computed vars
        #---------------------------
        #self.check_input_types()  # (maybe not used yet)

        self.status = 'initialized'
        
    def read_next_modified_KU(self, file_name, var_type, \
                  dtype='Float32', factor=1.0):
    
        #-------------------------------------------------------
        # (5/7/09) Allow "dtype" to be given using RTI types.
        # (4/21/16) Elchin Jafarov introduced this function b/c
        # he was not sure how to deal with rti in the original function
        # this version foes not have grid choice
        #-------------------------------------------------------
        rti_types = ['BYTE','INTEGER','LONG','FLOAT','DOUBLE']
        if (dtype.upper() in rti_types):
            dtype_map = {'BYTE':'uint8', 'INTEGER':'int16',
                         'LONG':'int32',
                         'FLOAT':'float32', 'DOUBLE':'float64'}
            dtype = dtype_map[dtype]
    
    
        if (var_type.lower() == 'scalar'):
            #-------------------------------------------
            # Scalar value was entered by user already
            #-------------------------------------------
            data = None
        elif (var_type.lower() == 'time_series'):
            #----------------------------------------------
            # Time series: Read scalar value from file.
            # File is ASCII text with one value per line.
            #----------------------------------------------
            data = np.loadtxt(file_name)
    
        else:
            raise RuntimeError('No match found for "var_type".')
            return None
    
        #---------------------------------------------
        # Multiply by a conversion or scale factor ?
        #---------------------------------------------
        if (factor != 1) and (data is not None):
            data = (data * factor)            
    
        #-----------------------------------------------------
        # Values must usually be read from file as FLOAT32
        # but then need to be returned as FLOAT64. (5/17/12)
        # But numpy.float64( None ) = NaN. (5/18/12)
        #-----------------------------------------------------
        if (data is None):
            return
        else:
            return np.float64( data )
