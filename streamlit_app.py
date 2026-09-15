import hmac
import math
import os

import streamlit as st

st.set_page_config(page_title="Loan Sanction Explorer", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

APP_TITLE="Loan Sanction Explorer"; APP_AREA="ANALYTICAL AI · FINTECH & RISK ANALYTICS"; APP_SUBTITLE="Explore how applicant and loan characteristics translate into a sanction probability."; DECISION_THRESHOLD=0.77

st.markdown("""
<style>
:root{--navy:#123b70;--teal:#19a7a8;--ink:#17324d;--muted:#647f9d;--line:#dbe7f3}.stApp{background:#f3f9ff;color:var(--ink)}.block-container{max-width:1380px;padding:1.35rem 2.2rem 2rem}header[data-testid="stHeader"]{background:transparent}#MainMenu,footer{visibility:hidden}
.hero{padding:.35rem .4rem 1rem}.eyebrow{font-size:.76rem;font-weight:800;letter-spacing:.16em;color:#2670b8}.hero h1{font-size:clamp(2rem,3vw,2.8rem);line-height:1.05;color:#082b61;letter-spacing:-.035em;margin:.4rem 0}.hero p{font-size:1.03rem;color:#587596;margin:0}.notice{margin:.1rem .4rem 1rem;padding:.7rem .95rem;border-left:4px solid #2670b8;border-radius:8px;background:#eaf4ff;color:#365d82;font-size:.88rem}.notice strong{color:#123b70}
.access{text-align:center;padding:.4rem 0 .8rem}.access h1{font-size:2rem;color:#082b61;margin:.3rem 0}.access p{color:#65809d}.access-note{text-align:center;color:#7890a8;font-size:.78rem;margin-top:.75rem}[data-testid="stVerticalBlockBorderWrapper"]{background:rgba(255,255,255,.97);border:1px solid #dce8f4!important;border-radius:18px!important;box-shadow:0 10px 30px rgba(18,59,112,.07)}
.section-title{font-size:1.32rem;font-weight:800;color:#092f66}.section-copy{color:#65809d;margin:.15rem 0 .9rem}.result-card{padding:1rem;border-radius:14px;background:#eefafc;border:1px solid #d8f0f1}.decision{font-size:1.6rem;font-weight:850;color:#087f89}.footer{border-top:1px solid #dbe7f3;margin-top:1.5rem;padding-top:1rem;color:#6d849b;font-size:.82rem}div.stButton>button[kind="primary"]{background:#13a4aa;border:0;border-radius:10px;min-height:3rem;font-weight:750}div.stButton>button[kind="primary"]:hover{background:#0b9299;border:0}@media(max-width:800px){.block-container{padding:1rem}}
</style>""",unsafe_allow_html=True)

def require_access():
    if st.session_state.get("class_access_granted",False): return
    expected=st.secrets.get("STUDENT_ACCESS_CODE",os.getenv("STUDENT_ACCESS_CODE","")); _,gate,_=st.columns([1,1.15,1])
    with gate:
        with st.container(border=True):
            st.markdown(f'<div class="access"><div class="eyebrow">AI APPLICATIONS LAB</div><h1>Student Lab Access</h1><p>Enter the class access code to open the {APP_TITLE}.</p></div>',unsafe_allow_html=True)
            entered=st.text_input("Class access code",type="password",placeholder="Enter the code provided in class")
            if st.button("Enter Application",type="primary",use_container_width=True):
                if expected and hmac.compare_digest(entered,expected): st.session_state["class_access_granted"]=True; st.rerun()
                st.error("Incorrect class code. Please try again.")
            if not expected: st.warning("Class access has not been configured by the application owner.")
            st.markdown('<div class="access-note">Access is restricted to classroom participants.</div>',unsafe_allow_html=True)
    st.stop()

def header():
    title,controls=st.columns([5,2])
    with title: st.markdown(f'<div class="hero"><div class="eyebrow">{APP_AREA}</div><h1>{APP_TITLE}</h1><p>{APP_SUBTITLE}</p></div>',unsafe_allow_html=True)
    with controls:
        st.link_button("← Back to AI Applications Lab","https://aiapplicationslab.in",use_container_width=True)
        if st.button("Exit Lab",use_container_width=True): st.session_state["class_access_granted"]=False; st.rerun()
    st.markdown('<div class="notice"><strong>Educational AI classroom prototype:</strong> This application demonstrates statistical decision support. Its output is not an actual lending decision and must not be used to evaluate a real applicant.</div>',unsafe_allow_html=True)

require_access(); header()
left,right=st.columns([5,8],gap="large")
with left:
    with st.container(border=True):
        st.markdown('<div class="section-title">Applicant &amp; loan inputs</div><div class="section-copy">Configure a hypothetical case using the teaching dataset variables.</div>',unsafe_allow_html=True)
        with st.form("prediction_form"):
            location_tier=st.selectbox("Customer location tier",["Tier 1","Tier 2","Tier 3"],help="Tier 3 is the reference category.")
            accommodation_category=st.selectbox("Accommodation category",["Reference category — coded 0","Category coded 1"])
            employment_category=st.selectbox("Employment category",["Reference category — coded 0","Category coded 1"])
            obligation_category=st.selectbox("Existing-obligation category",["Reference category — coded 0","Category coded 1"])
            ltv=st.number_input("Loan-to-value ratio (%)",0.0,250.0,57.0,1.0)
            mfoir=st.number_input("Modified fixed-obligation-to-income ratio (%)",0.0,300.0,71.0,1.0)
            down_payment=st.number_input("Down-payment proportion (%)",0.0,100.0,33.33,1.0)
            bank_savings=st.number_input("Bank savings measure",0.0,300.0,5.0,0.5,help="Use the scaled unit employed in the teaching dataset.")
            run_model=st.form_submit_button("Run model",type="primary",use_container_width=True)

with right:
    with st.container(border=True):
        st.markdown('<div class="section-title">AI model insight</div><div class="section-copy">Review the classification, probability, threshold and model-ready inputs.</div>',unsafe_allow_html=True)
        if not run_model:
            st.info("Configure a hypothetical applicant and select **Run model** to generate the result.")
        else:
            tier_1,tier_2=(1.0,0.0) if location_tier=="Tier 1" else ((0.0,1.0) if location_tier=="Tier 2" else (0.0,0.0))
            accommodation_code=1.0 if accommodation_category=="Category coded 1" else 0.0; employment_code=1.0 if employment_category=="Category coded 1" else 0.0; obligation_code=1.0 if obligation_category=="Category coded 1" else 0.0
            score=6.722057+0.548073*tier_1+0.692575*tier_2+0.592230*accommodation_code-0.486777*employment_code-0.557610*obligation_code-0.070967*float(ltv)+0.016011*float(mfoir)-0.064725*float(down_payment)+0.054671*float(bank_savings)
            probability=1.0/(1.0+math.exp(-score)); recommendation="Likely Sanction" if probability>=DECISION_THRESHOLD else "Likely Rejection"
            st.markdown(f'<div class="result-card"><div>Model recommendation</div><div class="decision">{recommendation}</div></div>',unsafe_allow_html=True)
            a,b=st.columns(2); a.metric("Sanction probability",f"{probability:.1%}"); b.metric("Decision threshold",f"{DECISION_THRESHOLD:.0%}")
            st.progress(min(max(probability,0.0),1.0),text=f"Predicted sanction probability: {probability:.1%}")
            if probability>=DECISION_THRESHOLD: st.success("The predicted probability meets or exceeds the decision threshold.")
            else: st.warning(f"The predicted probability is {DECISION_THRESHOLD-probability:.1%} below the decision threshold.")
            with st.expander("Model-ready input values"):
                st.json({"Tier_1":tier_1,"Tier_2":tier_2,"AccoClass":accommodation_code,"Etype":employment_code,"eom_25":obligation_code,"LTV":float(ltv),"mfoir_p":float(mfoir),"dwnp_prop_p":float(down_payment),"banksave_s":float(bank_savings)})
            with st.expander("How should this result be interpreted?"):
                st.write("The probability is estimated from historical observations using logistic regression. It represents a statistical association, not a guarantee of sanction or rejection.")
                st.write("The 77% threshold was selected during model validation. Changing it changes predicted sanctions, rejections, false positives and false negatives.")
            with st.expander("Logistic-regression equation"):
                st.code("""Logit score = 6.722057 + 0.548073 × Tier_1 + 0.692575 × Tier_2 + 0.592230 × AccoClass - 0.486777 × Etype - 0.557610 × eom_25 - 0.070967 × LTV + 0.016011 × mfoir_p - 0.064725 × dwnp_prop_p + 0.054671 × banksave_s
Probability = 1 / (1 + exp(-Logit score))""",language="text")
st.markdown('<div class="footer">AI Applications Lab · Analytical AI · Guided classroom learning</div>',unsafe_allow_html=True)

