# AiiDA Scine AutoCAS

[AiiDA](http://www.aiida.net/) plugin for [Scine AutoCAS](https://scine.ethz.ch/download/autocas).

## Installation

The plugin can be installed using pip and the pyproject.toml file assuming AiiDA has already been installed.
```bash
git clone https://github.com/microsoft/aiida-autocas.git
cd aiida-autocas
pip install -e .
```

## Usage

First add the AutoCAS code to verdi following the instructions
[here](https://aiida.readthedocs.io/projects/aiida-core/en/latest/howto/run_codes.html). The AutoCAS plugin is
implemented as a [CalcJob](https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/calculations/concepts.html#calculation-jobs)
where with the name `autocas`.  A sample script is given in [examples](https://github.com/microsoft/aiida-autocas/blob/main/examples/n2.py).

### Calculation Input Parameters
The CalcJob is implemented with a number of input parameters that allow you to modify the
job. Almost all of these input variables already have default values except for **structure**,
which provides the molecular geometry. The following table outlines the input parameters
and the default values being used.

| Variable | Type  | Default | Description|
|----------|-------|---------|-----------------|
| structure           | Structure Data | None      | Molecular geometry of the system|
| basis_set           | String         | def2-svpd | The basis set to use for the quantum chemistry calculations |
| charge              | Int            | 0         | Charge of the system            |
| multiplicity        | Int            | 1         | Spin multiplicity of the system |
| double_d_shell      | Bool           | True      | Whether to include the d shell for 3d transition metals |
| interface           | String         | chronusq  | Which interface to quantum chemistry software should be used |
| method              | String         | dmrg_ci   | Which active space method to use for the final energy (e.g. dmrg_ci, casscf, casci) |
| dmrg_bond_dimension | Int            | 1000      | The bond dimension to use for the final DMRG calculation when using method=dmrg_ci |
| dmrg_sweeps         | Int            | 10        | The number of DMRG sweeps to perform for the final DMRG calculation when using method=dmrg_ci |
| large_cas_protocol  | Bool           | False     | Whether to use the Large CAS protocol |


### Calculation Output Results
Upon completion of the CalcJob, the following results (using
[AiiDA data types](https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/data_types.html))
are returned.

| Variable   |  Type   | Description |
|------------|---------|-------------|
| n_active_electrons | Int  | Number of electrons in determined active space |
| n_active_orbitals  | Int  | Number of orbitals in the choosen active space |
| active_orbitals    | ArrayData | One dimensional array containing the orbital indices of the choosen active space |
| energy             | Float | Energy of the system using the method choosen in the input (e.g. DRMG, CASCI, CASSCF) |



## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
