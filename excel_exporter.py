import pandas as pd
from datetime import datetime


def export_results(results, destination, priority):

    # تنظيف الاسم لاستخدامه كاسم ملف
    clean_destination = destination.replace(" ", "_")

    clean_priority = priority.replace(" ", "_")

    # إضافة وقت الاستخراج حتى لا يتم استبدال الملفات القديمة
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = (
        f"Logistics_Routes_{clean_destination}_"
        f"{clean_priority}_{timestamp}.xlsx"
    )

    results.to_excel(
        filename,
        index=False
    )

    return filename