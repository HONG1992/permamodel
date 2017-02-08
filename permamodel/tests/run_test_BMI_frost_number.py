#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
A simple BMI FrostNumberModel example. Run with:

  $ python -m permamodel.tests.run_test_BMI_frost_number

Created on Tue Jan 10 10:56:16 2017
@author: kangwang
"""

import os
import sys
from permamodel.components import bmi_frost_number
from .. import examples_directory


cfg_file = os.path.join(examples_directory,
                        'Frostnumber_example_singlesite_singleyear.cfg')
x = bmi_frost_number.BmiFrostnumberMethod()

x.initialize(cfg_file)
x.update()
x.finalize()

print x.get_value('frostnumber__air')
