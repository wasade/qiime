#!/usr/bin/env python
# File created on 09 Feb 2010
from __future__ import division

__author__ = "Rob Knight and Micah Hamady"
__copyright__ = "Copyright 2010, The QIIME project"
__credits__ =  ["Rob Knight", "Micah Hamady", "Greg Caporaso", "Kyle Bittinger","Jesse Stombaugh","William Walters", "Jens Reeder"] #remember to add yourself
__license__ = "GPL"
__status__ = "1.2.0-dev"
__maintainer__ = "William Walters"
__email__ = "william.a.walters@colorado.edu"
__status__ = "Development"
 

from qiime.util import parse_command_line_parameters, get_options_lookup
from optparse import make_option
from sys import stderr
from qiime.split_libraries import preprocess

#split_libraries.py
options_lookup = get_options_lookup()
script_info={}
script_info['brief_description']="""Split libraries according to barcodes specified in mapping file"""
script_info['script_description']="""Since newer sequencing technologies provide many reads per run (e.g. the 454 GS FLX Titanium series can produce 400-600 million base pairs with 400-500 base pair read lengths) researchers are now finding it useful to combine multiple samples into a single 454 run. This multiplexing is achieved through the application of a pyrosequencing-tailored nucleotide barcode design (described in (Parameswaran et al., 2007)). By assigning individual, unique sample specific barcodes, multiple sequencing runs may be performed in parallel and the resulting reads can later be binned according to sample. The script split_libraries.py performs this task, in addition to several quality filtering steps including user defined cut-offs for: sequence lengths; end-trimming; minimum quality score. To summarize, by using the fasta, mapping, and quality files, the program split_libraries.py will parse sequences that meet user defined quality thresholds and then rename each read with the appropriate Sample ID, thus formatting the sequence data for downstream analysis. If a combination of different sequencing technologies are used in any particular study, split_libraries.py can be used to perform the quality-filtering for each library individually and the output may then be combined.

Sequences from samples that are not found in the mapping file (no corresponding barcode) and sequences without the correct primer sequence will be excluded. Additional scripts can be used to exclude sequences that match a given reference sequence (e.g. the human genome; exclude_seqs_by_blast.py) and/or sequences that are flagged as chimeras (identify_chimeric_seqs.py).
"""
script_info['script_usage']=[]
script_info['script_usage'].append(("""Standard Example:""","""Using a single 454 run, which contains a single FASTA, QUAL, and mapping file while using default parameters and outputting the data into the Directory "Split_Library_Output":""","""split_libraries.py -m Mapping_File.txt -f 1.TCA.454Reads.fna -q 1.TCA.454Reads.qual -o Split_Library_Output/"""))
script_info['script_usage'].append(("""""","""For the case where there are multiple FASTA and QUAL files, the user can run the following command as long as there are not duplicate barcodes listed in the mapping file:""","""split_libraries.py -m Mapping_File.txt -f 1.TCA.454Reads.fna,2.TCA.454Reads.fna -q 1.TCA.454Reads.qual,2.TCA.454Reads.qual -o Split_Library_Output/"""))
script_info['script_usage'].append(("""Duplicate Barcode Example:""","""An example of this situation would be a study with 1200 samples. You wish to have 400 samples per run, so you split the analysis into three runs with and reuse barcoded primers (you only have 600). After initial analysis you determine a small subset is underrepresented (<500 sequences per samples) and you boost the number of sequences per sample for this subset by running a fourth run. Since the same sample IDs are in more than one run, it is likely that some sequences will be assigned the same unique identifier by split_libraries.py when it is run separately on the four different runs, each with their own barcode file. This will cause a problem in file concatenation of the four different runs into a single large file. To avoid this, you can use the '-s' parameter which defines a start index for split_libraries.py. From experience, most FLX runs (when combining both files for a single plate) will have 350,000 to 650,000 sequences. Thus, if Run 1 for split_libraries.py uses '-n 1000000', Run 2 uses '-n 2000000', etc., then you are guaranteed to have unique identifiers after concatenating the results of multiple FLX runs. With newer technologies you will just need to make sure that your start index spacing is greater than the potential number of sequences.

To run split_libraries.py, you will need two or more (depending on the number of times the barcodes were reused) separate mapping files (one for each Run, for example one Run1 and another one for Run2), then you can run split_libraries.py using the FASTA and mapping file for Run1 and FASTA and mapping file for Run2. Once you have independently run split libraries on each file independently, you can concatenate (cat) the sequence files generated. You can also concatenate the mapping files, since the barcodes are not necessary for downstream analyses, unless the same sample id's are found in multiple mapping files.

Run split_libraries.py on Run 1:""","""split_libraries.py -m Mapping_File.txt -f 1.TCA.454Reads.fna -q 1.TCA.454Reads.qual -o Split_Library_Run1_Output/ -n 1000000"""))
script_info['script_usage'].append(("""""","""Run split_libraries.py on Run 2:""","""split_libraries.py -m Mapping_File.txt -f 2.TCA.454Reads.fna -q 2.TCA.454Reads.qual -o Split_Library_Run2_Output/ -n 2000000"""))
script_info['script_usage'].append(("""""","""Concatenate the resulting FASTA files for use in downstream analyses:""","""cat Split_Library_Run1_Output/seqs.fna Split_Library_Run2_Output/seqs.fna > Combined_seqs.fna"""))
script_info['script_usage'].append(("""Suppress "Unassigned" Sequences Example:""","""Users may want to only output sequences which have been assigned to a particular sample. To suppress the outputting of "Unassigned sequences", the user can pass the "-r" option, without any additional values:""","""split_libraries.py -m Mapping_File.txt -f 1.TCA.454Reads.fna -q 1.TCA.454Reads.qual -o Split_Library_Output/ -r"""))
script_info['script_usage'].append(("""Barcode Decoding Example:""","""The standard barcode types supported by split_libraries.py are golay (Length: 12 NTs) and hamming (Length: 8 NTs). For situations where the barcodes are of a different length than golay and hamming, the user can define a generic barcode type "-b" as an integer, where the integer is the length of the barcode used in the study.

For the case where the hamming_8 barcodes were used, you can use the following command:""","""split_libraries.py -m Mapping_File.txt -f 1.TCA.454Reads.fna -q 1.TCA.454Reads.qual -o Split_Library_Output/ -b hamming_8"""))
script_info['script_usage'].append(("""""","""In the case where the barcodes used were different than the golay or hamming, one can define the length of barcode used (e.g. length of 6 NTs), as shown by the following command:""","""split_libraries.py -m Mapping_File.txt -f 1.TCA.454Reads.fna -q 1.TCA.454Reads.qual -o Split_Library_Output/ -b 6"""))
script_info['script_usage'].append(("""""","""Note: When analyzing large datasets (>100,000 seqs), users may want to use a generic barcode type, even for length 8 and 12 NTs, since the golay and hamming decoding processes can be computationally intensive, which causes the script to run slow. Barcode correction can be disabled with the -c option if desired.""",""""""))
script_info['script_usage'].append(("""Linkers and Primers:""","""The linker and primer sequence (or all the degenerate possibilities) are associated with each barcode from the mapping file. If a barcode cannot be identified, all the possible primers in the mapping file are tested to find a matching sequence. Using truncated forms of the same primer can lead to unexpected results for rare circumstances where the barcode cannot be identified and the sequence following the barcode matches multiple primers.""",""""""))
script_info['script_usage'].append(("""Reverse Primer Removal:""","""In many cases, sequence reads are long enough to sequence through the reverse primer and sequencing adapter.  To remove these primers and all following sequences, the -z option can be used.  By default, this option is set to 'disable'.  If it is set to 'truncate_only', split_libraries will trim the primer and any sequence following it if the primer is found.  If the 'truncate_remove' option is set, split_libraries.py will trim the primer if found, and will not write the sequence if the primer is not found. The allowed mismatches for the reverse primer shares the parameter value for the forward primer, -M (default 0).  To use reverse primer removal, one must include a 'ReversePrimer' column in the mapping file, with the reverse primer recorded in the 5' to 3' orientation.\nExample reverse primer removal, where primers are trimmed if found, and sequence is written unchanged if not found.  Mismatches are increased to 1 from the default 0:""","""split_libraries.py -m Mapping_File.txt -f 1.TCA.454Reads.fna -q 1.TCA.454Reads.qual -o Split_Library_Output/ -M 1 -z truncate_only"""))


