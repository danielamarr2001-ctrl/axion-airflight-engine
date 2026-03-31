"""Seed script for AXIOM demo database.
Run: python -m axiom.db.seed
Drops all tables and recreates with fresh demo data.
"""

import random
import string
from datetime import date, datetime, timedelta

from axiom.db.engine import Base, SessionLocal, engine
from axiom.db.models import Decision, Flight, Passenger, Reservation, Rule, SSRRecord, Segment

# ---------------------------------------------------------------------------
# Reference data – real IATA codes and realistic airline routes
# ---------------------------------------------------------------------------

AIRPORTS = [
    "BOG", "MDE", "CLO", "CTG", "MIA", "MAD", "GRU", "SCL",
    "LIM", "PTY", "JFK", "FLL", "CUN", "MEX", "EZE",
]

AIRLINES = {
    "AV": "Avianca",
    "LA": "LATAM",
    "IB": "Iberia",
    "AA": "American Airlines",
    "CM": "Copa",
    "B6": "JetBlue",
    "DL": "Delta",
}

ROUTES = [
    ("AV", "BOG", "MDE"),
    ("AV", "BOG", "CTG"),
    ("AV", "BOG", "MIA"),
    ("AV", "BOG", "MAD"),
    ("AV", "BOG", "CLO"),
    ("LA", "BOG", "LIM"),
    ("LA", "SCL", "GRU"),
    ("LA", "LIM", "MIA"),
    ("IB", "MAD", "BOG"),
    ("IB", "MAD", "MIA"),
    ("CM", "PTY", "BOG"),
    ("CM", "PTY", "MDE"),
    ("AA", "MIA", "BOG"),
    ("AA", "JFK", "BOG"),
]

AIRCRAFT_TYPES = ["A320", "A319", "B738", "B787", "A330", "E190"]
FARE_CLASSES = ["Y", "B", "M", "H", "Q"]
DEPARTURE_TIMES = ["06:00", "07:15", "08:30", "10:00", "10:30", "12:00",
                   "14:00", "14:20", "16:30", "18:30", "20:00", "21:30"]

FIRST_NAMES = [
    "DANIELA", "SANTIAGO", "CAMILA", "ANDRES", "MARIA", "SOFIA",
    "CARLOS", "VALENTINA", "DIEGO", "ISABELLA", "FELIPE", "LUCIA",
    "JUAN", "PAULA", "ALEJANDRO", "ELENA", "MARTIN", "ANA",
    "MIGUEL", "GABRIELA",
]

LAST_NAMES = [
    "MARTINEZ", "TORRES", "RODRIGUEZ", "GARCIA", "LOPEZ",
    "HERNANDEZ", "PEREZ", "GONZALEZ", "SANCHEZ", "RAMIREZ",
    "DIAZ", "MORENO", "JIMENEZ", "ALVAREZ", "ROMERO",
    "VARGAS", "CASTRO", "REYES", "ORTIZ", "CRUZ",
]

JUSTIFICATIONS = {
    "APPROVED": [
        "Flight cancelled, same airline available, no sensitive SSR, fare class matches",
        "Involuntary schedule change, reprotection within 24 hours approved",
        "Flight cancellation confirmed, alternative on same route available",
        "Delay exceeds 180 min, reprotection to next available flight approved",
        "Same-day rebooking, fare class maintained, passenger notified",
    ],
    "ESCALATED": [
        "SSR UMNR requires supervisor review for unaccompanied minor",
        "Passenger has WCHR SSR, accessibility requirements need manual check",
        "Multi-segment itinerary with codeshare, requires manual review",
        "VIP passenger flagged for priority handling",
        "Group booking exceeding 4 passengers requires supervisor approval",
    ],
    "REJECTED": [
        "Fare class downgrade not permitted under current policy",
        "Voluntary change request does not qualify for reprotection",
        "Ticket already refunded, reprotection not applicable",
        "Outside involuntary change window (>72 hours)",
    ],
}

RULE_APPLIED_CHOICES = [
    ("involuntary_change", 60),
    ("fare_protection", 20),
    ("ssr_check", 10),
    ("delay_rule", 10),
]


