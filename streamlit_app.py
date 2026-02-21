import os
import io
import tempfile
from datetime import datetime, timedelta
from contextlib import redirect_stdout

import streamlit as st
from setbp1_literature_search import SETBPLiteratureSearch

st.set_page_config(
    page_title="SETBP1 Literature Search",
    layout="centered",
)


def run_search(start_date_str: str, end_date_str: str) -> dict:
    """Run the literature search and return results with file bytes."""
    output_dir = tempfile.mkdtemp(prefix="setbp1_search_")
    searcher = SETBPLiteratureSearch(start_date_str, end_date_str, output_dir)

    stdout_buffer = io.StringIO()
    with redirect_stdout(stdout_buffer):
        searcher.run()

    captured_output = stdout_buffer.getvalue()

    end_date_formatted = end_date_str.replace("-", "")
    excel_path = os.path.join(output_dir, f"{end_date_formatted}-SETBP1-Literature-Data.xlsx")
    pdf_path = os.path.join(output_dir, f"{end_date_formatted}-SETBP1-Literature-Summary.pdf")

    # Read file bytes into memory so they survive across Streamlit reruns
    excel_bytes = None
    excel_name = None
    if os.path.exists(excel_path):
        with open(excel_path, "rb") as f:
            excel_bytes = f.read()
        excel_name = os.path.basename(excel_path)

    pdf_bytes = None
    pdf_name = None
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        pdf_name = os.path.basename(pdf_path)

    categories = searcher.categorize_papers(searcher.all_papers)
    category_counts = {k: len(v) for k, v in categories.items()}

    pubmed_count = sum(1 for p in searcher.all_papers if p.get("source") == "PubMed")
    biorxiv_count = sum(1 for p in searcher.all_papers if p.get("source") == "biorxiv")
    medrxiv_count = sum(1 for p in searcher.all_papers if p.get("source") == "medrxiv")

    return {
        "excel_bytes": excel_bytes,
        "excel_name": excel_name,
        "pdf_bytes": pdf_bytes,
        "pdf_name": pdf_name,
        "total_papers": len(searcher.all_papers),
        "paper_counts": {
            "PubMed": pubmed_count,
            "bioRxiv": biorxiv_count,
            "medRxiv": medrxiv_count,
        },
        "categories": category_counts,
        "stdout_log": captured_output,
    }


# --- UI ---

st.title("SETBP1 Literature Search")
st.markdown(
    "Search PubMed, bioRxiv, and medRxiv for **SETBP1** and "
    "**Schinzel-Giedion Syndrome** papers. Generate Excel and PDF reports."
)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", value=datetime.now().date() - timedelta(days=7))
with col2:
    end_date = st.date_input("End date", value=datetime.now().date())

date_valid = start_date <= end_date
if not date_valid:
    st.error("Start date must be before or equal to end date.")

search_clicked = st.button("Search", type="primary", disabled=not date_valid)

if search_clicked:
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    with st.status("Searching databases...", expanded=True) as status:
        st.write("Querying PubMed, bioRxiv, and medRxiv...")
        results = run_search(start_str, end_str)
        status.update(label="Search complete!", state="complete", expanded=False)

    st.session_state["results"] = results

if "results" in st.session_state:
    results = st.session_state["results"]

    st.divider()
    st.subheader("Results")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Papers", results["total_papers"])
    m2.metric("PubMed", results["paper_counts"]["PubMed"])
    m3.metric("bioRxiv", results["paper_counts"]["bioRxiv"])
    m4.metric("medRxiv", results["paper_counts"]["medRxiv"])

    st.markdown("**Papers by category:**")
    cat = results["categories"]
    cat_cols = st.columns(len(cat))
    for i, (name, count) in enumerate(cat.items()):
        label = "New Data Sets" if name == "dataset" else name.capitalize()
        cat_cols[i].metric(label, count)

    st.subheader("Download Reports")
    dl_col1, dl_col2 = st.columns(2)

    if results["excel_bytes"]:
        dl_col1.download_button(
            label="Download Excel Report",
            data=results["excel_bytes"],
            file_name=results["excel_name"],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        dl_col1.info("No Excel report (no papers found).")

    if results["pdf_bytes"]:
        dl_col2.download_button(
            label="Download PDF Report",
            data=results["pdf_bytes"],
            file_name=results["pdf_name"],
            mime="application/pdf",
        )
    else:
        dl_col2.info("No PDF report (no papers found).")

    with st.expander("Search log"):
        st.code(results["stdout_log"], language=None)
