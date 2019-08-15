# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aiida import orm
from aiida.engine import WorkChain
from aiida.orm.nodes.data.array.bands import find_bandgap
from aiida_quantumespresso.utils.resources import get_default_options
import aiida_quantumespresso.utils.workflows.pw.band_structure


class PwBandGapWorkChain(WorkChain):
    """
    Extension to the PwBandStructureWorkChain to
    compute a band gap for a given structure
    using Quantum ESPRESSO pw.x
    """

    @classmethod
    def define(cls, spec):
        super(PwBandGapWorkChain, cls).define(spec)
        spec.input('code', valid_type=orm.Code)
        spec.input('structure', valid_type=orm.StructureData)
        spec.outline(cls.run_band_structure, cls.get_bandgap)
        spec.output('band_gap', valid_type=orm.Float)

    def run_band_structure(self):
        """
        Run the PwBandsWorkChain to compute the band structure
        """

        inputs = {'structure': self.inputs.structure, 'code': self.inputs.code}

        running = self.submit(PwBandsWorkChain, **inputs)
        self.report('launching PwBandsWorkChain<{}>'.format(running.pk))
        return ToContext(workchain_bands=running)

    def get_bandgap(self):
        """
        From the band object obtained by the band structure
        calculation, run a simple script to obtain the band gap
        """

        bands = self.ctx.workchain_bands.outputs.band_structure
        is_insulator, bandgap = bands.find_bandgap()
        self.report('calculation completed')
        self.ctx.band_gap = bandgap

        return