def _random_pnr() -> str:
    """Generate a 6-character uppercase alphanumeric PNR."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def _random_flight_number(airline: str) -> str:
    """Generate a realistic flight number like AV9421."""
    return f"{airline}{random.randint(100, 9999)}"


def _add_hours(time_str: str, hours: int, minutes: int = 0) -> str:
    """Add hours and minutes to a HH:MM time string."""
    h, m = map(int, time_str.split(":"))
    total_min = h * 60 + m + hours * 60 + minutes
    new_h = (total_min // 60) % 24
    new_m = total_min % 60
    return f"{new_h:02d}:{new_m:02d}"


def _weighted_choice(choices_with_weights):
    """Pick from list of (value, weight) tuples."""
    values = [c[0] for c in choices_with_weights]
    weights = [c[1] for c in choices_with_weights]
    return random.choices(values, weights=weights, k=1)[0]


def seed_database():
    """Drop all tables, recreate schema, and populate with demo data."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        _seed_reservations(session)
        _seed_flights(session)
        _seed_rules(session)
        _seed_decisions(session)
        session.commit()

        # Print summary
        res_count = session.query(Reservation).count()
        flight_count = session.query(Flight).count()
        rule_count = session.query(Rule).count()
        dec_count = session.query(Decision).count()
        print(f"Seeded: {res_count} reservations, {flight_count} flights, "
              f"{rule_count} rules, {dec_count} decisions")
    finally:
        session.close()


def _seed_reservations(session):
    """Create 4 specific demo scenarios + 12 generated reservations."""

    # ---------------------------------------------------------------
    # Scenario 1: Golden path (PNR: XKJR4T)
    # Flight cancelled, same airline has alternatives -> APPROVED
    # ---------------------------------------------------------------
    r1 = Reservation(pnr="XKJR4T")
    p1 = Passenger(
        last_name="MARTINEZ", first_name="DANIELA",
        ticket_number="045-2847563901", fare_class="Y",
        fare_basis="YOWCO", passenger_type="ADT",
    )
    s1 = Segment(
        flight_number="AV9421", airline="AV", origin="BOG",
        destination="MDE", departure_date=date(2026, 4, 15),
        departure_time="08:30", arrival_time="09:45",
        status="XX", cabin_class="Y", aircraft_type="A320",
    )
    r1.passengers.append(p1)
    r1.segments.append(s1)
    session.add(r1)

    # ---------------------------------------------------------------
    # Scenario 2: Escalation (PNR: BN7M2P)
    # UMNR SSR triggers ESCALATED decision
    # ---------------------------------------------------------------
    r2 = Reservation(pnr="BN7M2P")
    p2a = Passenger(
        last_name="TORRES", first_name="SANTIAGO",
        ticket_number="045-3921847560", fare_class="M",
        passenger_type="ADT",
    )
    p2b = Passenger(
        last_name="TORRES", first_name="LUCAS",
        fare_class="M", passenger_type="CHD",
    )
    ssr_umnr = SSRRecord(ssr_type="UMNR", ssr_detail="Unaccompanied minor, age 10")
    p2b.ssr_records.append(ssr_umnr)
    s2 = Segment(
        flight_number="AV8834", airline="AV", origin="BOG",
        destination="MIA", departure_date=date(2026, 4, 16),
        departure_time="14:20", arrival_time="19:35",
        status="XX", cabin_class="Y", aircraft_type="A330",
    )
    r2.passengers.extend([p2a, p2b])
    r2.segments.append(s2)
    session.add(r2)

    # ---------------------------------------------------------------
    # Scenario 3: Multi-segment (PNR: FW3KLC)
    # First segment cancelled, connection affected
    # ---------------------------------------------------------------
    r3 = Reservation(pnr="FW3KLC")
    p3 = Passenger(
        last_name="RODRIGUEZ", first_name="CAMILA",
        fare_class="H", fare_basis="HLXP3M", passenger_type="ADT",
    )
    s3a = Segment(
        flight_number="CM7712", airline="CM", origin="BOG",
        destination="PTY", departure_date=date(2026, 4, 17),
        departure_time="06:15", arrival_time="08:30",
        status="XX", cabin_class="Y", aircraft_type="E190",
    )
    s3b = Segment(
        flight_number="CM4451", airline="CM", origin="PTY",
        destination="MIA", departure_date=date(2026, 4, 17),
        departure_time="10:45", arrival_time="14:20",
        status="HK", cabin_class="Y", aircraft_type="B738",
    )
    r3.passengers.append(p3)
    r3.segments.extend([s3a, s3b])
    session.add(r3)

    # ---------------------------------------------------------------
    # Scenario 4: Multi-passenger family (PNR: HT9QRS)
    # 3 passengers, WCHR SSR on one
    # ---------------------------------------------------------------
    r4 = Reservation(pnr="HT9QRS")
    p4a = Passenger(
        last_name="GARCIA", first_name="ANDRES",
        fare_class="B", fare_basis="BOWRT", passenger_type="ADT",
    )
    p4b = Passenger(
        last_name="GARCIA", first_name="MARIA",
        fare_class="B", fare_basis="BOWRT", passenger_type="ADT",
    )
    ssr_wchr = SSRRecord(ssr_type="WCHR", ssr_detail="Wheelchair required for boarding")
    p4b.ssr_records.append(ssr_wchr)
    p4c = Passenger(
        last_name="GARCIA", first_name="SOFIA",
        fare_class="B", fare_basis="BOWRT", passenger_type="CHD",
    )
    s4 = Segment(
        flight_number="LA801", airline="LA", origin="BOG",
        destination="LIM", departure_date=date(2026, 4, 18),
        departure_time="11:00", arrival_time="14:15",
        status="TK", cabin_class="Y", aircraft_type="B787",
    )
    r4.passengers.extend([p4a, p4b, p4c])
    r4.segments.append(s4)
    session.add(r4)

    # ---------------------------------------------------------------
    # Generated reservations (12 more -> total 16)
    # ---------------------------------------------------------------
    generated_pnrs = [
        "KP5WDN", "QR8JTY", "LM4CVB", "NX6HAQ", "TP2RFG",
        "VW7ZKL", "DS9MYP", "BJ3UEN", "GH1XOT", "RC5WAJ",
        "YF8DLS", "ZN4KMI",
    ]

    used_names = set()
    ssr_candidates = ["PETC", "MAAS"]
    ssr_count = 0

    for i, pnr in enumerate(generated_pnrs):
        res = Reservation(pnr=pnr)

        # 1-3 passengers per reservation
        num_pax = random.choice([1, 1, 1, 2, 2, 3])
        family_name = LAST_NAMES[i % len(LAST_NAMES)]

        for j in range(num_pax):
            first = FIRST_NAMES[(i * 3 + j) % len(FIRST_NAMES)]
            fc = random.choice(FARE_CLASSES)
            ptype = "CHD" if j == 2 and num_pax == 3 else "ADT"
            pax = Passenger(
                last_name=family_name,
                first_name=first,
                fare_class=fc,
                passenger_type=ptype,
            )
            # Add SSR to 2-3 generated passengers
            if ssr_count < 3 and i in (2, 5, 9):
                ssr_type = ssr_candidates[ssr_count % len(ssr_candidates)]
                detail = ("Small dog in cabin, carrier required" if ssr_type == "PETC"
                          else "Meet and assist service requested")
                pax.ssr_records.append(SSRRecord(ssr_type=ssr_type, ssr_detail=detail))
                ssr_count += 1
            res.passengers.append(pax)

        # 1-2 segments per reservation
        num_segs = random.choice([1, 1, 2])
        route = ROUTES[i % len(ROUTES)]
        dep_date = date(2026, 4, 15) + timedelta(days=i % 16)
        dep_time = random.choice(DEPARTURE_TIMES)
        status = random.choice(["HK", "HK", "HK", "XX", "TK"])
        aircraft = random.choice(AIRCRAFT_TYPES)

        seg = Segment(
            flight_number=_random_flight_number(route[0]),
            airline=route[0],
            origin=route[1],
            destination=route[2],
            departure_date=dep_date,
            departure_time=dep_time,
            arrival_time=_add_hours(dep_time, random.randint(1, 4), random.randint(0, 45)),
            status=status,
            cabin_class="Y",
            aircraft_type=aircraft,
        )
        res.segments.append(seg)

        if num_segs == 2:
            # Create a connecting segment
            conn_route = ROUTES[(i + 3) % len(ROUTES)]
            conn_time = _add_hours(dep_time, random.randint(3, 5))
            seg2 = Segment(
                flight_number=_random_flight_number(conn_route[0]),
                airline=conn_route[0],
                origin=conn_route[1],
                destination=conn_route[2],
                departure_date=dep_date,
                departure_time=conn_time,
                arrival_time=_add_hours(conn_time, random.randint(1, 4), random.randint(0, 30)),
                status="HK",
                cabin_class="Y",
                aircraft_type=random.choice(AIRCRAFT_TYPES),
            )
            res.segments.append(seg2)

        session.add(res)


