import json
import frappe


def create_task_period(doc, method=None):

    matrix_text = doc.custom_matrix_data or ""

    # clear old rows
    doc.custom_task_period = []

    # parse json safely
    try:
        data = json.loads(matrix_text)
    except Exception as e:
        frappe.log_error(
            f"INVALID JSON: {str(e)}",
            "TASK PERIOD ERROR"
        )
        return

    # loop clusters
    for cluster_name, cluster in data.items():

        rows = cluster.get("data", [])

        for row in rows:

            stage = row.get("row")
            percent = row.get("_percent", 0)

            # skip invalid rows
            if not stage:
                continue

            # skip TOTAL row
            if str(stage).upper() == "TOTAL":
                continue

            # skip zero %
            if float(percent or 0) <= 0:
                continue

            # loop MEPs
            for mep_row in doc.custom_mep_:

                mep = mep_row.mep

                # get rate from json row
                rate = row.get(mep, 0)

                # department
                department = frappe.db.get_value(
                    "MEP",
                    mep,
                    "department"
                ) or ""

                # task name
                task_name = f"{cluster_name} | {stage} | {mep}"

                # avoid duplicates
                exists = False

                for d in doc.custom_task_period:
                    if d.task_name == task_name:
                        exists = True
                        d.percent = percent
                        d.rate = rate
                        d.department = department
                        break

                # create row
                if not exists:

                    r = doc.append("custom_task_period", {})

                    r.task_name = task_name
                    r.period = "0"
                    r.percent = percent
                    r.rate = rate
                    r.department = department

                # debug log
                frappe.logger().info(
                    f"TASK CREATED: {task_name}"
                )