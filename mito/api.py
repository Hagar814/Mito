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