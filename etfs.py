"""
Summary.

Retrieve the companies infos from ETF's website.
"""
# -*- coding: utf-8 -*-

import os
import pandas as pd
import tabula


# # Commom functions.
def extract_pdf_tables(folder):
    """
    Summary.

    Extract tables from a pdf file.
    folder: Folder.
    """
    ftables = []
    for filename in os.listdir(folder):
        if filename.endswith(".pdf"):
            filepath = os.path.join(folder, filename)  # Path.
            pdf_tables = tabula.read_pdf(filepath, pages="all",
                                         multiple_tables=True)
            ftables.extend(pdf_tables)

    return ftables


FOLDER = "../FONTES/INVESTIMENTOS/ETFS"
tables = extract_pdf_tables(folder=FOLDER)
df = [pd.DataFrame(table) for table in tables]
df = pd.concat(df, ignore_index=True)
# df.to_excel("../OUTPUT/ETFS_ETFS.xlsx", index=False)
