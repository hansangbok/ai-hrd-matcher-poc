
#!/usr/bin/env python3
import csv
import json
import os
from datetime import datetime

# 입력 CSV 경로
INPUT_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'rfps.csv')
# 출력 JSON 경로
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'mapped')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_int(value):
    try:
        return int(value)
    except:
        return None

def parse_schedule(value):
    """
    '2025-08-10~2025-08-11' 또는 '2025-05-21,2025-06-11' 형식을
    스키마의 period/dates 로 변환
    """
    # 기간 구분자 '~' 또는 '/'
    if '~' in value or '/' in value:
        # 슬래시로 통일
        period = value.replace('~', '/').split()[0]
        return {"type": "period", "period": period}
    else:
        dates = [d.strip() for d in value.split(',')]
        return {"type": "dates", "dates": dates}

def map_row_to_schema(row):
    """
    CSV 한 행(row: dict)을 스키마에 맞춘 JSON 객체로 매핑
    필드명은 CSV 헤더에 맞춰 조정하세요.
    """
    return {
        "company": row.get("Company/Organization", "").strip(),
        "request_date": row.get("Request Date", "").strip(),
        "request_type": row.get("Request Type", "").strip(),
        "course_name": row.get("Course Name", "").strip(),
        "topics": [t.strip() for t in row.get("Education Topic(s)", "").split(",") if t.strip()],
        "description": row.get("Free Form Description", "").strip(),
        "target": {
            "level": row.get("Target Level", "").strip(),
            "size": parse_int(row.get("Target Audience Size", "")) or 0
        },
        "learning_objectives": [row.get("Learning Objectives", "").strip()],
        "scope_of_work": [row.get("Scope of Work", "").strip()],
        "curriculum_items": [
            {
                "title": item.split("|")[0].strip(),
                "duration_hours": parse_int(item.split("|")[1].strip()) or 0
            }
            for item in row.get("Detailed Curriculum Items", "").split(";")
            if "|" in item
        ],
        "delivery_mode": row.get("Delivery Mode", "").strip().lower(),
        "location": row.get("Location", "").strip(),
        "schedule": parse_schedule(row.get("Schedule Details", "")),
        "budget": {
            "amount": parse_int(row.get("Budget (KRW)", "")),
            "currency": "KRW"
        },
        "instructor_requirements": [row.get("Instructor Requirements", "").strip()],
        "materials": [row.get("Materials / Equipment", "").strip()],
        "assessments": [row.get("Assessment / Tasks", "").strip()],
        "quality_sla": [row.get("Quality / SLA", "").strip()],
        "success_metrics": [row.get("Success Metrics", "").strip()],
        "submission_deadline": row.get("Submission Deadline", "").strip().replace(" ", "T"),
        "contacts": {
            "requester": {
                "name": row.get("Contact Person", "").strip(),
                "email": row.get("Contact Email/Phone", "").split("/")[0].strip(),
                "phone": row.get("Contact Email/Phone", "").split("/")[-1].strip()
            },
            "purchasing": {
                "name": row.get("Purchasing Person", "").strip(),
                "email": row.get("Purchasing Contact Info", "").split("/")[0].strip(),
                "phone": row.get("Purchasing Contact Info", "").split("/")[-1].strip()
            }
        }
    }

def main():
    with open(INPUT_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            mapped = map_row_to_schema(row)
            out_path = os.path.join(OUTPUT_DIR, f"rfp_{idx:02d}.json")
            with open(out_path, 'w', encoding='utf-8') as wf:
                json.dump(mapped, wf, ensure_ascii=False, indent=2)
            print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
