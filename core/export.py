import os

import csv
from typing import Dict, Any

def export_result_csv(container: Dict[str, Any], outpath: str):
    winners = container["draw"].get("winners")
    if not winners:
        raise ValueError("Нет победителей для экспорта!")

    fieldnames = ["position", "id", "name"]
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    with open(outpath, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, w in enumerate(winners, 1):
            writer.writerow({
                "position": i,
                "id": w["id"],
                "name": w["name"]
            })

def export_result_pdf(container: Dict[str, Any], outpath: str):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        raise RuntimeError("reportlab not installed")

    c = canvas.Canvas(outpath, pagesize=A4)
    w, h = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, h - 40, f"Результаты розыгрыша (id: {container['id']})")
    c.setFont("Helvetica", 10)

    y = h - 80
    for i, p in enumerate(container["draw"]["shuffled"], 1):
        if y < 60:
            c.showPage()
            y = h - 40
        c.drawString(40, y, f"{i}. {p['id']} — {p['name']}")
        y -= 16

    c.save()
