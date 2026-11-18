import sqlite3
from app import app, db, Enquiry

conn = sqlite3.connect("aps_enterprises.db")
conn.row_factory = sqlite3.Row
records = conn.execute("SELECT * FROM enquiries").fetchall()

with app.app_context():
    for row in records:
        exists = Enquiry.query.filter_by(
            name=row["name"],
            phone=row["phone"],
            message=row["message"]
        ).first()

        if not exists:
            item = Enquiry(
                name=row["name"],
                phone=row["phone"],
                email=row["email"],
                service=row["service"],
                message=row["message"]
            )
            db.session.add(item)

    db.session.commit()

conn.close()
print("Migration completed!")