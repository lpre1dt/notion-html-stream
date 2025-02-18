import streamlit as st
import pandas as pd

# Sample DataFrame
data = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35]
})

st.write("### DataFrame with Buttons")

# Create buttons next to each row
for index, row in data.iterrows():
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        st.write(f"{row['Name']} (Age: {row['Age']})")
    with col2:
        if st.button(f"Click Me {index}", key=f"btn_{index}"):
            st.success(f"You clicked on {row['Name']}'s button!")
    with col3:
        if st.button(f"Delete {index}", key=f"del_{index}"):
            st.warning(f"{row['Name']} would be deleted (not implemented)")

# Display the original DataFrame for context
st.dataframe(data)
