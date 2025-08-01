
import streamlit as st
import pandas as pd
import re

# --- Constants ---
ROADS = ["Highway 1", "Highway 2", "Highway 3"]
LANES = ["Lane 1", "Lane 2"]
VEHICLE_TYPES = ["Car", "Bus", "Truck"]
ROAD_SPEED_LIMIT = {"Highway 1": (60, 100), "Highway 2": (60, 100), "Highway 3": (60, 100)}
ROAD_CAPACITY = 10
SIGNAL_DIRECTIONS = ["North-South", "East-West"]
SIGNAL_SEQUENCE = ["Red", "Green", "Yellow"]
INCIDENT_TYPES = ["Accident", "Construction"]
TOLL_RATES = {"Car": 40, "Bus": 80, "Truck": 120}

# --- Session State Initialization ---
def reset_all():
    st.session_state.vehicles = []
    st.session_state.signals = {d: "Red" for d in SIGNAL_DIRECTIONS}
    st.session_state.incidents = []
    st.session_state.tolls = []

if "vehicles" not in st.session_state:
    st.session_state.vehicles = []
if "signals" not in st.session_state:
    st.session_state.signals = {d: "Red" for d in SIGNAL_DIRECTIONS}
if "incidents" not in st.session_state:
    st.session_state.incidents = []
if "tolls" not in st.session_state:
    st.session_state.tolls = []

# --- Sidebar Navigation ---
st.sidebar.title("🚦 Smart Highway Management")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Vehicle Entry", "Traffic Signal Control", "Incident Management", "Toll Plaza", "Nearby Services"]
)
if st.sidebar.button("Reset All Data"):
    reset_all()
    st.sidebar.success("All data reset.")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total Vehicles:** {len(st.session_state.vehicles)}")
st.sidebar.markdown(f"**Active Incidents:** {sum(1 for i in st.session_state.incidents if not i['resolved'])}")

# --- Dashboard Page ---
if page == "Dashboard":
    st.header("📊 Highway Dashboard")
    st.metric("Total Vehicles", len(st.session_state.vehicles))
    st.metric("Active Incidents", sum(1 for i in st.session_state.incidents if not i["resolved"]))
    if st.session_state.vehicles:
        road_usage = pd.Series([v['road'] for v in st.session_state.vehicles]).value_counts()
        st.bar_chart(road_usage)

# --- Vehicle Entry Page ---
elif page == "Vehicle Entry":
    st.header("🚗 Vehicle Entry & Exit Management")
    with st.form("add_vehicle_form"):
        plate = st.text_input("Vehicle Plate Number", help="Must be unique")
        vtype = st.selectbox("Vehicle Type", VEHICLE_TYPES)
        road = st.selectbox("Assign to Road", ROADS)
        lane = st.selectbox("Assign to Lane", LANES)
        speed = st.number_input(f"Set Speed (km/h) [{ROAD_SPEED_LIMIT[road][0]}–{ROAD_SPEED_LIMIT[road][1]}]", min_value=0, max_value=200, value=80)
        add_vehicle = st.form_submit_button("Add Vehicle")

    if add_vehicle:
        plate_clean = plate.strip().upper()
        if not plate_clean:
            st.error("Vehicle plate cannot be empty.")
        elif not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$', plate_clean):
            st.error("Invalid plate format. Use format like 'AB12CD3456'.")
        elif any(v["plate"] == plate_clean for v in st.session_state.vehicles):
            st.error("Vehicle already exists.")
        elif any(inc["road"] == road and not inc["resolved"] for inc in st.session_state.incidents):
            st.error(f"{road} has an active incident.")
        elif sum(1 for v in st.session_state.vehicles if v["road"] == road) >= ROAD_CAPACITY:
            st.error(f"{road} is at full capacity.")
        else:
            st.session_state.vehicles.append({
                "plate": plate_clean,
                "type": vtype,
                "road": road,
                "lane": lane,
                "speed": speed
            })
            st.success(f"Vehicle {plate_clean} added.")

    st.subheader("Vehicles")
    df = pd.DataFrame(st.session_state.vehicles)
    if not df.empty:
        st.dataframe(df)

# --- Traffic Signal Control ---
elif page == "Traffic Signal Control":
    st.header("🚦 Traffic Signal Control")
    for direction in SIGNAL_DIRECTIONS:
        st.subheader(f"{direction}")
        current = st.session_state.signals[direction]
        idx = SIGNAL_SEQUENCE.index(current)
        next_state = SIGNAL_SEQUENCE[(idx + 1) % len(SIGNAL_SEQUENCE)]
        st.write(f"Current: {current}")
        if st.button(f"Change to {next_state}", key=direction):
            if next_state == "Green":
                others = [d for d in SIGNAL_DIRECTIONS if d != direction and st.session_state.signals[d] == "Green"]
                if others:
                    st.error(f"Conflict with {others[0]}. Cannot set to Green.")
                    continue
            st.session_state.signals[direction] = next_state

# --- Incident Management ---
elif page == "Incident Management":
    st.header("🚧 Incident Management")
    with st.form("add_incident_form"):
        road = st.selectbox("Road", ROADS)
        inc_type = st.selectbox("Type", INCIDENT_TYPES)
        add = st.form_submit_button("Add Incident")
    if add:
        if any(inc for inc in st.session_state.incidents if inc["road"] == road and not inc["resolved"]):
            st.error("Active incident already exists.")
        else:
            st.session_state.incidents.append({"road": road, "type": inc_type, "resolved": False})
            st.success("Incident logged.")

    st.subheader("Active Incidents")
    df = pd.DataFrame([i for i in st.session_state.incidents if not i["resolved"]])
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No active incidents.")

# --- Toll Plaza ---
elif page == "Toll Plaza":
    st.header("🏁 Toll Plaza Management")
    with st.form("toll_form"):
        road = st.selectbox("Road", ROADS)
        vtype = st.selectbox("Vehicle Type", VEHICLE_TYPES)
        pay = st.form_submit_button("Charge Toll")
    if pay:
        fee = TOLL_RATES[vtype]
        st.session_state.tolls.append({"road": road, "type": vtype, "fee": fee})
        st.success(f"Charged ₹{fee} for {vtype} on {road}.")

    st.subheader("Toll Records")
    df = pd.DataFrame(st.session_state.tolls)
    if not df.empty:
        st.dataframe(df)
        st.metric("Total Collection", f"₹{df['fee'].sum()}")
    else:
        st.info("No tolls yet.")

# --- Nearby Services ---
elif page == "Nearby Services":
    st.header("📍 Nearby Services")
    road = st.selectbox("Road", ROADS)
    st.subheader("🏨 Hotels")
    for h in ["Highway Inn", "Rest & Go", "GreenView"]:
        st.markdown(f"- {h}")
    st.subheader("⛽ Petrol Bunks")
    for s in ["Shell", "Indian Oil", "Bharat Petroleum"]:
        st.markdown(f"- {s}")

st.caption("Smart Highway System • Streamlit Demo")
