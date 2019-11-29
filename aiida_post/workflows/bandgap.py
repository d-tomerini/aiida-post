"""
Very basic workchain to calculate the bandgap
from the result of a PwBandsWorkChain workflow
"""

from __future__ import absolute_import
from aiida import orm
from aiida.engine import WorkChain, ToContext


class PwBandGapWorkChain(WorkChain):
    """
    Extension to the PwBandStructureWorkChain to
    compute a band gap for a given structure
    using Quantum ESPRESSO pw.x
    """

    @classmethod
    def define(cls, spec):
        super(PwBandGapWorkChain, cls).define(spec)
        #inputs
        spec.input('code', valid_type=orm.Code)
        spec.input('structure', valid_type=orm.StructureData)
        #outline
        spec.outline(cls.run_band_structure, cls.get_bandgap)
        #outputs
        spec.output('output_parameters', valid_type=orm.Dict)

    def run_band_structure(self):
        """
        Run the PwBandsWorkChain to compute the band structure
        """

        from aiida.plugins import WorkflowFactory
        PwBandStructureWorkChain = WorkflowFactory('quantumespresso.pw.band_structure')
        inputs = {'structure': self.inputs.structure, 'code': self.inputs.code}

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
        self.report('Calculation completed')
        return
