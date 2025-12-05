import streamlit as st
import math
from datetime import datetime, timedelta, time
import constants as ct
#print(dir(ct))

st.title("Axon Fleet Price Calculator ")

# -------------------------------
# Configuration
# -------------------------------
# -------------------------------
# Helper functions
# -------------------------------
def adjust_time(dt):
    """Ensure time is between 8 AM and 10 PM, else shift to next valid slot."""
    if dt.hour < ct.MIN_HOUR:
        return dt.replace(hour=ct.MIN_HOUR, minute=0)
    elif dt.hour > ct.MAX_HOUR:
        next_day = dt.date() + timedelta(days=1)
        return datetime.combine(next_day, time(ct.MIN_HOUR))
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
car_type = st.selectbox("Select Car Type", list(ct.FLEET_PRICES.keys()))
plan_type = st.selectbox("Select Plan Type", list(ct.FLEET_PRICES[car_type].keys()))

# Pickup & Drop side by side (date + hour together)
col1, col2 = st.columns(2)

with col1:
    st.write("### Pickup")
    pcol1, pcol2 = st.columns([2,1])
    with pcol1:
        pickup_date = st.date_input("Date", value=default_pickup.date(), key="pickup_date")
    with pcol2:
        pickup_hour = st.number_input("Hour", min_value=ct.MIN_HOUR, max_value=ct.MAX_HOUR, value=default_pickup.hour, key="pickup_hour")

with col2:
    st.write("### Drop")
    dcol1, dcol2 = st.columns([2,1])
    with dcol1:
        drop_date = st.date_input("Date", value=default_drop.date(), key="drop_date")
    with dcol2:
        drop_hour = st.number_input("Hour", min_value=ct.MIN_HOUR, max_value=ct.MAX_HOUR, value=default_drop.hour, key="drop_hour")

pickup_dt = datetime.combine(pickup_date, time(pickup_hour))
drop_dt = datetime.combine(drop_date, time(drop_hour))

# Show total duration
if drop_dt > pickup_dt:
    total_hours = (drop_dt - pickup_dt).total_seconds() / 3600
    total_days = total_hours / 24
    st.write(f"**Total Duration:** {total_hours:.1f} hours ({total_days:.1f} days)")
else:
    st.warning("Drop time must be after pickup time.")

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
        # Rental Price Calculation (base)
        # -------------------------------
        base_price = ct.FLEET_PRICES[car_type][plan_type]
        rental_price = base_price * (total_hours / 24)
        rental_price = math.ceil(rental_price)
        rental_price = float(f"{rental_price:.2f}")

        # -------------------------------
        # Total KM Calculation
        # -------------------------------
        if "Unlimited" in plan_type:
            total_km = "Unlimited"
        else:
            base_km = int(plan_type.split(" ")[0])  # e.g. "120 km / 24 hr"
            total_km = round(base_km * (total_hours / 24), 2)

        st.write(f"**Total KM Allowed:** {total_km}")

        # Pickup & Drop costs first
        pickup_choice = st.selectbox("Pickup Location", list(ct.LOCATIONS.keys()))
        drop_choice = st.selectbox("Drop Location", list(ct.LOCATIONS.keys()))
        pickup_cost = round(float(ct.LOCATIONS[pickup_choice]), 2)
        drop_cost = round(float(ct.LOCATIONS[drop_choice]), 2)

        subtotal_before_discount = round(rental_price + pickup_cost + drop_cost, 2)

        # -------------------------------
        # Discount Selection
        # -------------------------------
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

        # Cap discount at ₹10,000
        discount_value = min(discount_value, 10000.0)
        discount_value = round(discount_value, 2)

        discounted_price = round(subtotal_before_discount - discount_value, 2)

        # -------------------------------
        # LOAD Button (final calculation)
        # -------------------------------
        if st.button("LOAD"):
            # GST 18% (no rounding)
            gst = discounted_price * 0.18
            price_with_gst = discounted_price + gst

            # Final total (with security deposit, rounded)
            final_price = round(price_with_gst + ct.SECURITY_DEPOSIT, 2)

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
            st.write(f"Security Deposit: ₹{ct.SECURITY_DEPOSIT}")
            st.write(f"## Final Total Price: ₹{final_price}")


