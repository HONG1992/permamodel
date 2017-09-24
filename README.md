[![Build Status](https://travis-ci.org/permamodel/permamodel.svg?branch=master)](https://travis-ci.org/permamodel/permamodel)
[![Code Health](https://landscape.io/github/permamodel/permamodel/master/landscape.svg?style=flat)](https://landscape.io/github/permamodel/permamodel/master)
[![Coverage Status](https://coveralls.io/repos/permamodel/permamodel/badge.svg?branch=master)](https://coveralls.io/r/permamodel/permamodel?branch=master)

# permamodel

 PermaModel project enables the broader use of permafrost models and consists of several permafrost models representing a range of capability and complexity. The PermaModel provides easy online access to everyone who want to use permafrost models, but lack the expertise and resources to develop them. It includes multiple sets of sample inputs representing a variety of conditions and locations to enable immediate use of any out of three permafrost models. It is built on the Community Surface Dynamics Modeling System (CSDMS) Modeling Framework platform. CSDMS provides an on-line environment where users can link and run models from multiple Earth science disciplines. We hope that the simple user interfaces, easy online access, open source models, and quick visualization tools can make permafrost models accessible to a broad audience well beyond the permafrost research community. These new easy-to-use modeling tools could be  useful to wide-range of users beyond the research community, such as educators, students, and policy-makers. 


Permamodel
==========

Permamodel is a collection of numerical permafrost models

Frostnumber
-----------
Calculates the frost number--an indication of the probability
of finding permafrost--at a site.  There are different versions of the
frost number depending on what data area available at the site.  

  The air frost number requires some indication of the annual temperature cycle.

  The surface frost number also requires indication of the year's precipitation.

  The Stefan frost number additionally incorporates soil information.


A sample project that exists as an aid to the `Python Packaging User Guide
<https://packaging.python.org>`_'s `Tutorial on Packaging and Distributing
Projects <https://packaging.python.org/en/latest/distributing.html>`_.

This projects does not aim to cover best practices for Python project
development as a whole. For example, it does not provide guidance or tool
recommendations for version control, documentation, or testing.

Ku
--

Implements a semi-empirical/analytical solution to soil conditions 


GIPL
----

GIPL is a detailed numerical model that solves for the temperature profile
of a soil column given its material properties and the temperature and
precipitation conditions it experiences. For more information please see <https://github.com/Elchin/GIPL> 

Installation
------------

The suite of permamodel routines as well as some useful ancillary packages 
can be installed using the bash script:

    $ permamodel/permamodel/examples/install\_pm.sh

If this file is downloaded to your system, you can change it to executable
and run it with:

    $ chmod +x ./install\_pm.sh
    $ ./install\_pm.sh 

By default, this will install a Python 2.7 environment and the permamodel
suite to the subdirectory ./pm\_env (or a different subdirectory, if specified
as a command line argument to install\_pm.sh).

How to build executables for the bmi-gipl_v0.1 model.
-----

The Fortran bindings for the Basic Modeling Interface of the GIPL model contains in bmi-giplf90_v0.1\bmi\bmi_impl.f90. 
The bmi-giplf90_v0.1 contains example of testing model against measured ground temperatures in 'examples' folder, and unit tests in 'testing' folder. The gipl_cfg.cfg is a configuration file containing an information about input/output files location and parameters setup.

To build the BMI Fortran-bindings and tests:

    $ mkdir _build && cd _build
    $ cmake ../ 
    $ make

Run all tests with:

    $ make test

Run an individual test file:
    
    $ cd testing
    $ ./irf_test
