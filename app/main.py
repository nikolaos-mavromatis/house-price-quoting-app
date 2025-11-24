"""Streamlit application for house price prediction."""

from babel.numbers import format_currency
import requests

import streamlit as st


main, help_tab = st.tabs(["Main", "Help"])

with main:
    st.title("House Price Prediction App")
    st.write(
        "The form below will be used to generate your quote. Fill in as accurately as you can."
    )

    with st.form("house_characteristics", enter_to_submit=False):
        st.header("House Characteristics")

        col1, col2 = st.columns(2, gap="small")

        with col1:
            build_year_val = st.number_input(
                "Build Year",
                value=None,
                step=1,
                help="The year the house was originally built",
            )
            qual_val = st.slider(
                "Overall Quality",
                min_value=1,
                max_value=10,
                value=5,
                step=1,
                help="Select the quality of the materials (1=Poor, 10=Excellent).",
            )
            remodeled_year_val = st.number_input(
                "Remodeled Year",
                value=None,
                step=1,
                help="Leave empty if the house has not been remodeled.",
            )

        with col2:
            area_val = st.number_input(
                "Living Area (in Sq.Ft.)",
                value=None,
                help="Total lot area in square feet",
            )
            cond_val = st.slider(
                "Overall Condition",
                min_value=1,
                max_value=10,
                value=5,
                step=1,
                help="Select the condition of the house (1=Poor, 10=Excellent).",
            )

        # Every form must have a submit button
        _, col, _ = st.columns(3)
        with col:
            submitted = st.form_submit_button("Quote me now!", use_container_width=True)

        if submitted:
            # Validate inputs
            if not all([area_val, build_year_val]):
                st.error(
                    "Please fill in all required fields (Living Area and Build Year)"
                )
            else:
                # Collect all form inputs to pass into the API call
                params = {
                    "LotArea": area_val,
                    "YearBuilt": build_year_val,
                    "YearRemodAdd": remodeled_year_val
                    if remodeled_year_val
                    else build_year_val,
                    "OverallQual": qual_val,
                    "OverallCond": cond_val,
                }

                try:
                    with st.spinner("Calculating your house price..."):
                        response = requests.get(
                            url="http://api:8000/quote/",
                            params=params,
                            timeout=10,
                        )
                        response.raise_for_status()

                        # Parse response
                        result = response.json()

                        # Handle both old format (float) and new format (dict)
                        if isinstance(result, dict):
                            quote = result.get("predicted_price", result)
                        else:
                            quote = result

                        quote_in_dollars = format_currency(quote, "USD", locale="en_US")

                        st.divider()
                        st.success("Prediction complete!")
                        st.subheader(
                            f"The value of your house is estimated at :blue[**{quote_in_dollars}**]"
                        )

                        # Show additional details if available
                        if isinstance(result, dict) and "input_features" in result:
                            with st.expander("View input details"):
                                st.json(result["input_features"])

                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error(
                        "Could not connect to the prediction service. Please ensure the API is running."
                    )
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

with help_tab:
    st.header("About This App")
    st.write("""
    This application uses machine learning to predict house prices based on various characteristics.

    **How it works:**
    1. Enter your house characteristics in the form
    2. Click "Quote me now!" to get a price prediction
    3. The app sends your data to our API service
    4. The API processes the data through our trained model
    5. You receive an estimated house price

    **Features used for prediction:**
    - Lot Area (square feet)
    - Year Built
    - Year Remodeled
    - Overall Quality (1-10)
    - Overall Condition (1-10)

    **Technical Architecture:**
    - Frontend: Streamlit (this app)
    - API: FastAPI service
    - Model: Ridge Regression with feature engineering
    - Deployment: Docker containers
    """)

    st.subheader("Need Help?")
    st.write("""
    - Make sure all required fields are filled
    - Ensure the Year Built is valid
    - If Remodeled Year is empty, the original build year will be used
    - Quality and Condition ratings range from 1 (Poor) to 10 (Excellent)
    """)
