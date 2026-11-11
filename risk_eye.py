
import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime

# ==========================================
# 1. إعدادات المشروع
# ==========================================

st.set_page_config(
    page_title="عين الخطر | RiskEye",
    page_icon="🛡️",
    layout="wide"
)

APP_NAME = "عين الخطر"
DATA_FILE = "risk_eye_data.csv"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "riskeye2026"

COLUMNS = [
    "id", "project", "risk", "category",
    "probability", "impact", "score",
    "days", "status", "created"
]

# ==========================================
# 2. تصميم الواجهة
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #101827;
    color: white;
}
[data-testid="stSidebar"] {
    background-color: #17243a;
}
h1, h2, h3, p, label {
    color: white !important;
}
.stButton button {
    border-radius: 10px;
    font-weight: bold;
    min-height: 40px;
}
div[data-testid="stMetric"] {
    background-color: #1c2b42;
    padding: 14px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. تحميل البيانات وحفظها
# ==========================================

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=COLUMNS)

    try:
        df = pd.read_csv(DATA_FILE)

        for column in COLUMNS:
            if column not in df.columns:
                df[column] = None

        df = df[COLUMNS]

        for column in ["probability", "impact", "score", "days"]:
            df[column] = pd.to_numeric(
                df[column], errors="coerce"
            ).fillna(0)

        return df

    except Exception:
        return pd.DataFrame(columns=COLUMNS)


def save_data(df):
    df.to_csv(
        DATA_FILE,
        index=False,
        encoding="utf-8-sig"
    )


if "risks" not in st.session_state:
    st.session_state.risks = load_data()


# ==========================================
# 4. تسجيل الدخول
# ==========================================

if "access" not in st.session_state:
    st.session_state.access = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None


def login_user(role, username):
    st.session_state.access = True
    st.session_state.role = role
    st.session_state.username = username
    st.rerun()


# ==========================================
# 5. شاشة البداية
# ==========================================

if not st.session_state.access:

    st.title("🛡️ عين الخطر")
    st.subheader("RiskEye")

    st.markdown("""
    ### اكتشف الخطر قبل وقوعه!

    منصة لتحليل المخاطر وتسجيل الأخطاء،
    وقياس تأثيرها، واقتراح طرق الوقاية منها.
    """)

    tab1, tab2 = st.tabs([
        "👤 دخول كضيف",
        "🔐 دخول المدير"
    ])

    with tab1:

        st.write("استكشف المنصة بوضع المشاهدة.")

        if st.button("الدخول كضيف", use_container_width=True):
            login_user("guest", "Guest")

    with tab2:

        username = st.text_input("اسم المستخدم")
        password = st.text_input(
            "كلمة المرور",
            type="password"
        )

        if st.button("تسجيل الدخول", use_container_width=True):

            if (
                username == ADMIN_USERNAME
                and password == ADMIN_PASSWORD
            ):
                login_user("admin", username)
            else:
                st.error("بيانات الدخول غير صحيحة.")

    st.stop()


# ==========================================
# 6. القائمة الجانبية
# ==========================================

st.sidebar.title("🛡️ عين الخطر")
st.sidebar.caption("RiskEye")

st.sidebar.write(
    "المستخدم: " + str(st.session_state.username)
)

if st.session_state.role == "admin":
    st.sidebar.success("المدير")
else:
    st.sidebar.info("ضيف - وضع المشاهدة")

pages = [
    "🏠 الرئيسية",
    "🔍 تحليل خطر جديد",
    "📋 سجل المخاطر",
    "📊 الإحصائيات",
    "💡 مستشار الحلول",
    "ℹ️ عن المشروع"
]

page = st.sidebar.radio("القائمة الرئيسية", pages)

if st.sidebar.button("🚪 تسجيل الخروج"):

    st.session_state.access = False
    st.session_state.role = None
    st.session_state.username = None
    st.rerun()


# ==========================================
# 7. الرئيسية
# ==========================================

