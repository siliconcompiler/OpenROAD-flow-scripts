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

####################################################
# PDK and Flow Setup
####################################################
def setup(chip):
    # Collect basic values.
    design = chip.get('design')
    platform = 'asap7'

    # Set the target name.
    chip.set('option', 'target', 'asap7_orflow')

    # Load PDK, flow, and libs.
    chip.load_pdk('asap7_orflow')
    chip.load_flow('orflow')
    chip.load_lib('asap7sc7p5t_orflow')

    # Load design and platform config values.
    chip = parse_target_config.parse(chip, platform)

    # Set Chip object to use the loaded flow, pdk, lib.
    process = 'asap7'
    stackup = '10M'
    libtype = '7p5t'
    group = 'asap7sc7p5t'
    libname = f'{group}_rvt'
    chip.set('option', 'flow', 'orflow')
    chip.set('option', 'pdk', process)
    chip.set('asic', 'logiclib', libname)

    # Set project-specific values
    chip.set('asic', 'delaymodel', 'nldm')
    chip.set('asic', 'stackup', stackup)
    chip.set('asic', 'minlayer', "M2")
    chip.set('asic', 'maxlayer', "M7")
    chip.set('asic', 'maxfanout', 64)
    chip.set('asic', 'maxlength', 1000)
    chip.set('asic', 'maxslew', 0.2e-9)
    chip.set('asic', 'maxcap', 0.2e-12)
    chip.set('asic', 'rclayer', 'clk', "M5")
    chip.set('asic', 'rclayer', 'data',"M3")
    chip.set('asic', 'hpinlayer', "M4")
    chip.set('asic', 'vpinlayer', "M5")
    chip.set('asic', 'density', 10)
    chip.set('asic', 'aspectratio', 1)
    chip.set('asic', 'coremargin', 0.270)
    # Set timing corners.
    corner = 'BC'
    chip.set('constraint','worst','libcorner', corner)
    chip.set('constraint','worst','pexcorner', corner)
    chip.set('constraint','worst','mode', 'func')
    chip.set('constraint','worst','check', ['setup','hold'])

    # Set default environment variables for the OpenROAD flow (asap7 platform).
    platform_dir = os.path.join(openroad_dir, 'flow', 'platforms', 'asap7')
    job_dir = os.path.join(chip.get('option', 'builddir'),
                           chip.get('design'),
                           chip.get('option', 'jobname'))
    env_vars = {
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

    corners = {
        'BC': 'FF',
        'WC': 'SS',
        'TC': 'TT',
    }
    post = 'nldm_201020.lib'
    for corner, abrv in corners.items():
        env_vars[f'{corner}_LIB_FILES'] = ' '.join(chip.get('library', libname, 'model', 'timing', 'nldm', corner))
        env_vars[f'{corner}_DONT_USE_LIBS'] = ' '.join(chip.get('library', libname, 'model', 'timing', 'nldm', corner))

    # Set default environment variables for every step in the flow.
    for step in chip.getkeys('flowgraph', 'orflow'):
        index = '0'
        for key, val in env_vars.items():
            tool = chip.get('flowgraph', 'orflow', step, index, 'tool')
            chip.set('tool', tool, 'env', step, index, key, val)


#########################
if __name__ == "__main__":
    chip = make_docs()
