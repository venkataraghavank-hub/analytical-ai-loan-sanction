# Loan Sanction Explorer

An AI Applications Lab Streamlit application for exploring how a logistic-regression model converts hypothetical applicant and loan characteristics into a predicted sanction probability.

> **Educational AI classroom prototype:** This application demonstrates statistical decision support. Its output is not an actual lending decision and must not be used to evaluate a real applicant.

## Features

- Secure classroom access using Streamlit Secrets
- Inputs for applicant location, accommodation, employment and obligation categories
- Inputs for loan-to-value ratio, fixed-obligation-to-income ratio, down payment and bank savings
- Logistic-regression probability calculated from embedded fitted coefficients
- Comparison against a 77% decision threshold
- Model-ready input values and interpretable model equation
- Consistent AI Applications Lab interface and website back-link

## Repository structure

```text
.
├── streamlit_app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example
```

The application does not load a serialized model or use a `models` folder. The fitted logistic-regression coefficients and the decision threshold are implemented directly in `streamlit_app.py`.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

For local development, create `.streamlit/secrets.toml` and configure the class access code. Do not commit that file to GitHub.

## Deploy on Streamlit Community Cloud

1. Connect the GitHub repository to Streamlit Community Cloud.
2. Select the `main` branch and `streamlit_app.py` entry point.
3. Select Python 3.12 in Advanced settings.
4. Add the class-code secret in Streamlit **App settings → Secrets**:

```toml
STUDENT_ACCESS_CODE = "your-private-class-code"
```

Set the real value only in Streamlit Secrets. Do not store or publish it in GitHub.

## Model logic

The application calculates the logistic-regression score using these model variables:

- `Tier_1`
- `Tier_2`
- `AccoClass`
- `Etype`
- `eom_25`
- `LTV`
- `mfoir_p`
- `dwnp_prop_p`
- `banksave_s`

The score is transformed into a probability using the logistic function:

```text
Probability = 1 / (1 + exp(-Logit score))
```

The application returns **Likely Sanction** when the predicted probability is at least `0.77`; otherwise, it returns **Likely Rejection**.

## Responsible use

The probability reflects statistical associations in historical teaching data. It is not a guarantee of sanction or rejection. A production lending system would require appropriate validation, fairness assessment, governance, regulatory review and human decision-making.

