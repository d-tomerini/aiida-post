# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aiida import orm
from aiida.engine import WorkChain, ToContext
from aiida_quantumespresso.workflows.pw.band_structure import PwBandStructureWorkChain


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
        spec.output('output_parameters', valid_type=orm.Dict)

    def run_band_structure(self):
        """
        Run the PwBandsWorkChain to compute the band structure
        """

        inputs = {
                'structure': self.inputs.structure,
                'code': self.inputs.code}

        running = self.submit(PwBandStructureWorkChain, **inputs)
        self.report('launching PwBandStructureWorkChain<{}>'.format(running.pk))
        return ToContext(workchain_bands=running)

    def get_bandgap(self):
        """
        From the band object obtained by the band structure
        calculation, run a simple script to obtain the band gap
        """
        from aiida.orm.nodes.data.array.bands import find_bandgap

        bands = self.ctx.workchain_bands.outputs.band_structure
        is_insulator, bandgap = find_bandgap(bands)
        output = {}
        output['band_gap'] = bandgap
        output['is_insulator'] = is_insulator
        self.out('output_parameters', Dict(dict=output))
        self.report('calculation completed')
        return
