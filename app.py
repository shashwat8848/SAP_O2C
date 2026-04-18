"""
SAP Order-to-Cash (O2C) Process Simulator
Capstone Project - SAP Track
Built with Streamlit
"""

import streamlit as st
import pandas as pd
import datetime
import random
import string

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SAP O2C Simulator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f0f4f8; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #003366 0%, #0059b3 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stRadio label { color: white !important; }

    /* Cards */
    .sap-card {
        background: white;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 5px solid #003366;
    }
    .sap-card h3 { color: #003366; margin-top: 0; }

    /* Step badge */
    .step-badge {
        display: inline-block;
        background: #003366;
        color: white;
        border-radius: 50%;
        width: 32px; height: 32px;
        line-height: 32px;
        text-align: center;
        font-weight: bold;
        margin-right: 10px;
        font-size: 15px;
    }

    /* Status chips */
    .status-open    { background:#fef3c7; color:#92400e; padding:3px 12px; border-radius:20px; font-size:13px; font-weight:600; }
    .status-done    { background:#d1fae5; color:#065f46; padding:3px 12px; border-radius:20px; font-size:13px; font-weight:600; }
    .status-pending { background:#dbeafe; color:#1e40af; padding:3px 12px; border-radius:20px; font-size:13px; font-weight:600; }

    /* Header banner */
    .main-header {
        background: linear-gradient(135deg, #003366, #0059b3);
        color: white;
        padding: 28px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    .main-header h1 { color: white; margin: 0; font-size: 28px; }
    .main-header p  { color: #b3d1ff; margin: 6px 0 0 0; font-size: 14px; }

    /* Metric box */
    .metric-box {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.07);
    }
    .metric-box .number { font-size: 32px; font-weight: 700; color: #003366; }
    .metric-box .label  { font-size: 13px; color: #666; margin-top: 4px; }

    /* Tcode label */
    .tcode {
        background: #fffbeb;
        border: 1px solid #f59e0b;
        color: #b45309;
        padding: 2px 10px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 13px;
        font-weight: 600;
    }

    /* Process flow node */
    .flow-step {
        background: white;
        border: 2px solid #003366;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
        font-weight: 600;
        color: #003366;
        font-size: 13px;
    }
    .flow-step.active {
        background: #003366;
        color: white;
    }
    .flow-arrow {
        text-align: center;
        font-size: 22px;
        color: #003366;
        padding: 4px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ───────────────────────────────────────────────────────
def init_state():
    defaults = {
        "orders": [],
        "deliveries": [],
        "invoices": [],
        "payments": [],
        "current_step": 1,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

# ─── Helper Functions ─────────────────────────────────────────────────────────
def gen_id(prefix, n=6):
    return prefix + "".join(random.choices(string.digits, k=n))

def today():
    return datetime.date.today().strftime("%d-%m-%Y")

def future_date(days):
    return (datetime.date.today() + datetime.timedelta(days=days)).strftime("%d-%m-%Y")

PRODUCTS = {
    "Laptop Pro X1":      {"price": 85000, "uom": "EA"},
    "Office Chair Delux": {"price": 12500, "uom": "EA"},
    "Printer HP 5000":    {"price": 22000, "uom": "EA"},
    "A4 Paper (Box)":     {"price":  1200, "uom": "BOX"},
    "UPS 650VA":          {"price":  5500, "uom": "EA"},
    "Monitor 24-inch":    {"price": 18000, "uom": "EA"},
    "Keyboard & Mouse":   {"price":  2800, "uom": "SET"},
    "Switch 24-Port":     {"price": 32000, "uom": "EA"},
}

CUSTOMERS = {
    "Infosys Ltd":        {"city": "Bengaluru", "credit_limit": 500000},
    "TCS Mumbai":         {"city": "Mumbai",    "credit_limit": 800000},
    "Wipro Hyderabad":    {"city": "Hyderabad", "credit_limit": 600000},
    "HCL Noida":          {"city": "Noida",     "credit_limit": 400000},
    "Tech Mahindra Pune": {"city": "Pune",      "credit_limit": 700000},
}

PAYMENT_TERMS = {"Immediate (0 days)": 0, "Net 15": 15, "Net 30": 30, "Net 45": 45}
TAX_RATE = 0.18  # 18% GST

# ─── Sidebar Navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💼 SAP O2C Simulator")
    st.markdown("---")
    page = st.radio("📋 Navigate", [
        "🏠 Dashboard",
        "📝 Step 1: Sales Order (VA01)",
        "✅ Step 2: Credit Check",
        "🚚 Step 3: Delivery (VL01N)",
        "📦 Step 4: Goods Issue (VL02N)",
        "🧾 Step 5: Invoice (VF01)",
        "💰 Step 6: Payment (F-28)",
        "📊 Step 7: Reports & Ledger",
    ])
    st.markdown("---")
    st.markdown("**O2C Process Flow**")
    steps = ["Sales Order","Credit Check","Delivery","Goods Issue","Invoice","Payment","Reports"]
    for i, s in enumerate(steps, 1):
        icon = "✅" if i < st.session_state.current_step else ("🔵" if i == st.session_state.current_step else "⬜")
        st.markdown(f"{icon} **{i}.** {s}")

# ─── DASHBOARD ────────────────────────────────────────────────────────────────
if page == "🏠 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>💼 SAP Order-to-Cash (O2C) Process Simulator</h1>
        <p>Simulating SAP S/4HANA SD Module | End-to-End Sales Cycle</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    total_order_val = sum(o["net_value"] for o in st.session_state.orders)
    total_invoiced  = sum(i["invoice_amount"] for i in st.session_state.invoices)
    total_received  = sum(p["amount_paid"] for p in st.session_state.payments)
    outstanding     = total_invoiced - total_received

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-box">
            <div class="number">{len(st.session_state.orders)}</div>
            <div class="label">Sales Orders</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-box">
            <div class="number">₹{total_order_val:,.0f}</div>
            <div class="label">Total Order Value</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-box">
            <div class="number">₹{total_invoiced:,.0f}</div>
            <div class="label">Total Invoiced</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-box">
            <div class="number">₹{outstanding:,.0f}</div>
            <div class="label">Outstanding AR</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Process flow diagram
    st.markdown("### 🔄 O2C Process Flow")
    cols = st.columns(7)
    flow_steps = [
        ("VA01","Sales\nOrder"),("Credit","Credit\nCheck"),
        ("VL01N","Delivery"),("VL02N","Goods\nIssue"),
        ("VF01","Invoice"),("F-28","Payment"),("FBL5N","AR\nLedger"),
    ]
    for i, (col, (tc, label)) in enumerate(zip(cols, flow_steps)):
        with col:
            active = "active" if (i+1) < st.session_state.current_step else ""
            st.markdown(f"""
            <div class="flow-step {active}">
                <div style="font-size:11px;opacity:0.7">{tc}</div>
                <div style="margin-top:4px">{label}</div>
            </div>
            """, unsafe_allow_html=True)
            if i < 6:
                st.markdown('<div style="text-align:center;font-size:20px;color:#003366">→</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent transactions
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("### 📋 Recent Sales Orders")
        if st.session_state.orders:
            df = pd.DataFrame(st.session_state.orders)[["order_id","customer","material","quantity","net_value","status"]]
            df.columns = ["Order ID","Customer","Material","Qty","Net Value (₹)","Status"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No sales orders yet. Go to Step 1 to create one.")

    with col_right:
        st.markdown("### 🧾 Recent Invoices")
        if st.session_state.invoices:
            df = pd.DataFrame(st.session_state.invoices)[["invoice_no","customer","invoice_amount","status"]]
            df.columns = ["Invoice No","Customer","Amount (₹)","Status"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No invoices yet. Complete Steps 1–4 first.")

# ─── STEP 1: SALES ORDER ──────────────────────────────────────────────────────
elif page == "📝 Step 1: Sales Order (VA01)":
    st.markdown("""
    <div class="main-header">
        <h1>📝 Step 1: Sales Order Creation</h1>
        <p>Transaction Code: <strong>VA01</strong> — Create Standard Sales Order</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sap-card">
        <h3>📖 What is a Sales Order?</h3>
        <p>A <b>Sales Order (SO)</b> is a legally binding document created when a customer places an order for goods/services.
        In SAP SD, it is created via T-Code <b>VA01</b>. It captures the customer, material, quantity, pricing,
        delivery date, and payment terms — and serves as the foundation for all downstream O2C activities.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("sales_order_form"):
        st.markdown("#### 📋 Enter Sales Order Details")
        c1, c2 = st.columns(2)
        with c1:
            customer   = st.selectbox("Customer Name *", list(CUSTOMERS.keys()))
            material   = st.selectbox("Material / Product *", list(PRODUCTS.keys()))
            quantity   = st.number_input("Quantity *", min_value=1, max_value=500, value=10)
            pay_term   = st.selectbox("Payment Terms *", list(PAYMENT_TERMS.keys()))
        with c2:
            sales_org  = st.selectbox("Sales Organization", ["KIIT_SO01 - India Sales", "KIIT_SO02 - Export"])
            dist_chan  = st.selectbox("Distribution Channel", ["10 - Direct Sales", "20 - Wholesale"])
            division   = st.selectbox("Division", ["01 - Electronics", "02 - Office Supplies"])
            req_date   = st.date_input("Requested Delivery Date", datetime.date.today() + datetime.timedelta(days=7))

        st.markdown("---")
        unit_price = PRODUCTS[material]["price"]
        uom        = PRODUCTS[material]["uom"]
        base_val   = unit_price * quantity
        tax_val    = base_val * TAX_RATE
        net_val    = base_val + tax_val

        st.markdown(f"""
        <div class="sap-card" style="border-left-color:#16a34a">
            <h3>💰 Pricing Preview</h3>
            <table style="width:100%;font-size:14px">
                <tr><td>Unit Price</td><td style="text-align:right"><b>₹{unit_price:,.2f}</b></td></tr>
                <tr><td>Quantity</td><td style="text-align:right"><b>{quantity} {uom}</b></td></tr>
                <tr><td>Base Value</td><td style="text-align:right"><b>₹{base_val:,.2f}</b></td></tr>
                <tr><td>GST (18%)</td><td style="text-align:right"><b>₹{tax_val:,.2f}</b></td></tr>
                <tr style="font-size:16px;color:#003366"><td><b>Net Order Value</b></td><td style="text-align:right"><b>₹{net_val:,.2f}</b></td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        submitted = st.form_submit_button("✅ Create Sales Order (VA01)", use_container_width=True)
        if submitted:
            order = {
                "order_id":      gen_id("SO"),
                "customer":      customer,
                "material":      material,
                "quantity":      quantity,
                "uom":           uom,
                "unit_price":    unit_price,
                "base_value":    base_val,
                "tax_amount":    tax_val,
                "net_value":     net_val,
                "payment_terms": pay_term,
                "sales_org":     sales_org,
                "dist_channel":  dist_chan,
                "division":      division,
                "req_del_date":  req_date.strftime("%d-%m-%Y"),
                "order_date":    today(),
                "status":        "Open",
                "credit_status": "Pending",
            }
            st.session_state.orders.append(order)
            if st.session_state.current_step < 2:
                st.session_state.current_step = 2
            st.success(f"✅ Sales Order **{order['order_id']}** created successfully!")
            st.balloons()

    # Show existing orders
    if st.session_state.orders:
        st.markdown("### 📋 All Sales Orders")
        df = pd.DataFrame(st.session_state.orders)
        st.dataframe(df[["order_id","customer","material","quantity","net_value","status","credit_status","order_date"]],
                     use_container_width=True, hide_index=True)

# ─── STEP 2: CREDIT CHECK ─────────────────────────────────────────────────────
elif page == "✅ Step 2: Credit Check":
    st.markdown("""
    <div class="main-header">
        <h1>✅ Step 2: Credit Check</h1>
        <p>Automatic Credit Verification — SAP Credit Management (FD32)</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sap-card">
        <h3>📖 What is a Credit Check?</h3>
        <p>Before processing a sales order, SAP verifies whether the customer has sufficient <b>credit limit</b>.
        If the order value exceeds the credit limit, the order is <b>blocked</b> and requires approval.
        T-Code <b>FD32</b> is used to manage credit limits. T-Code <b>VKM3</b> is used to release blocked orders.</p>
    </div>
    """, unsafe_allow_html=True)

    pending = [o for o in st.session_state.orders if o["credit_status"] == "Pending"]
    if not pending:
        st.info("No orders pending credit check. Create a Sales Order in Step 1 first.")
    else:
        for order in pending:
            cust_data = CUSTOMERS[order["customer"]]
            credit_limit = cust_data["credit_limit"]
            existing_exposure = sum(
                o["net_value"] for o in st.session_state.orders
                if o["customer"] == order["customer"] and o["credit_status"] == "Approved"
            )
            available_credit = credit_limit - existing_exposure
            order_value = order["net_value"]
            passes = order_value <= available_credit

            status_color = "#d1fae5" if passes else "#fee2e2"
            status_icon  = "✅ APPROVED" if passes else "❌ BLOCKED"
            status_text  = "Credit limit sufficient — order approved." if passes else "Order value exceeds available credit limit. Manual release required."

            st.markdown(f"""
            <div class="sap-card" style="background:{status_color}; border-left-color:{'#16a34a' if passes else '#dc2626'}">
                <h3>Order {order['order_id']} — {order['customer']}</h3>
                <table style="width:100%;font-size:14px">
                    <tr><td>Order Value</td><td style="text-align:right"><b>₹{order_value:,.2f}</b></td></tr>
                    <tr><td>Credit Limit (FD32)</td><td style="text-align:right"><b>₹{credit_limit:,.2f}</b></td></tr>
                    <tr><td>Existing Exposure</td><td style="text-align:right"><b>₹{existing_exposure:,.2f}</b></td></tr>
                    <tr><td>Available Credit</td><td style="text-align:right"><b>₹{available_credit:,.2f}</b></td></tr>
                    <tr style="font-size:16px"><td><b>Credit Decision</b></td><td style="text-align:right"><b>{status_icon}</b></td></tr>
                </table>
                <p style="margin-top:10px">{status_text}</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Approve Order {order['order_id']}", key=f"approve_{order['order_id']}"):
                    for o in st.session_state.orders:
                        if o["order_id"] == order["order_id"]:
                            o["credit_status"] = "Approved"
                            o["status"] = "Confirmed"
                    if st.session_state.current_step < 3:
                        st.session_state.current_step = 3
                    st.success(f"Order {order['order_id']} credit approved!")
                    st.rerun()
            with col2:
                if not passes:
                    if st.button(f"🔓 Release Block (VKM3) {order['order_id']}", key=f"release_{order['order_id']}"):
                        for o in st.session_state.orders:
                            if o["order_id"] == order["order_id"]:
                                o["credit_status"] = "Approved"
                                o["status"] = "Confirmed"
                        st.success(f"Order {order['order_id']} manually released!")
                        st.rerun()

# ─── STEP 3: DELIVERY ─────────────────────────────────────────────────────────
elif page == "🚚 Step 3: Delivery (VL01N)":
    st.markdown("""
    <div class="main-header">
        <h1>🚚 Step 3: Outbound Delivery Creation</h1>
        <p>Transaction Code: <strong>VL01N</strong> — Create Outbound Delivery</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sap-card">
        <h3>📖 What is a Delivery Document?</h3>
        <p>After the credit check passes, SAP creates an <b>Outbound Delivery (OBD)</b> document via T-Code <b>VL01N</b>.
        It specifies the <b>shipping point</b>, <b>route</b>, <b>picking</b>, and <b>packing</b> details.
        The delivery triggers warehouse activities before Goods Issue (GI) is posted.</p>
    </div>
    """, unsafe_allow_html=True)

    approved = [o for o in st.session_state.orders if o["credit_status"] == "Approved"
                and not any(d["order_id"] == o["order_id"] for d in st.session_state.deliveries)]

    if not approved:
        st.info("No approved orders available for delivery. Complete Steps 1 & 2 first.")
    else:
        with st.form("delivery_form"):
            order_sel    = st.selectbox("Select Sales Order", [o["order_id"] for o in approved])
            ship_point   = st.selectbox("Shipping Point", ["SP01 - Delhi Warehouse", "SP02 - Mumbai Hub", "SP03 - Kolkata DC"])
            route        = st.selectbox("Route", ["R001 - Road Express", "R002 - Air Cargo", "R003 - Rail Freight"])
            planned_date = st.date_input("Planned GI Date", datetime.date.today() + datetime.timedelta(days=2))
            picker       = st.text_input("Picker Name", "Warehouse Staff 01")

            if st.form_submit_button("🚚 Create Delivery (VL01N)", use_container_width=True):
                order = next(o for o in st.session_state.orders if o["order_id"] == order_sel)
                delivery = {
                    "delivery_no":    gen_id("DN"),
                    "order_id":       order_sel,
                    "customer":       order["customer"],
                    "material":       order["material"],
                    "quantity":       order["quantity"],
                    "ship_point":     ship_point,
                    "route":          route,
                    "planned_gi":     planned_date.strftime("%d-%m-%Y"),
                    "picker":         picker,
                    "delivery_date":  today(),
                    "status":         "Delivery Created",
                    "gi_status":      "Pending",
                }
                st.session_state.deliveries.append(delivery)
                if st.session_state.current_step < 4:
                    st.session_state.current_step = 4
                st.success(f"✅ Delivery **{delivery['delivery_no']}** created for Order {order_sel}!")
                st.balloons()

    if st.session_state.deliveries:
        st.markdown("### 📋 Delivery Documents")
        df = pd.DataFrame(st.session_state.deliveries)
        st.dataframe(df[["delivery_no","order_id","customer","material","quantity","ship_point","route","gi_status","delivery_date"]],
                     use_container_width=True, hide_index=True)

# ─── STEP 4: GOODS ISSUE ──────────────────────────────────────────────────────
elif page == "📦 Step 4: Goods Issue (VL02N)":
    st.markdown("""
    <div class="main-header">
        <h1>📦 Step 4: Post Goods Issue (PGI)</h1>
        <p>Transaction Code: <strong>VL02N</strong> — Post Goods Issue</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sap-card">
        <h3>📖 What is Post Goods Issue (PGI)?</h3>
        <p><b>Post Goods Issue (PGI)</b> is a critical step where stock ownership transfers from the company to the customer.
        In SAP, T-Code <b>VL02N</b> is used to post GI. It triggers: (1) reduction of stock in inventory (MM),
        (2) cost of goods sold entry in FI/CO, and (3) enables invoice creation in the next step.</p>
    </div>
    """, unsafe_allow_html=True)

    pending_gi = [d for d in st.session_state.deliveries if d["gi_status"] == "Pending"]

    if not pending_gi:
        st.info("No deliveries pending Goods Issue. Complete Step 3 first.")
    else:
        for delivery in pending_gi:
            st.markdown(f"""
            <div class="sap-card">
                <h3>Delivery {delivery['delivery_no']} — {delivery['customer']}</h3>
                <p>Material: <b>{delivery['material']}</b> | Qty: <b>{delivery['quantity']}</b> | Route: {delivery['route']}</p>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                actual_qty  = st.number_input(f"Actual GI Qty ({delivery['delivery_no']})",
                                              min_value=1, max_value=delivery["quantity"],
                                              value=delivery["quantity"], key=f"qty_{delivery['delivery_no']}")
                gi_date     = st.date_input("Goods Issue Date", datetime.date.today(), key=f"date_{delivery['delivery_no']}")
            with c2:
                movement    = st.selectbox("Movement Type", ["601 - GI to Customer", "602 - Return from Customer"],
                                           key=f"mvt_{delivery['delivery_no']}")
                storage_loc = st.selectbox("Storage Location", ["SL01 - Main Store", "SL02 - Dispatch Bay"],
                                           key=f"sl_{delivery['delivery_no']}")

            if st.button(f"📦 Post Goods Issue (VL02N) — {delivery['delivery_no']}", key=f"gi_{delivery['delivery_no']}"):
                for d in st.session_state.deliveries:
                    if d["delivery_no"] == delivery["delivery_no"]:
                        d["gi_status"]     = "GI Posted"
                        d["actual_gi_qty"] = actual_qty
                        d["gi_date"]       = gi_date.strftime("%d-%m-%Y")
                        d["movement_type"] = movement
                        d["storage_loc"]   = storage_loc
                        d["mat_doc"]       = gen_id("MAT")
                if st.session_state.current_step < 5:
                    st.session_state.current_step = 5
                st.success(f"✅ Goods Issue posted for Delivery {delivery['delivery_no']}! Material Document generated.")
                st.rerun()

    if st.session_state.deliveries:
        gi_done = [d for d in st.session_state.deliveries if d["gi_status"] == "GI Posted"]
        if gi_done:
            st.markdown("### ✅ Goods Issue Posted")
            df = pd.DataFrame(gi_done)
            show_cols = [c for c in ["delivery_no","order_id","customer","material","actual_gi_qty","gi_date","mat_doc"] if c in df.columns]
            st.dataframe(df[show_cols], use_container_width=True, hide_index=True)

# ─── STEP 5: INVOICE ──────────────────────────────────────────────────────────
elif page == "🧾 Step 5: Invoice (VF01)":
    st.markdown("""
    <div class="main-header">
        <h1>🧾 Step 5: Invoice / Billing Document</h1>
        <p>Transaction Code: <strong>VF01</strong> — Create Billing Document</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sap-card">
        <h3>📖 What is a Billing Document?</h3>
        <p>After PGI, the invoice is created via T-Code <b>VF01</b>. SAP generates a <b>Billing Document</b>
        which automatically creates an <b>Accounting Document</b> in FI — debiting Accounts Receivable (AR)
        and crediting Revenue. The customer is then sent this invoice for payment.</p>
    </div>
    """, unsafe_allow_html=True)

    gi_posted = [d for d in st.session_state.deliveries if d["gi_status"] == "GI Posted"
                 and not any(i["delivery_no"] == d["delivery_no"] for i in st.session_state.invoices)]

    if not gi_posted:
        st.info("No deliveries with PGI available for invoicing. Complete Step 4 first.")
    else:
        with st.form("invoice_form"):
            del_sel     = st.selectbox("Select Delivery", [d["delivery_no"] for d in gi_posted])
            bill_type   = st.selectbox("Billing Type", ["F2 - Invoice", "F5 - Pro Forma Invoice", "RE - Credit Memo"])
            billing_date = st.date_input("Billing Date", datetime.date.today())

            selected_del = next(d for d in gi_posted if d["delivery_no"] == del_sel)
            order        = next(o for o in st.session_state.orders if o["order_id"] == selected_del["order_id"])
            qty          = selected_del.get("actual_gi_qty", selected_del["quantity"])
            base_val     = order["unit_price"] * qty
            tax_val      = base_val * TAX_RATE
            invoice_amt  = base_val + tax_val
            due_days     = PAYMENT_TERMS[order["payment_terms"]]

            st.markdown(f"""
            <div class="sap-card" style="border-left-color:#7c3aed">
                <h3>🧾 Invoice Preview</h3>
                <table style="width:100%;font-size:14px">
                    <tr><td>Customer</td><td style="text-align:right"><b>{order['customer']}</b></td></tr>
                    <tr><td>Material</td><td style="text-align:right"><b>{order['material']}</b></td></tr>
                    <tr><td>Quantity Billed</td><td style="text-align:right"><b>{qty} {order['uom']}</b></td></tr>
                    <tr><td>Base Amount</td><td style="text-align:right"><b>₹{base_val:,.2f}</b></td></tr>
                    <tr><td>GST (18%)</td><td style="text-align:right"><b>₹{tax_val:,.2f}</b></td></tr>
                    <tr style="font-size:16px;color:#003366"><td><b>Invoice Total</b></td><td style="text-align:right"><b>₹{invoice_amt:,.2f}</b></td></tr>
                    <tr><td>Due Date</td><td style="text-align:right"><b>{future_date(due_days)}</b></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

            if st.form_submit_button("🧾 Create Invoice (VF01)", use_container_width=True):
                invoice = {
                    "invoice_no":      gen_id("INV"),
                    "billing_doc":     gen_id("BL"),
                    "accounting_doc":  gen_id("ACC"),
                    "delivery_no":     del_sel,
                    "order_id":        selected_del["order_id"],
                    "customer":        order["customer"],
                    "material":        order["material"],
                    "quantity":        qty,
                    "base_amount":     base_val,
                    "tax_amount":      tax_val,
                    "invoice_amount":  invoice_amt,
                    "billing_type":    bill_type,
                    "billing_date":    billing_date.strftime("%d-%m-%Y"),
                    "due_date":        future_date(due_days),
                    "status":          "Open",
                }
                st.session_state.invoices.append(invoice)
                if st.session_state.current_step < 6:
                    st.session_state.current_step = 6
                st.success(f"✅ Invoice **{invoice['invoice_no']}** created! Accounting Doc: **{invoice['accounting_doc']}**")
                st.balloons()

    if st.session_state.invoices:
        st.markdown("### 📋 All Invoices")
        df = pd.DataFrame(st.session_state.invoices)
        st.dataframe(df[["invoice_no","customer","material","quantity","invoice_amount","billing_date","due_date","status"]],
                     use_container_width=True, hide_index=True)

# ─── STEP 6: PAYMENT ──────────────────────────────────────────────────────────
elif page == "💰 Step 6: Payment (F-28)":
    st.markdown("""
    <div class="main-header">
        <h1>💰 Step 6: Incoming Payment Processing</h1>
        <p>Transaction Code: <strong>F-28</strong> — Post Incoming Payment</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sap-card">
        <h3>📖 What is Payment Processing in O2C?</h3>
        <p>When the customer pays against an invoice, the accountant uses T-Code <b>F-28</b> to post the
        <b>incoming payment</b>. SAP clears the open AR item, debits the Bank account, and credits
        Accounts Receivable. This completes the O2C cycle — cash has been received!</p>
    </div>
    """, unsafe_allow_html=True)

    open_invoices = [i for i in st.session_state.invoices if i["status"] == "Open"]

    if not open_invoices:
        st.info("No open invoices for payment. Complete Step 5 first.")
    else:
        with st.form("payment_form"):
            inv_sel     = st.selectbox("Select Open Invoice", [i["invoice_no"] for i in open_invoices])
            pay_method  = st.selectbox("Payment Method", ["T - Bank Transfer (NEFT/RTGS)", "C - Cheque", "O - Online Payment"])
            bank_acc    = st.text_input("Customer Bank Account (Last 4 digits)", "4521")
            pay_date    = st.date_input("Payment Date", datetime.date.today())
            reference   = st.text_input("Payment Reference / UTR No.", gen_id("UTR", 10))

            selected_inv = next(i for i in open_invoices if i["invoice_no"] == inv_sel)
            amt_due      = selected_inv["invoice_amount"]
            amt_paid     = st.number_input("Amount Paid (₹)", min_value=0.0, max_value=float(amt_due * 1.1),
                                           value=float(amt_due), step=100.0)
            is_partial   = amt_paid < amt_due

            if st.form_submit_button("💰 Post Payment (F-28)", use_container_width=True):
                payment = {
                    "payment_id":    gen_id("PAY"),
                    "invoice_no":    inv_sel,
                    "customer":      selected_inv["customer"],
                    "amount_due":    amt_due,
                    "amount_paid":   amt_paid,
                    "payment_method":pay_method,
                    "reference":     reference,
                    "payment_date":  pay_date.strftime("%d-%m-%Y"),
                    "status":        "Partial" if is_partial else "Cleared",
                }
                st.session_state.payments.append(payment)

                for i in st.session_state.invoices:
                    if i["invoice_no"] == inv_sel:
                        i["status"] = "Partial Payment" if is_partial else "Cleared"

                if st.session_state.current_step < 7:
                    st.session_state.current_step = 7

                if is_partial:
                    st.warning(f"⚠️ Partial payment of ₹{amt_paid:,.2f} recorded. Outstanding: ₹{amt_due - amt_paid:,.2f}")
                else:
                    st.success(f"✅ Payment **{payment['payment_id']}** posted! Invoice {inv_sel} is now **CLEARED**. 🎉")
                    st.balloons()

    if st.session_state.payments:
        st.markdown("### 💰 Payment Ledger")
        df = pd.DataFrame(st.session_state.payments)
        st.dataframe(df[["payment_id","invoice_no","customer","amount_due","amount_paid","payment_method","reference","payment_date","status"]],
                     use_container_width=True, hide_index=True)

# ─── STEP 7: REPORTS ──────────────────────────────────────────────────────────
elif page == "📊 Step 7: Reports & Ledger":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Step 7: Reports & AR Ledger</h1>
        <p>T-Codes: <strong>VA05</strong> (Order List) | <strong>VF05</strong> (Billing List) | <strong>FBL5N</strong> (AR Ledger)</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Order Summary", "🧾 Invoice Report", "💰 AR Ledger (FBL5N)", "📈 Analytics"])

    with tab1:
        st.markdown("#### 📋 Sales Order List (VA05)")
        if st.session_state.orders:
            df = pd.DataFrame(st.session_state.orders)
            df["net_value"] = df["net_value"].apply(lambda x: f"₹{x:,.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv = pd.DataFrame(st.session_state.orders).to_csv(index=False)
            st.download_button("⬇️ Download Orders CSV", csv, "sales_orders.csv", "text/csv")
        else:
            st.info("No orders yet.")

    with tab2:
        st.markdown("#### 🧾 Billing Document List (VF05)")
        if st.session_state.invoices:
            df = pd.DataFrame(st.session_state.invoices)
            df["invoice_amount"] = df["invoice_amount"].apply(lambda x: f"₹{x:,.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv = pd.DataFrame(st.session_state.invoices).to_csv(index=False)
            st.download_button("⬇️ Download Invoices CSV", csv, "invoices.csv", "text/csv")
        else:
            st.info("No invoices yet.")

    with tab3:
        st.markdown("#### 💰 Customer AR Ledger (FBL5N)")
        if st.session_state.invoices:
            rows = []
            for inv in st.session_state.invoices:
                paid = sum(p["amount_paid"] for p in st.session_state.payments if p["invoice_no"] == inv["invoice_no"])
                outstanding = inv["invoice_amount"] - paid
                rows.append({
                    "Invoice No":    inv["invoice_no"],
                    "Customer":      inv["customer"],
                    "Invoice Amt":   f"₹{inv['invoice_amount']:,.2f}",
                    "Paid":          f"₹{paid:,.2f}",
                    "Outstanding":   f"₹{outstanding:,.2f}",
                    "Due Date":      inv["due_date"],
                    "Status":        inv["status"],
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            total_inv  = sum(i["invoice_amount"] for i in st.session_state.invoices)
            total_paid = sum(p["amount_paid"] for p in st.session_state.payments)
            total_out  = total_inv - total_paid
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Invoiced",    f"₹{total_inv:,.2f}")
            c2.metric("Total Collected",   f"₹{total_paid:,.2f}")
            c3.metric("Total Outstanding", f"₹{total_out:,.2f}")
        else:
            st.info("No invoice data yet.")

    with tab4:
        st.markdown("#### 📈 O2C Analytics")
        if st.session_state.orders:
            # Customer-wise order value
            df_orders = pd.DataFrame(st.session_state.orders)
            cust_summary = df_orders.groupby("customer")["net_value"].sum().reset_index()
            cust_summary.columns = ["Customer", "Total Order Value (₹)"]
            st.markdown("**Customer-wise Order Value**")
            st.bar_chart(cust_summary.set_index("Customer"))

            st.markdown("**Material-wise Order Quantity**")
            mat_summary = df_orders.groupby("material")["quantity"].sum().reset_index()
            mat_summary.columns = ["Material", "Total Qty"]
            st.bar_chart(mat_summary.set_index("Material"))
        else:
            st.info("Create some orders to see analytics.")

    # O2C Completion Timeline
    st.markdown("---")
    st.markdown("### 🏁 O2C Cycle Completion Status")
    progress_steps = [
        ("Sales Order", len(st.session_state.orders) > 0),
        ("Credit Check", any(o["credit_status"] == "Approved" for o in st.session_state.orders)),
        ("Delivery", len(st.session_state.deliveries) > 0),
        ("Goods Issue", any(d["gi_status"] == "GI Posted" for d in st.session_state.deliveries)),
        ("Invoice", len(st.session_state.invoices) > 0),
        ("Payment", len(st.session_state.payments) > 0),
    ]
    cols = st.columns(6)
    for col, (step, done) in zip(cols, progress_steps):
        with col:
            icon = "✅" if done else "⏳"
            bg   = "#d1fae5" if done else "#f3f4f6"
            st.markdown(f"""
            <div style="background:{bg};border-radius:8px;padding:14px;text-align:center">
                <div style="font-size:24px">{icon}</div>
                <div style="font-size:12px;font-weight:600;margin-top:6px">{step}</div>
            </div>""", unsafe_allow_html=True)

    completed = sum(1 for _, done in progress_steps if done)
    st.progress(completed / 6, text=f"O2C Cycle: {completed}/6 steps completed")
