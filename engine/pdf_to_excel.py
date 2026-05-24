"""PDF to Excel conversion using tabula-py and camelot-py."""

import os


def convert(input_path: str, output_path: str, report_fn) -> str:
    report_fn(10, "Analyzing PDF for tables...")

    tables_found = False

    # Try camelot first (better accuracy for bordered tables)
    try:
        import camelot
        report_fn(15, "Trying camelot for table extraction...")
        tables = camelot.read_pdf(input_path, pages="all", flavor="lattice")
        if len(tables) > 0:
            report_fn(30, f"Camelot found {len(tables)} tables")
            # Export to Excel
            writer = None
            try:
                import openpyxl
                writer = openpyxl.Workbook()
                ws = writer.active
                ws.title = "Tables"

                for i, table in enumerate(tables):
                    df = table.df
                    pct = 30 + int(50 * (i + 1) / len(tables))
                    report_fn(pct, f"Processing table {i+1}/{len(tables)}...")
                    # Write each table to a sheet
                    if i == 0:
                        for r_idx, row in df.iterrows():
                            for c_idx, val in enumerate(row):
                                ws.cell(row=r_idx+1, column=c_idx+1, value=val)
                    else:
                        ws2 = writer.create_sheet(f"Table_{i+1}")
                        for r_idx, row in df.iterrows():
                            for c_idx, val in enumerate(row):
                                ws2.cell(row=r_idx+1, column=c_idx+1, value=val)

                writer.save(output_path)
                tables_found = True
            except ImportError:
                pass
    except (ImportError, Exception):
        pass

    # Fallback to tabula-py
    if not tables_found:
        try:
            import tabula
            report_fn(20, "Using tabula for table extraction...")
            dfs = tabula.read_pdf(input_path, pages="all", multiple_tables=True)

            if dfs and len(dfs) > 0:
                report_fn(40, f"Tabula found {len(dfs)} tables")
                import openpyxl
                writer = openpyxl.Workbook()
                ws = writer.active
                ws.title = "Tables"

                for i, df in enumerate(dfs):
                    pct = 40 + int(50 * (i + 1) / len(dfs))
                    report_fn(pct, f"Processing table {i+1}/{len(dfs)}...")
                    if i == 0:
                        for r_idx, row in df.iterrows():
                            for c_idx, val in enumerate(row):
                                ws.cell(row=r_idx+1, column=c_idx+1, value=val)
                    else:
                        ws2 = writer.create_sheet(f"Table_{i+1}")
                        for r_idx, row in df.iterrows():
                            for c_idx, val in enumerate(row):
                                ws2.cell(row=r_idx+1, column=c_idx+1, value=val)

                writer.save(output_path)
                tables_found = True
        except (ImportError, Exception):
            pass

    if not tables_found:
        # No tables found, create a minimal file with a note
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "No Tables"
            ws.cell(row=1, column=1, value="No tables detected in this PDF.")
            ws.cell(row=2, column=1, value="Try converting to TXT or Word instead.")
            wb.save(output_path)
        except ImportError:
            raise RuntimeError("No tables found and openpyxl not available")

    if os.path.exists(output_path):
        return os.path.abspath(output_path)
    raise RuntimeError("Excel conversion failed")
