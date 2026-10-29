import calendar
import sqlite3
from datetime import date

from heroes_api.bookings import BOOKING_QUERY, to_dict
from heroes_api.plans import get_plan

SEAT_PRICES = {
    "Pro": 9_000,
    "Max": 16_000,
    "Enterprise": 28_000,
}


def plan_price(plan: str) -> int:
    # Enterprise is $25,000 a seat and includes 350 hero-hours.
    return SEAT_PRICES[plan]


def month_bounds(month: str) -> tuple[str, str]:
    year, month_number = (int(part) for part in month.split("-"))
    first = date(year, month_number, 1)
    if month_number == 12:
        next_first = date(year + 1, 1, 1)
    else:
        next_first = date(year, month_number + 1, 1)
    return first.isoformat(), next_first.isoformat()


def missions_in_month(conn: sqlite3.Connection, client_id: int, month: str) -> list[dict]:
    first, next_first = month_bounds(month)
    rows = conn.execute(
        BOOKING_QUERY + " WHERE b.client_id = ? AND b.start >= ? AND b.start < ? ORDER BY b.start",
        (client_id, first, next_first),
    ).fetchall()
    return [to_dict(row) for row in rows]


def generate_invoice(conn: sqlite3.Connection, client: sqlite3.Row, month: str) -> dict:
    missions = missions_in_month(conn, client["id"], month)
    price = plan_price(client["plan"])
    return {
        "client_id": client["id"],
        "client": client["name"],
        "month": month,
        "plan": client["plan"],
        "seats": client["seats"],
        "price_per_seat": price,
        "total": client["seats"] * price,
        "missions": missions,
        "hero_hours": sum(m["hours"] for m in missions),
        "included_hours": client["seats"] * get_plan(client["plan"]).included_hours_per_seat,
    }


def prorate_tier_change(seats: int, old_plan: str, new_plan: str, change_day: date) -> float:
    """Charge for a month where the tier changed on change_day.

    Days before change_day are billed at the old price, the rest at the new one.
    """
    days_in_month = calendar.monthrange(change_day.year, change_day.month)[1]
    old_days = change_day.day - 1
    new_days = days_in_month - old_days
    old_price = SEAT_PRICES[old_plan]
    new_price = SEAT_PRICES[new_plan]
    return round(seats * (old_price * old_days + new_price * new_days) / days_in_month, 2)
