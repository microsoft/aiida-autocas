

from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory
from aiida.orm import Int, Float, ArrayData
import numpy as np
import re

AutoCASCalculation = CalculationFactory("autocas")

class AutoCASParser(Parser):
    """
    Parser class for AutoCAS calculation job.
    """

    def parse(self, **kwargs):
        """
        Parse the AutoCAS output file and store the results in the database
        """

        # Check that the number of files
        files_retrieved = self.retrieved.list_object_names()
        files_expected = [AutoCASCalculation._OUTPUT_FILE]
        # Note: set(A) <= set(B) checks whether A is a subset of B
        if not set(files_expected) <= set(files_retrieved):
            self.logger.error(
                f"Found files '{files_retrieved}', expected to find '{files_expected}'"
            )
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILE

        # if there's an error in stderr, calculation has likely failed
        stderr_content = self.node.get_scheduler_stderr()
        if stderr_content and "error" in stderr_content.lower():
            self.logger.error(f"Error(s) occurred during execution:\n{stderr_content}")
            return self.exit_codes.ERROR_CALCULATION_FAILED

        with self.retrieved.open(AutoCASCalculation._OUTPUT_FILE,'r') as file:
            output = file.read()
        
        # Use regex to parse output
        # Parse Active space
        grp = re.search( r'Final\s*active\s*space\s*CAS\s*\(\s*e,\s*o\s*\)\s*:\s*\(\s*(\d+),\s*(\d+)\s*\)', output )
        if grp:
            self.out('n_active_electrons', Int(int(grp.group(1))))
            self.out('n_active_orbitals', Int(int(grp.group(2))))
        else:
            self.logger.error("Could not find active space in autocas output file")
            return self.exit_codes.ERROR_PARSER_FAILED

        grp = re.search( r'Final\s*energy:\s*(-*[\d]+.[\d]+)', output)
        if grp:
            self.out('energy', Float(float(grp.group(1))))
        else:
            self.logger.error("Could not find energy in autocas output file")
            return self.exit_codes.ERROR_PARSER_FAILED

        grp = re.search( r'Final\s*orbital\s*indices:\s*\[([\d,\s]+)\]', output)
        if grp:
            str_list = grp.group(1).split(',')
            int_list = [int(i) for i in str_list]
            array = ArrayData()
            array.set_array('active_orbitals',np.array(int_list))
            self.out('active_orbitals',array)
        else:
            self.logger.error("Could not find orbital indices in autocas output file")
            return self.exit_codes.ERROR_PARSER_FAILED

        return ExitCode(0)
