import hmac
from pathlib import Path

import pandas as pd
import statsmodels.api as sm
import streamlit as st


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Credit Sanction Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MODEL_PATH = Path("models/credit_sanction_model.pkl")
THRESHOLD = 0.77


# ---------------------------------------------------------
# ACCESS CONTROL
# ---------------------------------------------------------

def check_access():
    """Display access screen until the correct class code is entered."""

    if st.session_state.get("authenticated", False):
        return True

    st.title("AI Applications Lab")
    st.subheader("Student Lab Access")

    st.write(
        "Enter the class access code to open the "
        "Credit Sanction Explorer."
    )

    with st.form("access_form"):
        entered_code = st.text_input(
            "Class access code",
            type="password",
            placeholder="Enter the code provided in class",
        )

        submitted = st.form_submit_button(
            "Enter Application",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        try:
            correct_code = st.secrets["STUDENT_ACCESS_CODE"]
        except KeyError:
            st.error(
                "The access code has not been configured. "
                "Please contact the instructor."
            )
            st.stop()

        if hmac.compare_digest(
            entered_code.strip(),
            str(correct_code).strip(),
        ):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect class code. Please try again.")

    return False


if not check_access():
    st.stop()


# ---------------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------------

@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}"
        )

    return sm.load(MODEL_PATH)


try:
    model = load_model()
except Exception as error:
    st.error("The prediction model could not be loaded.")
    st.exception(error)
    st.stop()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

top_left, top_right = st.columns([5, 1])

with top_left:
    st.title("Credit Sanction Explorer")
    st.write(
        "Explore how a logistic-regression model converts applicant "
        "and loan characteristics into a predicted sanction probability."
    )

with top_right:
    if st.button("Exit Lab", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()


st.info(
    "This is an educational decision-support application. "
    "Its output is not an actual lending decision."
)


# ---------------------------------------------------------
# INPUT FORM
# ---------------------------------------------------------

st.subheader("Applicant and Loan Information")

with st.form("prediction_form"):

    col1, col2, col3 = st.columns(3)

    with col1:
        location_tier = st.selectbox(
            "Customer location tier",
            ["Tier 1", "Tier 2", "Tier 3"],
            help=(
                "Tier 3 is the reference category used by the model."
            ),
        )

        accommodation_class = st.selectbox(
            "Accommodation category",
            [
                "Reference category — coded 0",
                "Category coded 1",
            ],
        )

        employment_type = st.selectbox(
            "Employment category",
            [
                "Reference category — coded 0",
                "Category coded 1",
            ],
        )

    with col2:
        obligation_category = st.selectbox(
            "Existing-obligation category",
            [
                "Reference category — coded 0",
                "Category coded 1",
            ],
        )

        ltv = st.number_input(
            "Loan-to-value ratio (%)",
            min_value=0.0,
            max_value=250.0,
            value=70.0,
            step=1.0,
            help=(
                "Loan amount as a percentage of the property's "
                "assessed value."
            ),
        )

        mfoir = st.number_input(
            "Modified fixed-obligation-to-income ratio (%)",
            min_value=0.0,
            max_value=300.0,
            value=40.0,
            step=1.0,
            help=(
                "The applicant's fixed financial obligations "
                "relative to income."
            ),
        )

    with col3:
        down_payment = st.number_input(
            "Down-payment proportion (%)",
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=1.0,
        )

        bank_savings = st.number_input(
            "Bank savings measure",
            min_value=0.0,
            max_value=300.0,
            value=5.0,
            step=0.5,
            help=(
                "Enter the value using the same scaled unit employed "
                "in the case dataset."
            ),
        )

    run_model = st.form_submit_button(
        "Run Credit Sanction Model",
        type="primary",
        use_container_width=True,
    )


# ---------------------------------------------------------
# PREDICTION
# ---------------------------------------------------------

if run_model:

    if location_tier == "Tier 1":
        tier_1, tier_2 = 1.0, 0.0
    elif location_tier == "Tier 2":
        tier_1, tier_2 = 0.0, 1.0
    else:
        tier_1, tier_2 = 0.0, 0.0

    input_data = pd.DataFrame(
        [{
            "const": 1.0,
            "Tier_1": tier_1,
            "Tier_2": tier_2,
            "AccoClass": (
                1.0 if accommodation_class == "Category coded 1"
                else 0.0
            ),
            "Etype": (
                1.0 if employment_type == "Category coded 1"
                else 0.0
            ),
            "eom_25": (
                1.0 if obligation_category == "Category coded 1"
                else 0.0
            ),
            "LTV": float(ltv),
            "mfoir_p": float(mfoir),
            "dwnp_prop_p": float(down_payment),
            "banksave_s": float(bank_savings),
        }]
    )

    # Enforce exactly the same column order used during training.
    model_columns = list(model.params.index)
    input_data = input_data.reindex(
        columns=model_columns,
        fill_value=0.0,
    )

    probability = float(model.predict(input_data).iloc[0])
    recommendation = (
        "Likely Sanction"
        if probability >= THRESHOLD
        else "Likely Rejection"
    )

    st.divider()
    st.subheader("Model Output")

    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:
        st.metric(
            "Recommendation",
            recommendation,
        )

    with result_col2:
        st.metric(
            "Predicted sanction probability",
            f"{probability:.1%}",
        )

    with result_col3:
        st.metric(
            "Decision threshold",
            f"{THRESHOLD:.0%}",
        )

    if probability >= THRESHOLD:
        st.success(
            "The predicted sanction probability meets or exceeds "
            "the model's selected decision threshold."
        )
    else:
        gap = THRESHOLD - probability

        st.warning(
            "The predicted sanction probability is "
            f"{gap:.1%} below the selected decision threshold."
        )

    st.progress(
        min(max(probability, 0.0), 1.0),
        text=f"Predicted probability: {probability:.1%}",
    )

    with st.expander("View the model-ready input record"):
        st.dataframe(
            input_data,
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("How should this result be interpreted?"):
        st.write(
            "The probability is estimated from historical observations "
            "using logistic regression. It represents a statistical "
            "association, not a guarantee of sanction or rejection."
        )

        st.write(
            "The 77% threshold was selected during model validation. "
            "Changing the threshold would change the number of predicted "
            "sanctions, rejections, false positives and false negatives."
        )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "AI Applications Lab · Analytical AI · "
    "Logistic Regression Demonstration"
)
