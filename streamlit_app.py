import hmac
import math
import streamlit as st


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Loan Sanction Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DECISION_THRESHOLD = 0.77


# ---------------------------------------------------------
# ACCESS CONTROL
# ---------------------------------------------------------

def check_access():
    if st.session_state.get("authenticated", False):
        return True

    st.title("AI Applications Lab")
    st.subheader("Student Lab Access")

    st.write(
        "Enter the class access code to open the "
        "Loan Sanction Explorer."
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
            correct_code = str(
                st.secrets["STUDENT_ACCESS_CODE"]
            ).strip()
        except KeyError:
            st.error(
                "The class access code has not been configured "
                "in Streamlit Secrets."
            )
            st.stop()

        if hmac.compare_digest(
            entered_code.strip(),
            correct_code,
        ):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect class code. Please try again.")

    return False


if not check_access():
    st.stop()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

header_left, header_right = st.columns([5, 1])

with header_left:
    st.title("Loan Sanction Explorer")

    st.write(
        "Explore how a logistic-regression model converts "
        "applicant and loan characteristics into a predicted "
        "sanction probability."
    )

with header_right:
    if st.button(
        "Exit Lab",
        use_container_width=True,
    ):
        st.session_state["authenticated"] = False
        st.rerun()


st.info(
    "This is an educational decision-support application. "
    "Its output is not an actual lending decision."
)


# ---------------------------------------------------------
# STUDENT INPUT FORM
# ---------------------------------------------------------

st.subheader("Applicant and Loan Information")

with st.form("prediction_form"):

    column_1, column_2, column_3 = st.columns(3)

    with column_1:

        location_tier = st.selectbox(
            "Customer location tier",
            options=[
                "Tier 1",
                "Tier 2",
                "Tier 3",
            ],
            index=0,
            help=(
                "Tier 3 is the reference category in the "
                "logistic-regression model."
            ),
        )

        accommodation_category = st.selectbox(
            "Accommodation category",
            options=[
                "Reference category — coded 0",
                "Category coded 1",
            ],
            index=0,
        )

        employment_category = st.selectbox(
            "Employment category",
            options=[
                "Reference category — coded 0",
                "Category coded 1",
            ],
            index=0,
        )

    with column_2:

        obligation_category = st.selectbox(
            "Existing-obligation category",
            options=[
                "Reference category — coded 0",
                "Category coded 1",
            ],
            index=0,
        )

        ltv = st.number_input(
            "Loan-to-value ratio (%)",
            min_value=0.0,
            max_value=250.0,
            value=57.0,
            step=1.0,
            help=(
                "Loan amount expressed as a percentage of "
                "the assessed property value."
            ),
        )

        mfoir = st.number_input(
            "Modified fixed-obligation-to-income ratio (%)",
            min_value=0.0,
            max_value=300.0,
            value=71.0,
            step=1.0,
            help=(
                "Fixed financial obligations relative to "
                "the applicant's income."
            ),
        )

    with column_3:

        down_payment = st.number_input(
            "Down-payment proportion (%)",
            min_value=0.0,
            max_value=100.0,
            value=33.33,
            step=1.0,
        )

        bank_savings = st.number_input(
            "Bank savings measure",
            min_value=0.0,
            max_value=300.0,
            value=5.0,
            step=0.5,
            help=(
                "Enter the value using the scaled unit "
                "employed in the teaching dataset."
            ),
        )

    run_model = st.form_submit_button(
        "Run Loan Sanction Model",
        type="primary",
        use_container_width=True,
    )


# ---------------------------------------------------------
# LOGISTIC-REGRESSION PREDICTION
# ---------------------------------------------------------

if run_model:

    # Convert location tier into dummy variables.
    if location_tier == "Tier 1":
        tier_1 = 1.0
        tier_2 = 0.0

    elif location_tier == "Tier 2":
        tier_1 = 0.0
        tier_2 = 1.0

    else:
        tier_1 = 0.0
        tier_2 = 0.0

    accommodation_code = (
        1.0
        if accommodation_category == "Category coded 1"
        else 0.0
    )

    employment_code = (
        1.0
        if employment_category == "Category coded 1"
        else 0.0
    )

    obligation_code = (
        1.0
        if obligation_category == "Category coded 1"
        else 0.0
    )

    # Logistic-regression equation obtained from model_2.
    score = (
        6.722057
        + 0.548073 * tier_1
        + 0.692575 * tier_2
        + 0.592230 * accommodation_code
        - 0.486777 * employment_code
        - 0.557610 * obligation_code
        - 0.070967 * float(ltv)
        + 0.016011 * float(mfoir)
        - 0.064725 * float(down_payment)
        + 0.054671 * float(bank_savings)
    )

    # Convert the logit score into a probability.
    probability = 1.0 / (1.0 + math.exp(-score))

    if probability >= DECISION_THRESHOLD:
        recommendation = "Likely Sanction"
    else:
        recommendation = "Likely Rejection"

    # -----------------------------------------------------
    # DISPLAY OUTPUT
    # -----------------------------------------------------

    st.divider()
    st.subheader("Model Output")

    result_1, result_2, result_3 = st.columns(3)

    with result_1:
        st.metric(
            "Recommendation",
            recommendation,
        )

    with result_2:
        st.metric(
            "Predicted sanction probability",
            f"{probability:.1%}",
        )

    with result_3:
        st.metric(
            "Decision threshold",
            f"{DECISION_THRESHOLD:.0%}",
        )

    if probability >= DECISION_THRESHOLD:
        st.success(
            "The predicted sanction probability meets or "
            "exceeds the selected decision threshold."
        )

    else:
        probability_gap = (
            DECISION_THRESHOLD - probability
        )

        st.warning(
            "The predicted sanction probability is "
            f"{probability_gap:.1%} below the selected "
            "decision threshold."
        )

    st.progress(
        min(max(probability, 0.0), 1.0),
        text=(
            f"Predicted sanction probability: "
            f"{probability:.1%}"
        ),
    )

    with st.expander("View the model-ready input values"):

        st.json(
            {
                "Tier_1": tier_1,
                "Tier_2": tier_2,
                "AccoClass": accommodation_code,
                "Etype": employment_code,
                "eom_25": obligation_code,
                "LTV": float(ltv),
                "mfoir_p": float(mfoir),
                "dwnp_prop_p": float(down_payment),
                "banksave_s": float(bank_savings),
            }
        )

    with st.expander("How should this result be interpreted?"):

        st.write(
            "The probability is estimated from historical "
            "observations using logistic regression. It "
            "represents a statistical association, not a "
            "guarantee of sanction or rejection."
        )

        st.write(
            "The 77% threshold was selected during model "
            "validation. Changing this threshold would alter "
            "the number of predicted sanctions, rejections, "
            "false positives and false negatives."
        )

    with st.expander("View the logistic-regression equation"):

        st.code(
            """
Logit score =
6.722057
+ 0.548073 × Tier_1
+ 0.692575 × Tier_2
+ 0.592230 × AccoClass
- 0.486777 × Etype
- 0.557610 × eom_25
- 0.070967 × LTV
+ 0.016011 × mfoir_p
- 0.064725 × dwnp_prop_p
+ 0.054671 × banksave_s

Probability = 1 / (1 + exp(-Logit score))
            """,
            language="text",
        )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "AI Applications Lab · Analytical AI · "
    "Logistic Regression Demonstration"
)