def _seed_flights(session):
    """Create 30-50 available flights for reprotection options."""
    flight_count = 0
    flight_dates = [date(2026, 4, 15) + timedelta(days=d) for d in range(6)]  # 6 days
    time_slots = ["06:00", "10:30", "14:00", "18:30"]

    for airline, origin, dest in ROUTES:
        # 2-4 flights per route spread across dates
        num_flights = random.randint(2, 4)
        selected_dates = random.sample(flight_dates, min(num_flights, len(flight_dates)))

        for dep_date in selected_dates:
            dep_time = random.choice(time_slots)
            duration_h = random.randint(1, 5)
            duration_m = random.choice([0, 15, 30, 45])
            arr_time = _add_hours(dep_time, duration_h, duration_m)

            flight = Flight(
                flight_number=_random_flight_number(airline),
                airline=airline,
                origin=origin,
                destination=dest,
                departure_date=dep_date,
                departure_time=dep_time,
                arrival_time=arr_time,
                available_seats=random.randint(2, 45),
                fare_class="Y",
                aircraft_type=random.choice(AIRCRAFT_TYPES),
                status="SCHEDULED",
            )
            session.add(flight)
            flight_count += 1

    # Ensure we hit at least 30 flights
    while flight_count < 30:
        route = random.choice(ROUTES)
        dep_date = random.choice(flight_dates)
        dep_time = random.choice(time_slots)
        flight = Flight(
            flight_number=_random_flight_number(route[0]),
            airline=route[0],
            origin=route[1],
            destination=route[2],
            departure_date=dep_date,
            departure_time=dep_time,
            arrival_time=_add_hours(dep_time, random.randint(1, 5), random.randint(0, 45)),
            available_seats=random.randint(2, 45),
            fare_class="Y",
            aircraft_type=random.choice(AIRCRAFT_TYPES),
            status="SCHEDULED",
        )
        session.add(flight)
        flight_count += 1


