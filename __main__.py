"""
Provides a command line interface to access the summarizer library for data files.

"""

import argparse
import os
import pathlib
from datafilesummarizer.renderers.JinjaRenderer import JinjaRenderer
from datafilesummarizer.Summarizer import Summarizer


def _parse_args() -> argparse.Namespace:
    """
    Parse input arguments.

    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('datafile',
                        help="The data file to read. Expects a path to a readable data file.",
                        type=pathlib.Path
                        )
    parser.add_argument("-d", "--delimiter",
                        help="Define the character(s) which delimit the file. Defaults to ','.",
                        default=','
                        )
    parser.add_argument("-t", "--filetype",
                        help="The Pandas file type to parse the dataFile with. Defaults to 'csv'.",
                        choices=['csv'],
                        default='csv'
                        )
    parser.add_argument("-o", "--output-type",
                        help="Type of output desired. Defaults to HTML content returned as stdout.",
                        choices=['file', 'stdout'],
                        default='file'
                        )

    return parser.parse_args()


def _get_output_file_name(input_file_path: pathlib.Path):
    parent = input_file_path.parent
    filename_base = input_file_path.stem

    output = parent.joinpath(filename_base + '-summary').with_suffix('.html')

    return output


args = vars(_parse_args())

output_type = args.pop('output_type')

summarizer = Summarizer(**args)

summary = summarizer.get_summary()

if output_type == 'file':
    outfile_name = _get_output_file_name(args['datafile'])
    with open(outfile_name, 'w') as outfile:
        outfile.write(JinjaRenderer.render(summary))

    print(f"Output written to {outfile_name}")
    os.system(f"open {outfile_name}")
else:
    print(summary)