script_info['output_description']="""Three files are generated by split_libraries.py:

1. .fna file (e.g. seqs.fna) - This is a FASTA file containing all sequences which meet the user-defined parameters, where each sequence identifier now contains its corresponding sample id from mapping file.

2. histograms.txt- This contains the counts of sequences with a particular length.

3. split_library_log.txt - This file contains a summary of the split_libraries.py analysis. Specifically, this file includes information regarding the number of sequences that pass quality control (number of seqs written) and how these are distributed across the different samples which, through the use of bar-coding technology, would have been pooled into a single 454 run. The number of sequences that pass quality control will depend on length restrictions, number of ambiguous bases, max homopolymer runs, barcode check, etc. All of these parameters are summarized in this file. If raw sequences do not meet the specified quality thresholds they will be omitted from downstream analysis. Since we never see a perfect 454 sequencing run, the number of sequences written should always be less than the number of raw sequences. The number of sequences that are retained for analysis will depend on the quality of the 454 run itself in addition to the default data filtering thresholds in the split_libraries.py script. The default parameters (minimum quality score = 25, minimum/maximum length = 200/1000, no ambiguous bases allowed, no mismatches allowed in primer sequence) can be adjusted to meet the user's needs.
"""
script_info['required_options']=[\
    make_option('-m', '--map', dest='map_fname', 
                help='name of mapping file. NOTE: Must contain a header'+\
                    ' line indicating SampleID in the first column and'+\
                    ' BarcodeSequence in the second,'+\
                    ' LinkerPrimerSequence in the third.'),
    make_option('-f', '--fasta', dest='fasta_fnames', 
                help='names of fasta files, comma-delimited')]
