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
    # MAIN FIELDS
    # =========================
    doc.customer = so.customer
    doc.company = so.company
    doc.custom_matrix_data = so.custom_matrix_data

    # =========================
    # MEP TABLE
    # =========================
    doc.custom_mep_ = []

    for mep in so.custom_mep_:
        doc.append("custom_mep_", {
            "mep": mep.mep
        })

    # =========================
    # PROGRESS TABLE
    # =========================
    doc.custom_progress = []

    for row in so.custom_task_period:

        doc.append("custom_progress", {
            "task_name": row.task_name,
            "department": row.department,
            "percent": row.percent,
            "rate": row.rate,
            "period": row.period
        })