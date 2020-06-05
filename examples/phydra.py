# write the phydra "backend" up here, later to be imported from script outside of file!

import numpy as np
import xsimlab as xs 
     
    
@xs.process
class Environment:
    """
    This physical environment provides a base dimension (0D), that is inherited by other components,
    so that all components can be group at grid points of a larger grid
    
    can be extended to higher dimensions via another grid process, defining 'grid_dims'
    """
    model_dims = xs.variable(intent='in') #needs to be supplied
    
    env = xs.index(dims='env')
    
    comp_flux = xs.variable(intent='out', groups='component_flux')
    grid_fluxes = xs.group('grid_flux')
    
    def initialize(self):
        self.env = np.array([0])
    
    def run_step(self):
        self.comp_flux = sum((v for v in self.grid_fluxes))
        
      
    
    
@xs.process
class Component:
    """
    Basis for all components, defines the calculation of fluxes and state.
    specific fluxes, variables, and parameters need to be defined in subclass.
    """
    dim = xs.variable(intent='in', groups='component_dimension')
    
       
    @xs.runtime(args="step_delta")
    def run_step(self, dt):
        self.delta = sum((v for v in self.fluxes)) * dt  # multiply by time step

    def finalize_step(self):
        self.state += self.delta

@xs.process
class Phytoplankton(Component):
    P = xs.index(dims='P')
    
    state = xs.variable(intent='inout', dims=[(),('env', 'P')])
    
    fluxes = xs.group('P_flux')
    
    def initialize(self):
        self.P = np.arange(self.dim)

@xs.process
class Zooplankton(Component):
    Z = xs.index(dims='Z')
    
    state = xs.variable(intent='inout', dims=[(),('env', 'Z')])
    
    fluxes = xs.group('Z_flux')
    
    def initialize(self):
        self.Z = np.arange(self.dim)

           
@xs.process
class Flux:
    """
    Basis for all fluxes, defines the calculation of fluxes.
    specific fluxes, variables, and parameters need to be defined in subclass.
    """ 
    #model_dims = xs.foreign(Environment, 'model_dims')
    
@xs.process
class ConstantGrowth(Flux):
    
    P_state = xs.foreign(Phytoplankton, 'state')
    P_growth = xs.variable(intent='out', groups='P_flux')
    
    mu = xs.variable(intent='in', description='constant growth rate of phytoplankton')
    
    def run_step(self):
        self.P_growth = self.mu * self.P_state
        
@xs.process
class Grazing(Flux):
    
    P_state = xs.foreign(Phytoplankton, 'state')
    P_grazed = xs.variable(intent='out', groups='P_flux')
    
    time = xs.variable(intent='out')
    b = xs.variable(intent='in', description='initial grazing rate')
    c = xs.variable(intent='in', description='grazing increase rate')
    
    def initialize(self):
        self.time=0
    
    @xs.runtime(args="step_delta")
    def run_step(self, dt):
        self.time += dt
        self.P_grazed = - (self.b + self.c * self.time) * self.P_state
        
        
@xs.process
class ZooGrazing(Flux):
    
    P_state = xs.foreign(Phytoplankton, 'state')
    P_grazed = xs.variable(intent='out', groups='P_flux')
    Z_growth = xs.variable(intent='out', groups='Z_flux')
    
    b = xs.variable(intent='in', description='initial grazing rate')
    c = xs.variable(intent='in', description='grazing increase rate')
    
    def initialize(self):
        self.time=0
    
    @xs.runtime(args="step_delta")
    def run_step(self, dt):
        self.time += dt
        self.P_grazed = - (self.b + self.c * self.time) * self.P_state
        self.Z_growth = (self.b + self.c * self.time) * self.P_state
        
        
        
        
        