script_info['optional_options']=[\
    make_option('-q', '--qual', dest='qual_fnames', 
        help='names of qual files, comma-delimited [default: %default]'),

    make_option('-l', '--min-seq-length', dest='min_seq_len',
        type=int, default=200,
        help='minimum sequence length, in nucleotides [default: %default]'),

    make_option('-L', '--max-seq-length', dest='max_seq_len',
        type=int, default=1000,
        help='maximum sequence length, in nucleotides [default: %default]'),

    make_option('-t', '--trim-seq-length', dest='trim_seq_len',
        action='store_true',
        help='calculate sequence lengths after trimming primers and barcodes'+\
         ' [default: %default]', default=False),

    make_option('-s', '--min-qual-score', type=int, default=25,
        help='min average qual score allowed in read [default: %default]'),

    make_option('-k', '--keep-primer', action='store_true',
        help='do not remove primer from sequences', default=False),

    make_option('-B', '--keep-barcode', action='store_true',
        help='do not remove barcode from sequences', default=False),

    make_option('-a', '--max-ambig', type=int, default=0,
        help='maximum number of ambiguous bases [default: %default]'),

    make_option('-H', '--max-homopolymer', type=int, default=6,
        help='maximum length of homopolymer run [default: %default]'),

    make_option('-M', '--max-primer-mismatch', dest='max_primer_mm',
        type=int, default=0,
        help='maximum number of primer mismatches [default: %default]'),

    make_option('-b', '--barcode-type', default='golay_12', 
        help=\
        'barcode type, hamming_8, golay_12, variable_length (will '+\
        'disable any barcode correction if variable_length set), or a '+\
        'number representing the length of the barcode, such as -b 4. '+\
        ' [default: %default]'),

    make_option('-o', '--dir-prefix', default='.',
        help='directory prefix for output files [default: %default]'),

    make_option('-e', '--max-barcode-errors', dest='max_bc_errors',
        default=1.5, type=float,
        help='maximum number of errors in barcode [default: %default]'),

    make_option('-n', '--start-numbering-at', dest='start_index',
        default=1, type=int,
        help='seq id to use for the first sequence [default: %default]'),

    make_option('-r', '--remove_unassigned', default=False,
        action='store_true', help='remove sequences which are Unassigned from \
            output [default: %default]'),

    make_option('-c', '--disable_bc_correction', default=False,
        action='store_true', help='Disable attempts to find nearest '+\
        'corrected barcode.  Can improve performance. [default: %default]'),

    make_option('-w', '--qual_score_window', dest="qual_score_window",
                type=int, default=0,
        action='store', help='Enable sliding window test of quality '+\
        'scores.  If the average score of a continuous set of w nucleotides '+\
        'falls below the threshold (see -s for default), the sequence is '+\
        'discarded. A good value would be 50. 0 (zero) means no filtering. '+\
        'Must pass a .qual file (see -q parameter) if this '+\
        'functionality is enabled. [default: %default]'),
        
    make_option('-p', '--disable_primers', default=False,
        action='store_true', help='Disable primer usage when demultiplexing.'+\
        '  Should be enabled for unusual circumstances, such as analyzing '+\
        'Sanger sequence data generated with different primers. '+\
        ' [default: %default]'),
        
    make_option('-z', '--reverse_primers', default="disable", type=str, 
        action='store', help='Enable removal of the reverse primer and '+\
        'any subsequence sequence from the end of each read.  To enable '+\
        'this, there has to be a "ReversePrimer" column in the mapping file. '+\
        "Primers a required to be in IUPAC format and written in the 5' to "+\
        " 3' direction.  Valid options are 'disable', 'truncate_only', "+\
        "and 'truncate_remove'.  'truncate_only' will remove the primer "+\
        "and subsequence sequence data from the output read and will not "+\
        "alter output of sequences where the primer cannot be found. "+\
        "'truncate_remove' will flag sequences where the primer cannot "+\
        "be found to not be written and will record the quantity of such "+\
        "failed sequences in the log file. [default: %default]"),
        
    make_option('-d', '--record_qual_scores', default=False,
        action='store_true', help='Enables recording of quality scores for '+\
        'all sequences that are recorded.  If this option is enabled, a file '+\
        'named seqs_filtered.qual will be created in the output directory, '+\
        'and will contain the same sequence IDs in the seqs.fna file and '+\
        'sequence quality scores matching the bases present in the seqs.fna '+\
        'file. [default: %default]')]

