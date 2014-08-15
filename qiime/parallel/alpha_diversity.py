#!/usr/bin/env python
# File created on 13 Jul 2012
from __future__ import division

__author__ = "Greg Caporaso"
__copyright__ = "Copyright 2011, The QIIME project"
__credits__ = ["Greg Caporaso", "Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "1.8.0-dev"
__maintainer__ = "Greg Caporaso"
__email__ = "gregcaporaso@gmail.com"

from os.path import join, abspath, exists, basename
from os import makedirs

from qiime.parallel.wrapper import ParallelWrapper
from qiime.workflow.util import WorkflowLogger


class ParallelAlphaDiversity(ParallelWrapper):
    def _construct_job_graph(self, input_fps, output_dir, params):
        """Creates the job workflow graph to execute alpha_diversity.py over
        a list of input files.

        Parameters
        ----------
        input_fps : list of str
            List of paths to the input biom tables
        output_dir : str
            Path to the output directory. It will be created if it does not
            exists
        params : dict
            Parameters to use when calling alpha_diversity.py, in the form of
            {param_name: value}
        """
        # Do the parameter parsing
        tree_str = '-t %s' % params['tree_path'] if params['tree_path'] else ''
        metrics = params['metrics']
        output_dir = abspath(output_dir)

        # Create the output directory
        if not exists(output_dir):
            makedirs(output_dir)

        # Create the log file
        self._logger = WorkflowLogger()

        for i, input_fp in enumerate(input_fps):
            input_fn = basename(input_fp)
            output_fn = '%d_alpha_%s' % (i, input_fn)
            output_fn = output_fn.replace('.biom', '.txt')
            output_fp = join(output_dir, output_fn)
            cmd = ("alpha_diversity.py -i %s -o %s %s -m %s"
                   % (input_fp, output_fp, tree_str, metrics))
            self._job_graph.add_node("%d" % i, job=(cmd, ),
                                     requires_deps=False)
