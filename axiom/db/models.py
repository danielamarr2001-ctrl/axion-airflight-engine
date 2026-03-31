"""SQLAlchemy ORM models for the AXIOM AirFlight Engine database."""

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from axiom.db.engine import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pnr: Mapped[str] = mapped_column(String(6), unique=True, index=True)
    booking_reference: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    passengers: Mapped[List["Passenger"]] = relationship(
        back_populates="reservation", cascade="all, delete-orphan"
    )
    segments: Mapped[List["Segment"]] = relationship(
        back_populates="reservation", cascade="all, delete-orphan"
    )


class Passenger(Base):
    __tablename__ = "passengers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reservation_id: Mapped[int] = mapped_column(Integer, ForeignKey("reservations.id"))
    last_name: Mapped[str] = mapped_column(String(50))
    first_name: Mapped[str] = mapped_column(String(50))
    ticket_number: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    fare_class: Mapped[str] = mapped_column(String(1))
    fare_basis: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    passenger_type: Mapped[str] = mapped_column(String(3), default="ADT")

    reservation: Mapped["Reservation"] = relationship(back_populates="passengers")
    ssr_records: Mapped[List["SSRRecord"]] = relationship(
        back_populates="passenger", cascade="all, delete-orphan"
    )


class Segment(Base):
    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reservation_id: Mapped[int] = mapped_column(Integer, ForeignKey("reservations.id"))
    flight_number: Mapped[str] = mapped_column(String(7))
    airline: Mapped[str] = mapped_column(String(2))
    origin: Mapped[str] = mapped_column(String(3))
    destination: Mapped[str] = mapped_column(String(3))
    departure_date: Mapped[date] = mapped_column(Date)
    departure_time: Mapped[str] = mapped_column(String(5))
    arrival_time: Mapped[str] = mapped_column(String(5))
    status: Mapped[str] = mapped_column(String(2), default="HK")
    cabin_class: Mapped[str] = mapped_column(String(1), default="Y")
    aircraft_type: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)

    reservation: Mapped["Reservation"] = relationship(back_populates="segments")


class SSRRecord(Base):
    __tablename__ = "ssr_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    passenger_id: Mapped[int] = mapped_column(Integer, ForeignKey("passengers.id"))
    ssr_type: Mapped[str] = mapped_column(String(4))
    ssr_detail: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    passenger: Mapped["Passenger"] = relationship(back_populates="ssr_records")


class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flight_number: Mapped[str] = mapped_column(String(7))
    airline: Mapped[str] = mapped_column(String(2))
    origin: Mapped[str] = mapped_column(String(3))
    destination: Mapped[str] = mapped_column(String(3))
    departure_date: Mapped[date] = mapped_column(Date)
    departure_time: Mapped[str] = mapped_column(String(5))
    arrival_time: Mapped[str] = mapped_column(String(5))
    available_seats: Mapped[int] = mapped_column(Integer, default=0)
    fare_class: Mapped[str] = mapped_column(String(1), default="Y")
    aircraft_type: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="SCHEDULED")


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field: Mapped[str] = mapped_column(String(50))
    operator: Mapped[str] = mapped_column(String(10))
    value: Mapped[str] = mapped_column(String(100), default="")
    action: Mapped[str] = mapped_column(String(100))
    priority: Mapped[int] = mapped_column(Integer, default=1)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reservation_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("reservations.id"), nullable=True
    )
    pnr: Mapped[Optional[str]] = mapped_column(String(6), nullable=True)
    rule_applied: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    options_generated: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    selected_option: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    operator_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
