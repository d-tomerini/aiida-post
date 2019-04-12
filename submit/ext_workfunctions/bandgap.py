from __future__ import absolute_import

from aiida import orm
from aiida.engine import WorkChain, ToContext
from aiida.plugins import WorkflowFactory

from aiida_quantumespresso.utils.mapping import update_mapping
from aiida_quantumespresso.utils.protocols.pw import ProtocolManager
from aiida_quantumespresso.utils.pseudopotential import get_pseudos_from_dict
from aiida_quantumespresso.utils.resources import get_default_options

PwBandsWorkChain = WorkflowFactory('quantumespresso.pw.bands')


class PwBandGapWorkChain(WorkChain):
    """
    Workchain to automatically compute a bandgap for a given structure using Quantum ESPRESSO pw.x
    Heavily borrowed from existing workchain for bandstructure
    in quantum espresso,
    plus just a little script at the end 
    """

    @classmethod
    def define(cls, spec):
        super(PwBandGapWorkChain, cls).define(spec)
        spec.input('structure', valid_type=orm.StructureData)
        spec.input('clean_workdir', valid_type=orm.Bool, default=orm.Bool(False))
        spec.input('nbands_factor', valid_type=orm.Float, default=orm.Float(1.2))
        spec.outline(
            cls.run_bands,
            cls.bandgap,
            cls.results,
        )
        spec.output('band_gap', valid_type=orm.Dict)


    def run_bands(self):
        """Run the PwBandsWorkChain"""
        inputs = AttributeDict(self.exposed_inputs(PwBaseWorkChain, namespace='scf'))
        inputs.structure = self.ctx.current_structure
        inputs.parameters = inputs.parameters.get_dict()
        inputs.parameters.setdefault('CONTROL', {})
        inputs.parameters['CONTROL']['calculation'] = 'scf'

        inputs = prepare_process_inputs(PwBaseWorkChain, inputs)
        running = self.submit(PwBaseWorkChain, **inputs)

        self.report('launching PwBaseWorkChain<{}> in {} mode'.format(running.pk, 'scf'))

        return ToContext(workchain_scf=running)

    def inspect_scf(self):
        """Verify that the PwBaseWorkChain for the scf run finished successfully."""
        workchain = self.ctx.workchain_scf

        if not workchain.is_finished_ok:
            self.report('scf PwBaseWorkChain failed with exit status {}'.format(workchain.exit_status))
            return self.exit_codes.ERROR_SUB_PROCESS_FAILED_SCF
        else:
            self.ctx.current_folder = workchain.outputs.remote_folder

    def run_bands(self):
        """Run the PwBaseWorkChain in bands mode along the path of high-symmetry determined by seekpath."""

        # Get info from SCF on number of electrons and number of spin components
        scf_out_dict = self.ctx.workchain_scf.outputs.output_parameters.get_dict()
        nelectron = int(scf_out_dict['number_of_electrons'])
        nspin = int(scf_out_dict['number_of_spin_components'])
        nbands = max(
            int(0.5 * nelectron * nspin * self.inputs.nbands_factor.value),
            int(0.5 * nelectron * nspin) + 4 * nspin)

        inputs = AttributeDict(self.exposed_inputs(PwBaseWorkChain, namespace='bands'))
        inputs.parameters = inputs.parameters.get_dict()

        inputs.parameters.setdefault('CONTROL', {})
        inputs.parameters.setdefault('SYSTEM', {})
        inputs.parameters.setdefault('ELECTRONS', {})

        inputs.parameters['CONTROL']['restart_mode'] = 'restart'
        inputs.parameters['CONTROL']['calculation'] = 'bands'
        inputs.parameters['ELECTRONS']['diagonalization'] = 'cg'
        inputs.parameters['ELECTRONS']['diago_full_acc'] = True
        inputs.parameters['SYSTEM']['nbnd'] = nbands

        if 'kpoints' not in self.inputs.bands:
            inputs.kpoints = self.ctx.kpoints_path

        inputs.structure = self.ctx.current_structure
        inputs.parent_folder = self.ctx.current_folder

        inputs = prepare_process_inputs(PwBaseWorkChain, inputs)
        running = self.submit(PwBaseWorkChain, **inputs)

        self.report('launching PwBaseWorkChain<{}> in {} mode'.format(running.pk, 'bands'))

        return ToContext(workchain_bands=running)

    def inspect_bands(self):
        """Verify that the PwBaseWorkChain for the bands run finished successfully."""
        workchain = self.ctx.workchain_bands

        if not workchain.is_finished_ok:
            self.report('bands PwBaseWorkChain failed with exit status {}'.format(workchain.exit_status))
            return self.exit_codes.ERROR_SUB_PROCESS_FAILED_BANDS

    def results(self):
        """Attach the desired output nodes directly as outputs of the workchain."""
        self.report('workchain succesfully completed')
        self.out('scf_parameters', self.ctx.workchain_scf.outputs.output_parameters)
        self.out('band_parameters', self.ctx.workchain_bands.outputs.output_parameters)
        self.out('band_structure', self.ctx.workchain_bands.outputs.output_band)

    def on_terminated(self):
        """
        If the clean_workdir input was set to True, recursively collect all called Calculations by
        ourselves and our called descendants, and clean the remote folder for the CalcJobNode instances
        """
        super(PwBandsWorkChain, self).on_terminated()

        if self.inputs.clean_workdir.value is False:
            self.report('remote folders will not be cleaned')
            return

        cleaned_calcs = []

        for called_descendant in self.calc.called_descendants:
            if isinstance(called_descendant, orm.CalcJobNode):
                try:
                    called_descendant.outputs.remote_folder._clean()
                    cleaned_calcs.append(called_descendant.pk)
                except (IOError, OSError, KeyError):
                    pass

        if cleaned_calcs:
            self.report('cleaned remote folders of calculations: {}'.format(' '.join(map(str, cleaned_calcs))))