script_info['version'] = __version__


def main():
    option_parser, opts, args = parse_command_line_parameters(**script_info)
    
    if opts.qual_score_window and not opts.qual_fnames:
        option_parser.error('To enable sliding window quality test (-w), '+\
        '.qual files must be included.')
  
    mapping_file = opts.map_fname
    fasta_files = set(opts.fasta_fnames.split(','))
    if opts.qual_fnames:
        qual_files = set(opts.qual_fnames.split(','))
    else:
        qual_files = set()

    for q in qual_files:
        if not q.endswith('qual'):
            stderr.write(
            "Qual file does not end with .qual: is it really a qual file?\n%s\n" 
            % q)

    for f in fasta_files:
        if not (f.endswith('fasta') or f.endswith('fna')):
            stderr.write(
            "Fasta file does not end with .fna: is it really a seq file?\n%s\n" 
            % f)
    
    preprocess(fasta_files, qual_files, mapping_file,
               barcode_type=opts.barcode_type,
               starting_ix = opts.start_index,
               min_seq_len = opts.min_seq_len,
               max_seq_len = opts.max_seq_len, 
               min_qual_score=opts.min_qual_score,
               keep_barcode=opts.keep_barcode,
               keep_primer=opts.keep_primer,
               max_ambig=opts.max_ambig,
               max_primer_mm=opts.max_primer_mm,
               trim_seq_len=opts.trim_seq_len,
               dir_prefix=opts.dir_prefix,
               max_bc_errors = opts.max_bc_errors,
               max_homopolymer = opts.max_homopolymer,
               remove_unassigned = opts.remove_unassigned,
               attempt_bc_correction = not opts.disable_bc_correction,
               qual_score_window = opts.qual_score_window,
               disable_primers = opts.disable_primers,
               reverse_primers = opts.reverse_primers,
               record_qual_scores = opts.record_qual_scores)
 
if __name__ == "__main__":
    main()
