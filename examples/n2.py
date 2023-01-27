#!/usr/bin/env runaiida
"""Example script to run a simple N2 calculation with aiida-autocas."""

from aiida.plugins import DataFactory
from aiida import orm
from aiida import engine

# Generate code
code = orm.load_code(label="autocas@local")

# Create Structure
struct_factory = DataFactory("core.structure")
struc = struct_factory(pbc=[False, False, False])
struc.append_atom(position=(0.00, 0.00, 0.00), symbols="N")
struc.append_atom(position=(3.00, 0.00, 0.00), symbols="N")

# Generate Builder
builder = code.get_builder()
builder.structure = struc

# Perform Calculation
result = engine.run(builder)
