#!/usr/bin/env python
# File created on 09 Feb 2010
from __future__ import division

__author__ = "Justin Kuczynski"
__copyright__ = "Copyright 2010, The QIIME project"
__credits__ = ["Justin Kuczynski"]
__license__ = "GPL"
__status__ = "1.2.0-dev"
__maintainer__ = "Justin Kuczynski"
__email__ = "justinak@gmail.com"
__status__ = "Development"
 

from qiime.util import parse_command_line_parameters, create_dir
from qiime.tree_compare import load_tree_files, bootstrap_support, write_bootstrap_support_files
from optparse import make_option
import os.path
from os.path import exists

script_info={}
script_info['brief_description']="""Compare jackknifed/bootstrapped trees"""
script_info['script_description']="""Compares jackknifed/bootstrapped trees (support trees) with a master tree constructed typically from the entire dataset (e.g: a resulting file from upgma_cluster.py) and outputs support for nodes.

if support trees do not have all tips that master has (e.g. because samples with few sequences were dropped during a jackknifing analysis), the output master tree will have only those tips included in all support trees

if support trees have tips that the master tree does not, those tips will be ignored (removed from the support tree during analysis)"""
script_info['script_usage']=[]
script_info['script_usage'].append(("""Example:""","""Given the sample upgma tree generated by the user for the entire dataset, the directory of jackknife supported trees (e.g.: the resulting directory from upgma_cluster.py) and the directory to write the results for the tree comparisons, the following command compares the support trees with the master:""","""tree_compare.py -m sample_clustering.tre -s jackknife_upgma_trees/ -o jackknife_comparison/"""))
script_info['script_usage'].append(("""""","""Additionally, tree_compare.py can be used to compare any set of support trees to a master tree, making it easily expandable to additional algorithms.""",""""""))
script_info['output_description']="""The result of tree_compare.py contains the master tree, now with internal nodes uniquely named, a separate bootstrap/jackknife support file, listing the support for each internal node, and a jackknife_named_nodes.tre tree, where internal nodes are named with their support values from 0 to 1.0, for use with tree visualization software (e.g. FigTree)."""
script_info['required_options']=[\
make_option('-m', '--master_tree', help='master tree filepath'),\
make_option('-s', '--support_dir', help='path to dir containing support trees'),\
make_option('-o', '--output_dir', help='output directory, writes three files here '+\
"makes dir if it doesn't exist")
]
script_info['optional_options']=[]
script_info['version'] = __version__


def main():
    option_parser, options, args = parse_command_line_parameters(**script_info)

    create_dir(options.output_dir, fail_on_exist=False)

    master_tree, support_trees = load_tree_files(options.master_tree,
        options.support_dir)
    # get support of each node in master
    new_master, bootstraps = bootstrap_support(master_tree, support_trees)

    write_bootstrap_support_files(new_master, bootstraps, options.output_dir,
    len(support_trees))

if __name__ == "__main__":
    main()
