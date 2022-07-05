import os
import siliconcompiler
import sys

openroad_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

mydir = os.path.dirname(__file__)
scdir = os.path.join(mydir, '..')
sys.path.append(os.path.join(scdir, 'util'))
import parse_target_config

def make_docs():
    # TODO: Docs
    chip = siliconcompiler.Chip('<design>')
    setup(chip)
    return chip

####################################################
# PDK and Flow Setup
####################################################
def setup(chip):
    # Collect basic values.
    design = chip.get('design')
    platform = 'sky130hd'

    # Set the target name.
    chip.set('option', 'target', 'sky130hd_orflow')

    # Load PDK, flow, and libs.
    chip.load_pdk('sky130hd_orflow')
    chip.load_flow('orflow')
    chip.load_lib('sky130hd_orflow')

    # Load design and platform config values.
    chip = parse_target_config.parse(chip, platform)

    # Set Chip object to use the loaded flow, pdk, lib.
    process = 'skywater130'
    stackup = '5M1LI'
    libname = 'sky130hd'
    libtype = 'unithd'
    chip.set('option', 'flow', 'orflow')
    chip.set('option', 'pdk', process)
    chip.set('asic', 'logiclib', libname)

    chip.set('asic', 'delaymodel', 'nldm')
    chip.set('asic', 'stackup', stackup)
    chip.set('asic', 'minlayer', "met1")
    chip.set('asic', 'maxlayer', "met5")
    chip.set('asic', 'maxfanout', 5) # TODO: fix this
    chip.set('asic', 'maxlength', 21000)
    chip.set('asic', 'maxslew', 1.5e-9)
    chip.set('asic', 'maxcap', .1532e-12)
    chip.set('asic', 'rclayer', 'clk', 'met5')
    chip.set('asic', 'rclayer', 'data', 'met3')
    chip.set('asic', 'hpinlayer', "met3")
    chip.set('asic', 'vpinlayer', "met2")
    chip.set('asic', 'density', 10)
    chip.set('asic', 'aspectratio', 1)
    chip.set('asic', 'coremargin', 62.56)
    corner = 'typical'
    chip.set('constraint', 'worst', 'libcorner', corner)
    chip.set('constraint', 'worst', 'pexcorner', corner)
    chip.set('constraint', 'worst', 'mode', 'func')
    chip.add('constraint', 'worst', 'check', ['setup','hold'])

    # Set default environment variables for the OpenROAD flow (sky130hd platform).
    platform_dir = os.path.join(openroad_dir, 'flow', 'platforms', 'sky130hd')
    job_dir = os.path.join(chip.get('option', 'builddir'),
                           chip.get('design'),
                           chip.get('option', 'jobname'))
    env_vars = {
        # Defaults
        'SCRIPTS_DIR': os.path.join(openroad_dir, 'flow', 'scripts'),
        'UTILS_DIR': os.path.join(openroad_dir, 'flow', 'util'),
        'PLATFORM_DIR': platform_dir,

        # Default values not set in platform config.mk
        'STREAM_SYSTEM_EXT': 'gds',
        'SYNTH_ARGS': '-flatten',
        'PLACE_PINS_ARGS': '',
        'GPL_ROUTABILITY_DRIVEN': '1',
        'GPL_TIMING_DRIVEN': '1',
        'GDS_LAYER_MAP': '',
        'ABC_AREA': '0',
        'NUM_CORES': f'{len(os.sched_getaffinity(0))}',

        # Project-specific
        'DESIGN_NAME': chip.get('design'),
        'VERILOG_FILES': ' '.join(chip.get('input', 'verilog')),
        'SDC_FILE': ' '.join(chip.get('input', 'sdc')),

        # Default location for generated files: job root directory. May be overridden later.
        'OBJECTS_DIR': os.path.abspath(job_dir),
        'REPORTS_DIR': os.path.abspath(job_dir),
        'RESULTS_DIR': os.path.abspath(job_dir),
        'SYNTH_STOP_MODULE_SCRIPT': os.path.join(job_dir, 'mark_hier_stop_modules.tcl'),
    }
    for step in chip.getkeys('flowgraph', 'orflow'):
        index = '0'
        for key, val in env_vars.items():
            tool = chip.get('flowgraph', 'orflow', step, index, 'tool')
            chip.set('tool', tool, 'env', step, index, key, val)

#########################
if __name__ == "__main__":
    chip = make_docs()