def _seed_rules(session):
    """Create 7 business rules for the decision engine."""
    rules = [
        Rule(id=1, field="delay_minutes", operator=">", value="180",
             action="offer_voucher", priority=1),
        Rule(id=2, field="passenger_name", operator="missing", value="",
             action="request_name", priority=1),
        Rule(id=3, field="pnr", operator="missing", value="",
             action="request_pnr", priority=1),
        Rule(id=4, field="event_type", operator="=", value="delay",
             action="process_delay", priority=2),
        Rule(id=5, field="flight_cancelled", operator="=", value="true",
             action="evaluate_reprotection", priority=1),
        Rule(id=6, field="has_sensitive_ssr", operator="=", value="true",
             action="escalate_to_supervisor", priority=1),
        Rule(id=7, field="fare_class_mismatch", operator="=", value="true",
             action="reject_reprotection", priority=2),
    ]
    session.add_all(rules)


def _seed_decisions(session):
    """Create 80-100 historical decisions spread across 14 days."""
    # Collect PNRs from seeded reservations for ~30% reuse
    all_reservations = session.query(Reservation).all()
    reservation_pnrs = [r.pnr for r in all_reservations]
    reservation_ids = {r.pnr: r.id for r in all_reservations}

    # Build extra PNRs for the remaining 70%
    extra_pnrs = [_random_pnr() for _ in range(30)]

    # Date range: 2026-04-01 through 2026-04-14
    start_date = date(2026, 4, 1)
    dates_14 = [start_date + timedelta(days=d) for d in range(14)]

    # Weekday distribution: Mon-Fri 6-10/day, Sat-Sun 2-4/day
    decisions_per_day = {}
    for d in dates_14:
        if d.weekday() < 5:  # Monday-Friday
            decisions_per_day[d] = random.randint(6, 10)
        else:  # Saturday-Sunday
            decisions_per_day[d] = random.randint(2, 4)

    total_decisions = sum(decisions_per_day.values())

    # Ensure total is 80-100
    while total_decisions < 80:
        # Add to a random weekday
        weekdays = [d for d in dates_14 if d.weekday() < 5]
        bump_day = random.choice(weekdays)
        decisions_per_day[bump_day] += 1
        total_decisions += 1

    while total_decisions > 100:
        weekdays = [d for d in dates_14 if d.weekday() < 5 and decisions_per_day[d] > 6]
        if not weekdays:
            break
        reduce_day = random.choice(weekdays)
        decisions_per_day[reduce_day] -= 1
        total_decisions -= 1

    # Status distribution: ~87% APPROVED, ~8% ESCALATED, ~5% REJECTED
    decision_idx = 0
    for d, count in decisions_per_day.items():
        for i in range(count):
            # Determine status
            roll = random.random()
            if roll < 0.87:
                status = "APPROVED"
            elif roll < 0.95:
                status = "ESCALATED"
            else:
                status = "REJECTED"

            # Pick PNR: 30% from reservations, 70% generated
            if random.random() < 0.3 and reservation_pnrs:
                pnr = random.choice(reservation_pnrs)
                res_id = reservation_ids.get(pnr)
            else:
                pnr = random.choice(extra_pnrs)
                res_id = None

            # Random hour between 08:00 and 20:00
            hour = random.randint(8, 20)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            created = datetime(d.year, d.month, d.day, hour, minute, second)

            # Processing time: 8-120ms, most between 15-60ms
            if random.random() < 0.7:
                proc_time = random.randint(15, 60)
            else:
                proc_time = random.randint(8, 120)

            rule_applied = _weighted_choice(RULE_APPLIED_CHOICES)
            justification = random.choice(JUSTIFICATIONS[status])

            decision = Decision(
                reservation_id=res_id,
                pnr=pnr,
                rule_applied=rule_applied,
                status=status,
                justification=justification,
                processing_time_ms=proc_time,
                created_at=created,
            )
            session.add(decision)
            decision_idx += 1


if __name__ == "__main__":
    seed_database()