if page == "🏠 الرئيسية":

    st.title("🛡️ عين الخطر | RiskEye")

    st.write(
        "نظام يساعدك على اكتشاف المخاطر "
        "وتحليلها ومتابعة معالجتها."
    )

    df = st.session_state.risks

    total = len(df)

    if total:
        high = int((df["score"] >= 15).sum())
        medium = int(
            ((df["score"] >= 8) & (df["score"] < 15)).sum()
        )
        low = int((df["score"] < 8).sum())
        resolved = int((df["status"] == "تم الحل").sum())
    else:
        high = medium = low = resolved = 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("إجمالي المخاطر", total)
    c2.metric("مخاطر مرتفعة", high)
    c3.metric("مخاطر متوسطة", medium)
    c4.metric("تم حلها", resolved)

    st.divider()

    st.subheader("📌 أحدث المخاطر")

    if total:
        st.dataframe(
            df.tail(10).iloc[::-1],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("لا توجد مخاطر مسجلة حتى الآن.")

    st.success(
        "هدف عين الخطر: اكتشاف المشكلة قبل أن تتفاقم."
    )


# ==========================================
# 8. تحليل خطر جديد
# ==========================================

elif page == "🔍 تحليل خطر جديد":

    st.title("🔍 تحليل خطر جديد")

    st.write("أدخل البيانات لتقدير مستوى الخطورة.")

    with st.form("risk_form"):

        project = st.text_input("📌 اسم المشروع")

        risk = st.text_area("⚠️ وصف الخطر")

        category = st.selectbox(
            "📂 تصنيف الخطر",
            [
                "تقني",
                "مالي",
                "إداري",
                "تعليمي",
                "أمني",
                "صحي",
                "بيئي",
                "أخرى"
            ]
        )

        col1, col2 = st.columns(2)

        with col1:
            probability = st.slider(
                "احتمالية الحدوث",
                1, 5, 3
            )

        with col2:
            impact = st.slider(
                "حجم التأثير",
                1, 5, 3
            )

        days = st.number_input(
            "الأيام المتبقية للمعالجة",
            min_value=1,
            max_value=365,
            value=30
        )

        submitted = st.form_submit_button(
            "💾 تحليل وحفظ الخطر",
            use_container_width=True
        )

    score = probability * impact

    st.subheader("🎯 نتيجة التحليل")

    st.metric("درجة الخطورة", f"{score}/25")

    if score >= 15:
        st.error("🔴 خطر مرتفع")
    elif score >= 8:
        st.warning("🟠 خطر متوسط")
    else:
        st.success("🟢 خطر منخفض")

    if submitted:

        if not project.strip() or not risk.strip():
            st.error("أدخل اسم المشروع ووصف الخطر.")

        elif st.session_state.role != "admin":
            st.warning("الحفظ متاح للمدير فقط.")

        else:

            new_risk = pd.DataFrame([{
                "id": str(uuid.uuid4())[:8],
                "project": project.strip(),
                "risk": risk.strip(),
                "category": category,
                "probability": probability,
                "impact": impact,
                "score": score,
                "days": days,
                "status": "مفتوح",
                "created": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            }])

            updated = pd.concat(
                [st.session_state.risks, new_risk],
                ignore_index=True
            )

            st.session_state.risks = updated
            save_data(updated)

            st.success("تم حفظ الخطر بنجاح!")


# ==========================================
# 9. سجل المخاطر
# ==========================================

elif page == "📋 سجل المخاطر":

    st.title("📋 سجل المخاطر")

    df = st.session_state.risks.copy()

    if df.empty:
        st.info("لا توجد مخاطر مسجلة.")

    else:

        search = st.text_input("🔎 ابحث عن خطر")

        if search.strip():
            mask = (
                df["project"].astype(str).str.contains(
                    search, case=False, na=False
                )
                |
                df["risk"].astype(str).str.contains(
                    search, case=False, na=False
                )
            )
            df = df[mask]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ تنزيل السجل",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="risk_eye_report.csv",
            mime="text/csv"
        )

        if st.session_state.role == "admin" and not df.empty:

            st.divider()
            st.subheader("تحديث حالة الخطر")

            selected_id = st.selectbox(
                "اختر الخطر",
                df["id"].tolist()
            )

            new_status = st.selectbox(
                "الحالة",
                ["مفتوح", "قيد المعالجة", "تم الحل"]
            )

            if st.button("حفظ الحالة"):

                original = st.session_state.risks

                original.loc[
                    original["id"] == selected_id,
                    "status"
                ] = new_status

                st.session_state.risks = original
                save_data(original)

                st.success("تم تحديث الحالة.")
                st.rerun()

            st.divider()
            st.subheader("حذف خطر")

            delete_id = st.selectbox(
                "اختر الخطر للحذف",
                df["id"].tolist(),
                key="delete_id"
            )

            confirm = st.checkbox(
                "أؤكد حذف هذا الخطر."
            )

            if st.button("🗑️ حذف الخطر"):

                if confirm:

                    original = st.session_state.risks

                    updated = original[
                        original["id"] != delete_id
                    ].copy()

                    st.session_state.risks = updated
                    save_data(updated)

                    st.success("تم الحذف.")
                    st.rerun()

                else:
                    st.warning("أكد الحذف أولًا.")


# ==========================================
# 10. الإحصائيات
# ==========================================

