import json
import frappe


def create_task_period(doc, method=None):

    matrix_text = doc.custom_matrix_data or ""

    try:
        data = json.loads(matrix_text)
    except Exception as e:
        frappe.log_error(str(e), "TASK JSON ERROR")
        return

    for cluster_name, cluster in data.items():

        for row in cluster.get("data", []):

            stage = row.get("row")

            if not stage or stage.upper() == "TOTAL":
                continue

            percent = float(row.get("_percent") or 0)
            if percent <= 0:
                continue

            for mep_row in doc.custom_mep_:

                mep = mep_row.mep
                rate = row.get(mep, 0)

                task_name = f"{cluster_name} | {stage} | {mep}"

                department = frappe.db.get_value("MEP", mep, "department") or ""

                # check existing row
                existing = None
                for d in doc.custom_task_period:
                    if d.task_name == task_name:
                        existing = d
                        break

                if existing:
                    existing.percent = percent
                    existing.rate = rate
                    existing.department = department
                else:
                    doc.append("custom_task_period", {
                        "task_name": task_name,
                        "period": "0",
                        "percent": percent,
                        "rate": rate,
                        "department": department
                    })

import frappe
from frappe.utils import cint


def fetch_sales_order_data_to_project(doc, method=None):

    if not doc.sales_order:
        return

    so = frappe.get_doc("Sales Order", doc.sales_order)

    # =========================
    # Copy matrix fields
    # =========================
    doc.custom_matrix_data = so.get("custom_matrix_data")

    # only if field exists
    if hasattr(so, "custom_matrix_html"):
        doc.custom_matrix_html = so.get("custom_matrix_html")

    # =========================
    # Copy MEP table
    # =========================
    doc.set("custom_mep_", [])

    for row in so.get("custom_mep_") or []:
        doc.append("custom_mep_", {
            "mep": row.mep
        })

    # =========================
    # Copy Task Period
    # -> custom_progress
    # =========================
    doc.set("custom_progress", [])

    for row in so.get("custom_task_period") or []:

        doc.append("custom_progress", {
            "task_name": row.task_name,
            "period": cint(row.period or 0),
            "department": row.department,
            "percent": row.percent,
            "rate": row.rate,
            "weight": 0,
            "progress": 0,
            "status": 0
        })