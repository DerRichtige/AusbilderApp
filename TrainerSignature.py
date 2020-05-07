"""Converter to create a PDF from the passed arguments

This script takes the passed arguments to fill at specific places a TEX file.
And this TEX file will be converted into a PDF file by using pdflatex.
"""

import os
import string
import subprocess
import datetime


def main():
    project_path = os.path.curdir
    trainer_signature = os.path.join(project_path,
                                     'signature',
                                     'signature.png')
    in_filenames = \
        [os.path.join(project_path,
                      'Template',
                      txt_file) for txt_file in ['packages.txt',
                                                 'commands.txt',
                                                 'content.txt']]

    build_path = os.path.join(project_path, 'Template')
    out_filename = os.path.join(build_path, 'trainer_signature')
    packages, commands, content = '', '', ''
    in_files_content = []
    for idx in range(len(in_filenames)):
        with open(in_filenames[idx], 'r') as f:
            in_files_content.append(f.read())
    packages, commands, content = in_files_content
    LATEX_TEMPLATE = string.Template(
        rf'''
        \documentclass[ngerman, a4paper]{{scrreprt}}
        {packages}
        {commands}
        \begin{{document}}
        {content}
        \end{{document}}
        '''
        )
    latex = LATEX_TEMPLATE.safe_substitute(
        sigDateTrainer=datetime.datetime.today().strftime('%d.%m.%Y'),
        signatureTrainer=trainer_signature
    )

    os.makedirs(build_path, exist_ok=True)
    with open(out_filename + '.tex', 'w') as out_file:
        out_file.write(latex)

    subprocess.run(['pdflatex', '-output-directory', build_path, out_filename],
                   stdout=open(os.devnull, 'wb'))


if __name__ == '__main__':
    main()