elif page == "📊 الإحصائيات":

    st.title("📊 إحصائيات عين الخطر")

    df = st.session_state.risks

    if df.empty:

        st.info("سجّل خطرًا لعرض الإحصائيات.")

    else:

        levels = pd.DataFrame({
            "المستوى": ["مرتفع", "متوسط", "منخفض"],
            "العدد": [
                int((df["score"] >= 15).sum()),
                int(
                    (
                        (df["score"] >= 8)
                        & (df["score"] < 15)
                    ).sum()
                ),
                int((df["score"] < 8).sum())
            ]
        })

        st.subheader("توزيع المخاطر")
        st.bar_chart(levels.set_index("المستوى"))

        st.subheader("المخاطر حسب التصنيف")

        categories = (
            df["category"]
            .value_counts()
            .rename_axis("التصنيف")
            .to_frame("العدد")
        )

        st.bar_chart(categories)

        st.subheader("حالة المخاطر")

        statuses = (
            df["status"]
            .value_counts()
            .rename_axis("الحالة")
            .to_frame("العدد")
        )

        st.bar_chart(statuses)


# ==========================================
# 11. مستشار الحلول
# ==========================================

elif page == "💡 مستشار الحلول":

    st.title("💡 مستشار الحلول")

    st.write(
        "اختر نوع الخطر للحصول على اقتراحات وقائية."
    )

    solutions = {
        "تقني": [
            "اختبر النظام قبل إطلاقه.",
            "احتفظ بنسخة احتياطية.",
            "حدّث البرامج بانتظام.",
            "ضع خطة بديلة للأعطال."
        ],
        "مالي": [
            "ضع ميزانية احتياطية.",
            "راقب المصروفات.",
            "راجع الالتزامات المالية.",
            "قارن التكاليف بالخطة."
        ],
        "إداري": [
            "حدد مسؤولية كل عضو.",
            "تابع تقدم العمل.",
            "وثّق القرارات.",
            "ضع خطة للطوارئ."
        ],
        "تعليمي": [
            "حدد أهداف التعلم.",
            "اختبر النتائج بانتظام.",
            "استخدم مصادر موثوقة.",
            "راجع الأخطاء السابقة."
        ],
        "أمني": [
            "استخدم كلمات مرور قوية.",
            "حدّث أنظمة الحماية.",
            "حدد صلاحيات المستخدمين.",
            "احتفظ بنسخ احتياطية."
        ],
        "صحي": [
            "اعتمد على مصادر صحية موثوقة.",
            "لا تتجاهل علامات الخطر.",
            "استشر مختصًا عند الحاجة."
        ],
        "بيئي": [
            "راقب مصادر التلوث.",
            "ضع خطة للطوارئ البيئية.",
            "قلل الهدر.",
            "تابع إجراءات السلامة."
        ],
        "أخرى": [
            "حدد السبب الأساسي.",
            "قيّم احتمالية الحدوث.",
            "قدّر حجم التأثير.",
            "ضع خطة للوقاية."
        ]
    }

    choice = st.selectbox(
        "نوع الخطر",
        list(solutions.keys())
    )

    if st.button("🔍 اقترح الحلول"):

        st.subheader("🛡️ الحلول المقترحة")

        for solution in solutions[choice]:
            st.success("✓ " + solution)

    st.caption(
        "المستشار يعتمد على قواعد ثابتة، "
        "وليس على اتصال مباشر بذكاء اصطناعي خارجي."
    )


# ==========================================
# 12. عن المشروع
# ==========================================

elif page == "ℹ️ عن المشروع":

    st.title("🛡️ عين الخطر")
    st.subheader("RiskEye")

    st.markdown("""
    ### فكرة المشروع

    منصة لتحليل المخاطر والأخطاء،
    وتسجيلها، ومتابعة معالجتها.

    ### المميزات

    1. تحليل المخاطر.
    2. تصنيف الأخطاء.
    3. حساب درجة الخطورة.
    4. سجل للمخاطر.
    5. إحصائيات ورسوم بيانية.
    6. مستشار للحلول الوقائية.
    7. تصدير التقارير.

    ### طريقة حساب الخطورة

    درجة الخطورة = احتمالية الحدوث × حجم التأثير

    - 1 إلى 7: منخفض.
    - 8 إلى 14: متوسط.
    - 15 إلى 25: مرتفع.

    ### تنبيه

    هذا نموذج أولي تعليمي.
    النتائج تقديرية ولا تضمن التنبؤ بالمستقبل.
    """)

    st.success(
        "عين الخطر — اكتشف الخطر قبل وقوعه."
    )


# ==========================================
# 13. تذييل القائمة
# ==========================================

st.sidebar.divider()
st.sidebar.caption("🛡️ RiskEye | عين الخطر")
