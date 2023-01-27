"""Calculation plugin for AutoCAS."""
from aiida.common import datastructures
from aiida.engine import CalcJob
from aiida.orm import Bool, Int, Str, ArrayData, Float, StructureData
from aiida.orm.nodes.data.base import to_aiida_type


class AutoCASCalculation(CalcJob):
    """
    Aiida CalcJob plugin for performing AutoCAS calculation to automatically
    determine the active space and perform a DMRG, CASSCF or CASCI calculation
    using the chosen active space.
    """

    _YAML_PARAMETER_FILE = "autocas.yaml"
    OUTPUT_FILE = "autocas.out"
    _XYZ_FILE = "autocas.xyz"

    @classmethod
    def define(cls, spec):
        super().define(spec)

        # Define Inputs
        spec.input(
            "structure",
            valid_type=StructureData,
            help="Structure of the molecular system",
        )
        spec.input(
            "charge",
            valid_type=Int,
            serializer=to_aiida_type,
            help="Charge of the molecular system",
            default=lambda: Int(0),
        )
        spec.input(
            "multiplicity",
            valid_type=Int,
            serializer=to_aiida_type,
            help="Multiplicity of the molecular system",
            default=lambda: Int(1),
        )
        spec.input(
            "double_d_shell",
            valid_type=Bool,
            serializer=to_aiida_type,
            help="Whether to include the d shell for 3d transition metals",
            default=lambda: Bool(True),
        )
        spec.input(
            "interface",
            valid_type=Str,
            serializer=to_aiida_type,
            help="Name of the calculation interface to use",
            default=lambda: Str("chronusq"),
        )
        spec.input(
            "method",
            valid_type=Str,
            serializer=to_aiida_type,
            help="Method to compute the energy using the chosen active space (e.g. dmrg_ci, casscf, casci)",
            default=lambda: Str("dmrg_ci"),
        )
        spec.input(
            "dmrg_bond_dimension",
            valid_type=Int,
            serializer=to_aiida_type,
            help="DMRG bond dimension for the final calculation of energy (using the chosen active space)",
            default=lambda: Int(1000),
        )
        spec.input(
            "dmrg_sweeps",
            valid_type=Int,
            serializer=to_aiida_type,
            help="Number of DMRG sweeps to perform of the final calculation (using the chosen active space)",
            default=lambda: Int(10),
        )
        spec.input(
            "basis_set",
            valid_type=Str,
            serializer=to_aiida_type,
            help="Basis set to use for all calculations",
            default=lambda: Str("def2-svpd"),
        )
        spec.input(
            "large_cas_protocol",
            valid_type=Bool,
            serializer=to_aiida_type,
            help="Whether to use the large CAS protocol (helpful for molecules with too large valence active space)",
            default=lambda: Bool(False),
        )

        # Define Outputs
        spec.output(
            "n_active_electrons",
            valid_type=Int,
            help="Number of electrons in active space",
        )
        spec.output(
            "n_active_orbitals",
            valid_type=Int,
            help="Number of orbitals in active space",
        )
        spec.output(
            "active_orbitals",
            valid_type=ArrayData,
            help="Indices of the orbitals in the active space",
        )
        spec.output(
            "energy",
            valid_type=Float,
            help="Energy using the method given in the input with the chosen active space",
        )

        # Error Codes
        spec.exit_code(
            300,
            "ERROR_CALCULATION_FAILED",
            message="Something went wrong during the calculation",
        )
        spec.exit_code(
            301,
            "ERROR_PARSER_FAILED",
            message="The parser did not find all of the data in the output file",
        )
        spec.exit_code(
            303,
            "ERROR_MISSING_OUTPUT_FILE",
            message="Output file was not returned from the autocas job calc",
        )

        # Meta Data
        spec.inputs["metadata"]["options"]["parser_name"].default = "autocas"
        spec.inputs["metadata"]["options"]["resources"].default = {
            "num_machines": 1,
            "num_mpiprocs_per_machine": 1,
        }

    def prepare_for_submission(self, folder):
        """
        Prepare the AutoCAS calculation for submission
        """

        # Create YAML parameter file to use as input for AutoCAS
        indent = "    "
        lines = "---\n"
        lines += "large_cas: " + str(self.inputs.large_cas_protocol.value) + "\n"
        lines += "molecule:\n"
        lines += indent + "charge: " + str(self.inputs.charge.value) + "\n"
        lines += (
            indent + "spin_multiplicity: " + str(self.inputs.multiplicity.value) + "\n"
        )
        lines += (
            indent + "double_d_shell: " + str(self.inputs.double_d_shell.value) + "\n"
        )
        lines += indent + "xyz_file: " + self._XYZ_FILE + "\n"
        lines += "interface:\n"
        lines += indent + "interface: " + str(self.inputs.interface.value) + "\n"
        lines += indent + "project_name: aiida_autocas\n"
        lines += indent + "settings:\n"
        lines += (
            indent
            + indent
            + "dmrg_bond_dimension: "
            + str(self.inputs.dmrg_bond_dimension.value)
            + "\n"
        )
        lines += (
            indent
            + indent
            + "dmrg_sweeps: "
            + str(self.inputs.dmrg_sweeps.value)
            + "\n"
        )
        lines += (
            indent + indent + "basis_set: " + str(self.inputs.basis_set.value) + "\n"
        )
        lines += indent + indent + "method: " + str(self.inputs.method.value) + "\n"
        lines += indent + indent + "xyz_file: " + self._XYZ_FILE + "\n"

        with folder.open(self._YAML_PARAMETER_FILE, "w") as handle:
            handle.write(lines)

        # Create XYZ file for AutoCAS
        sites = self.inputs.structure.sites
        lines = str(len(sites)) + "\n"
        lines += "AutoCAS Structure\n"
        for site in sites:
            lines += "{} {} {} {}".format(site.kind_name, *site.position) + "\n"

        with folder.open(self._XYZ_FILE, "w") as handle:
            handle.write(lines)

        # Handle Code info
        codeinfo = datastructures.CodeInfo()
        codeinfo.cmdline_params = ["-y", self._YAML_PARAMETER_FILE]
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.OUTPUT_FILE

        # Prepare Calc Info
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.retrieve_list = [self.OUTPUT_FILE]

        return calcinfo
