import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Energy Dashboard", layout="wide")
st.markdown("""
<h1 style='text-align:center;
color:#0E4D92;
font-size:42px;'>
⚡ Energy Management Dashboard
</h1>

<p style='text-align:center;
font-size:18px;
color:gray;'>
Compressor Performance | Energy Analysis | Air Consumption Monitoring
</p>
""", unsafe_allow_html=True)
# =========================
# PREMIUM DASHBOARD STYLE
# =========================
st.markdown("""
<style>

/* Main background */
.stApp{
    background: linear-gradient(to right,#f4f7fc,#eef3fb);
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#0E4D92,#1E88E5);
    color:white;
}

/* Sidebar text */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{
    color:Black!important;
}

/* KPI Cards */
div[data-testid="metric-container"]{
    background:white;
    border-radius:18px;
    padding:20px;
    border-left:8px solid #1976D2;
    box-shadow:0px 8px 20px rgba(0,0,0,0.15);
    transition:0.3s;
}

div[data-testid="metric-container"]:hover{
    transform:translateY(-5px);
    box-shadow:0px 12px 28px rgba(0,0,0,0.25);
}

/* Tables */
div[data-testid="stDataFrame"]{
    border-radius:15px;
    overflow:hidden;
    border:1px solid #D9E2EF;
}

/* Buttons */
.stButton>button{
    background:#1976D2;
    color:white;
    border-radius:10px;
    border:none;
    padding:10px 20px;
    font-weight:bold;
}

.stButton>button:hover{
    background:#0E4D92;
}

/* Select Box */
div[data-baseweb="select"]{
    border-radius:10px;
}

/* Headers */
h1{
    color:#0E4D92;
    text-align:center;
    font-size:42px;
}

h2{
    color:#1565C0;
    border-left:6px solid #1976D2;
    padding-left:12px;
}

h3{
    color:#1565C0;
}

/* Expanders */
.streamlit-expanderHeader{
    font-size:18px;
    font-weight:bold;
}

/* Success Box */
div[data-testid="stAlert"]{
    border-radius:12px;
}

/* Horizontal Rule */
hr{
    border:1px solid #D9E2EF;
}

/* Scrollbar */
::-webkit-scrollbar{
    width:10px;
}

::-webkit-scrollbar-thumb{
    background:#1976D2;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# LOAD EXCEL
# =========================
# =========================
# UPLOAD EXCEL FILE
# =========================
uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Compressor Excel File",
    type=["xlsx", "xls"]
)

if uploaded_file is None:
    st.info("Please upload an Excel file to continue.")
    st.stop()

xls = pd.ExcelFile(uploaded_file)

sheet_map = {
    "Compressor Readings": "compressor readings",
    "Load & Unload": "load&unload",
    "Contribution of Each Compressor": "contribution of each compressor",
    "MV1 Analysis": "MV1",
    "MV2 Analysis": "MV 2",
    "Compressor in MV Panel1": "COMPRESSORINMV PANEL1",
    "CFM Analysis": "CFM IN EACH BAY"
}

# =========================
# HELPERS
# =========================
def load_sheet(name):
    df = pd.read_excel(xls, sheet_name=sheet_map[name])

    df.columns = df.columns.str.strip()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(
            df["Date"],
            dayfirst=True,
            errors="coerce"
        )

    return df

def safe_mean(df, col):
    if col not in df.columns:
        return 0
    return pd.to_numeric(df[col], errors="coerce").mean()

def safe_group_mean(df, cols):
    cols = [c for c in cols if c in df.columns]
    if not cols:
        return pd.Series(dtype=float)
    return df[cols].apply(pd.to_numeric, errors="coerce").mean()

def compare(df, col):
    if col not in df.columns:
        return None

    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if len(s) < 2:
        return None

    return s.iloc[-1], s.iloc[-2]

# =========================
# PIE CHART (FIXED SIZE)
# =========================
def pie_chart(data, title):

    # Convert to numeric
    data = pd.to_numeric(data, errors="coerce")

    # Remove invalid values
    data = data.dropna()
    data = data[data > 0]

    if len(data) == 0:
        st.warning(f"No valid data available for {title}")
        return

    def func(pct):
        return f"{pct:.1f}%"

    fig, ax = plt.subplots(figsize=(7,7))

    wedges, texts, autotexts = ax.pie(
        data.values,
        labels=data.index,          # C1, C2, Load, Unload, etc.
        autopct=func,
        startangle=90,
        labeldistance=0.45,         # Move labels inside
        pctdistance=0.70,           # Percentage inside
        textprops={
            "fontsize":10,
            "fontweight":"bold",
            "color":"white"
        },
        wedgeprops=dict(
            edgecolor="white",
            linewidth=2
        )
    )

    ax.set_title(title, fontsize=15, fontweight="bold")
    ax.axis("equal")

    st.pyplot(fig)

# =========================
# SIDEBAR
# =========================
# =========================
# SIDEBAR
# =========================

st.sidebar.image(
    "https://img.icons8.com/color/96/electrical.png",
    width=80
)

st.sidebar.markdown("## ⚡ Dashboard Menu")

page = st.sidebar.selectbox(
    "Choose Analysis",
    list(sheet_map.keys())
)

st.sidebar.markdown("---")
st.sidebar.success("📂 Upload Excel and choose analysis.")

df = load_sheet(page)

# =========================
# DATE FILTER
# =========================
if "Date" in df.columns:

    df["Date"] = pd.to_datetime(
    df["Date"],
    dayfirst=True,
    errors="coerce"
)
    df = df.dropna(subset=["Date"])

    dates = sorted(df["Date"].dt.date.unique())
    selected_date = st.sidebar.selectbox("Select Date", dates)

    df = df[df["Date"].dt.date == selected_date]

# =========================
# DATA VIEW
# =========================
st.subheader(f"📊 {page}")

with st.expander("📄 View Raw Data"):
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

# =========================
# 1. COMPRESSOR READINGS
# =========================
if page == "Compressor Readings":

    st.divider()
    st.subheader("📈 Key Performance Indicators")

    col1, col2, col3 = st.columns(3)
    col1.metric("Load %", round(safe_mean(df, "load%"), 2))
    col2.metric("Unload %", round(safe_mean(df, "unload%"), 2))
    col3.metric("Availability %", round(safe_mean(df, "Availabilty%"), 2))

    col4, col5 = st.columns(2)
    col4.metric("Runtime", round(safe_mean(df, "Run time"), 2))
    col5.metric("Stop Time", round(safe_mean(df, "Stop time"), 2))

    st.metric("Fault %", round(safe_mean(df, "Fault%"), 2))

    # PIE CHART
    st.subheader("Compressor Overview")
    metrics = ["load%", "unload%", "Availabilty%", "Fault%"]
    data = safe_group_mean(df, metrics)

    if not data.empty:
        pie_chart(data, "Compressor Overview")

    # COMPARISON
    st.subheader("Comparison")

    comp = []
    for m in metrics:
        res = compare(df, m)
        if res:
            comp.append([m, res[0], res[1]])

    if comp:
        comp_df = pd.DataFrame(comp, columns=["Metric", "Current", "Previous"])
        st.dataframe(comp_df)
        st.bar_chart(comp_df.set_index("Metric"))

# =========================
# 2. LOAD & UNLOAD
# =========================
elif page == "Load & Unload":

    st.subheader("Load & Unload")

    comp_cols = ["C1", "C2", "C3", "C4"]
    data = safe_group_mean(df, comp_cols)

    if not data.empty:

        col1, col2 = st.columns(2)

        with col1:
            pie_chart(data, "Load Distribution")

        with col2:
            unload_cols = [c for c in df.columns if "UNLOAD" in c.upper()]
            unload_data = safe_group_mean(df, unload_cols)

            if not unload_data.empty:
                pie_chart(unload_data, "Unload Distribution")

        st.bar_chart(data)

        # COMPARISON
        st.subheader("Comparison")

        comp = []
        for c in comp_cols:
            res = compare(df, c)
            if res:
                comp.append([c, res[0], res[1]])

        if comp:
            comp_df = pd.DataFrame(comp, columns=["Compressor", "Current", "Previous"])
            st.dataframe(comp_df)
            st.bar_chart(comp_df.set_index("Compressor"))

# =========================
# 3. CONTRIBUTION
# =========================
elif page == "Contribution of Each Compressor":

    st.subheader("Contribution")

    cols = ["C1%", "C2%", "C3%", "C4%"]
    data = safe_group_mean(df, cols)

    if not data.empty:
        pie_chart(data, "Contribution Pie")
        st.bar_chart(data)

        comp = []
        for c in cols:
            res = compare(df, c)
            if res:
                comp.append([c, res[0], res[1]])

        if comp:
            st.subheader("Comparison")
            comp_df = pd.DataFrame(comp, columns=["Comp", "Current", "Previous"])
            st.dataframe(comp_df)
            st.bar_chart(comp_df.set_index("Comp"))

# =========================
# 4. MV1 / MV2
# =========================
# =========================
# 4. MV1 ANALYSIS
# =========================
elif page == "MV1 Analysis":

    st.subheader("⚡ MV1 Analysis")

    cols = [
        "MV PANEL 2%",
        "SR FUNANCE%",
        "CPS%",
        "OVEN%",
        "AMF%"
    ]

    cols = [c for c in cols if c in df.columns]

    data = df[cols].apply(pd.to_numeric, errors="coerce").mean()
    data = data.dropna()
    data = data[data > 0]

    if data.empty:
        st.warning("No valid data available.")
    else:
        st.bar_chart(data)
        st.line_chart(data)

elif page == "MV2 Analysis":

    st.subheader("⚡ MV Panel 2 Analysis")

    # Percentage columns (exclude TOTAL%)
    cols = [
        "SSB1%",
        "SSB2%",
        "SSB3%",
        "SSB4%",
        "SSB5%",
        "COMPR%",
        "MLSB%"
    ]

    # Keep only columns that exist
    cols = [c for c in cols if c in df.columns]

    if len(cols) == 0:
        st.error("Percentage columns not found.")
        st.stop()

    # Convert to numeric
    data = (
        df[cols]
        .apply(pd.to_numeric, errors="coerce")
        .mean()
        .dropna()
    )

    # Remove zero values
    data = data[data > 0]

    if data.empty:
        st.warning("No valid percentage data available.")
    else:

        st.subheader("Horizontal Comparison")
        st.bar_chart(data)

        st.subheader("Trend")
        st.line_chart(df[cols].apply(pd.to_numeric, errors="coerce"))

        st.subheader("Statistics")
        st.dataframe(data.reset_index().rename(
            columns={"index":"Section",0:"Average %"}
        ))
elif page == "Compressor in MV Panel1":

    st.subheader("⚡ Compressor Contribution in MV Panel 1")

    cols = ["C1%", "C2%", "C3%", "C4%"]

    # Convert to numeric
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    data = df[cols].mean()

    # Fill NaN with 0
    data = data.fillna(0)

    # Don't remove zeros until after checking
    if data.sum() == 0:
        st.warning("No compressor contribution recorded for this selected date.")
    else:

        st.bar_chart(data)

        st.line_chart(df[cols])

        st.dataframe(
            pd.DataFrame({
                "Compressor": cols,
                "Contribution (%)": data.values.round(2)
            }),
            use_container_width=True
        )
# =========================
# 6. CFM ANALYSIS
# =========================
elif page == "CFM Analysis":

    st.subheader("💨 CFM Dashboard")

    # Show available columns (remove this after checking)
    st.write("Columns found:", list(df.columns))

    # Find Bay column
    bay_col = None
    for col in df.columns:
        if "BAY" in str(col).upper():
            bay_col = col
            break

    # Find Total CFM column
    total_col = None
    for col in df.columns:
        if "TOTAL" in str(col).upper() and "CFM" in str(col).upper():
            total_col = col
            break

    # If not found, use "Total"
    if total_col is None:
        for col in df.columns:
            if str(col).strip().upper() == "TOTAL":
                total_col = col
                break

    # Find Overall column
    overall_col = None
    for col in df.columns:
        if "OVERALL" in str(col).upper():
            overall_col = col
            break

    if bay_col is None or total_col is None:
        st.error("Bay or Total CFM column not found.")
        st.stop()

    # Convert to numeric
    df[total_col] = pd.to_numeric(df[total_col], errors="coerce")

    # Bay totals
    bay_df = (
        df[[bay_col, total_col]]
        .dropna()
        .groupby(bay_col)[total_col]
        .sum()
        .reset_index()
    )

    bay_df = bay_df[bay_df[total_col] > 0]
    bay_df = bay_df.sort_values(total_col, ascending=False)

    # Overall
    if overall_col:
        overall = pd.to_numeric(df[overall_col], errors="coerce").dropna()

        if len(overall):
            overall_cfm = overall.iloc[0]
        else:
            overall_cfm = bay_df[total_col].sum()
    else:
        overall_cfm = bay_df[total_col].sum()

    installed = 2785
    unused = installed - overall_cfm
    utilization = overall_cfm / installed * 100

    # KPI
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Overall CFM", round(overall_cfm))
    c2.metric("Installed CFM", installed)
    c3.metric("Unused CFM", round(unused))
    c4.metric("Utilization", f"{utilization:.1f}%")

    # Horizontal chart
    st.subheader("Bay Consumption")

    chart = bay_df.set_index(bay_col)

    st.bar_chart(chart[total_col])

    # Ranking table
    st.subheader("Ranking")

    rank = bay_df.copy()
    rank.insert(0, "Rank", range(1, len(rank)+1))

    st.dataframe(rank, use_container_width=True)

    # Highest
    highest = rank.iloc[0]

    st.success(
        f"🏆 Highest Consumption: {highest[bay_col]} ({highest[total_col]:.0f} CFM)"
    )