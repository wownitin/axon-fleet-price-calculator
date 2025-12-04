import streamlit as st
import math
from datetime import datetime, timedelta, time

st.title("Axon Fleet Price Calculator ")

# -------------------------------
# Configuration
# -------------------------------
FLEET_PRICES = {
    "Ignis Grey 3415": {
        "120 km / 24 hr": 1799,
        "240 km / 24 hr": 2299,
        "Unlimited km / 24 hr": 2899
    },
    "Ignis Blue 1923": {
        "120 km / 24 hr": 1899,
        "240 km / 24 hr": 2399,
        "Unlimited km / 24 hr": 2999
    },
    "Swift Brown 4022": {
        "120 km / 24 hr": 2099,
        "240 km / 24 hr": 2599,
        "Unlimited km / 24 hr": 3199
    },
    "Baleno Blue 1292": {
        "120 km / 24 hr": 2099,
        "240 km / 24 hr": 2599,
        "Unlimited km / 24 hr": 3199
    },
    "Baleno Grey 6027": {
        "120 km / 24 hr": 2299,
        "240 km / 24 hr": 2799,
        "Unlimited km / 24 hr": 3399
    },
    "Fronx Grey 1291": {
        "120 km / 24 hr": 2399,
        "240 km / 24 hr": 2899,
        "Unlimited km / 24 hr": 3499
    },
    "Fronx Blue 5049": {
        "120 km / 24 hr": 2499,
        "240 km / 24 hr": 2999,
        "Unlimited km / 24 hr": 3599
    },
    "XL6 Silver": {
        "120 km / 24 hr": 2999,
        "240 km / 24 hr": 3499,
        "Unlimited km / 24 hr": 4099
    }
}

LOCATIONS = {
    "Hub (Free)": 0,
    "Railway Station Civil Lines": 300,
    "Railway Station Sangam": 500,
    "Railway Station Cheoki": 600,
    "Airport": 600,
    "MNNIT": 600,
    "IIIT": 600,
    "UIT/UCER": 1000,
    "SHUATS": 600
}

SECURITY_DEPOSIT = 4000.0
MIN_HOUR = 8
MAX_HOUR = 22

# -------------------------------
# Helper functions
# -------------------------------
def adjust_time(dt):
    """Ensure time is between 8 AM and 10 PM, else shift to next valid slot."""
    if dt.hour < MIN_HOUR:
        return dt.replace(hour=MIN_HOUR, minute=0)
    elif dt.hour > MAX_HOUR:
        next_day = dt.date() + timedelta(days=1)
        return datetime.combine(next_day, time(MIN_HOUR))
    else:
        return dt.replace(minute=0)

# -------------------------------
# Default pickup/drop times
# -------------------------------
now = datetime.now()
default_pickup = adjust_time(now + timedelta(hours=2))
default_drop = adjust_time(default_pickup + timedelta(days=1))

# -------------------------------
# User Inputs
# -------------------------------
car_type = st.selectbox("Select Car Type", list(FLEET_PRICES.keys()))
plan_type = st.selectbox("Select Plan Type", list(FLEET_PRICES[car_type].keys()))

pickup_date = st.date_input("Pickup Date", value=default_pickup.date())
pickup_hour = st.number_input("Pickup Hour (0-23)", min_value=MIN_HOUR, max_value=MAX_HOUR, value=default_pickup.hour)

drop_date = st.date_input("Drop Date", value=default_drop.date())
drop_hour = st.number_input("Drop Hour (0-23)", min_value=MIN_HOUR, max_value=MAX_HOUR, value=default_drop.hour)

pickup_dt = datetime.combine(pickup_date, time(pickup_hour))
drop_dt = datetime.combine(drop_date, time(drop_hour))

# -------------------------------
# Validation
# -------------------------------
if drop_dt <= pickup_dt:
    st.error("❌ Drop time must be after pickup time.")
else:
    total_hours = (drop_dt - pickup_dt).total_seconds() / 3600
    if total_hours < 24:
        st.error("❌ Booking must be at least 1 day.")
    else:
        # -------------------------------
        # Rental Price Calculation
        # -------------------------------
        base_price = FLEET_PRICES[car_type][plan_type]
        rental_price = base_price * (total_hours / 24)
        rental_price = math.ceil(rental_price)
        rental_price = float(f"{rental_price:.2f}")

        # Pickup & Drop costs first
        pickup_choice = st.selectbox("Pickup Location", list(LOCATIONS.keys()))
        drop_choice = st.selectbox("Drop Location", list(LOCATIONS.keys()))
        pickup_cost = round(float(LOCATIONS[pickup_choice]), 2)
        drop_cost = round(float(LOCATIONS[drop_choice]), 2)

        subtotal_before_discount = round(rental_price + pickup_cost + drop_cost, 2)

        # Discount
        discount_options = ["None", "₹300", "10%", "20%", "25%", "Other"]
        discount_choice = st.selectbox("Select Discount", discount_options)

        discount_value = 0.0
        if discount_choice == "₹300":
            discount_value = 300.0
        elif discount_choice == "10%":
            if subtotal_before_discount >= 5000:
                discount_value = subtotal_before_discount * 0.10
            else:
                st.warning("⚠️ Minimum subtotal ₹5000 required for 10% offer")
        elif discount_choice == "20%":
            if subtotal_before_discount >= 10000:
                discount_value = subtotal_before_discount * 0.20
            else:
                st.warning("⚠️ Minimum subtotal ₹10000 required for 20% offer")
        elif discount_choice == "25%":
            if subtotal_before_discount >= 20000:
                discount_value = subtotal_before_discount * 0.25
            else:
                st.warning("⚠️ Minimum subtotal ₹20000 required for 25% offer")
        elif discount_choice == "Other":
            discount_value = float(st.number_input("Enter custom discount (₹)", min_value=0, value=0))
        discount_value = round(discount_value, 2)

        discounted_price = round(subtotal_before_discount - discount_value, 2)

        # GST 18% (no rounding)
        gst = discounted_price * 0.18
        price_with_gst = discounted_price + gst

        # Final total (with security deposit, rounded)
        final_price = round(price_with_gst + SECURITY_DEPOSIT, 2)

        # -------------------------------
        # Price Breakdown
        # -------------------------------
        st.write("### Price Breakdown")
        st.write(f"Rental Price (before discount): ₹{rental_price}")
        st.write(f"Pickup Cost ({pickup_choice}): ₹{pickup_cost}")
        st.write(f"Drop Cost ({drop_choice}): ₹{drop_cost}")
        st.write(f"Subtotal before Discount: ₹{subtotal_before_discount}")
        st.write(f"Discount Applied: -₹{discount_value}")
        st.write(f"Price after Discount: ₹{discounted_price}")
        st.write(f"GST (18%): ₹{gst}")  # full precision
        st.write(f"Security Deposit: ₹{SECURITY_DEPOSIT}")
        st.write(f"## Final Total Price: ₹{final_price}")
