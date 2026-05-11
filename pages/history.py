import streamlit as st
import APi.AssetsAPi as api
import pandas as pd
st.set_page_config(page_title="Asset History", layout="wide")
st.title("📜 Asset History")

    # Get response from Laravel
response = api.get_assets()
    
    # 1. Handle the structure: Laravel likely sends {"message": "...", "data": [...]}
asset_list = []
if isinstance(response, dict):
    asset_list = response.get('data', []) # Use .get() to avoid KeyError
elif isinstance(response, list):
        asset_list = response

if asset_list:
        # 2. Create DataFrame
        df = pd.DataFrame(asset_list)
        
        # 3. Define the columns we want to show
        target_cols = ['id', 'ip_address', 'mac_address', 'hostname', 'vendor', 'last_seen']
        
        # 4. Filter only columns that actually exist in the DB response
        available_cols = [c for c in target_cols if c in df.columns]
        
        if available_cols:
            display_df = df[available_cols]
            # use st.dataframe for an interactive, searchable table
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("Data found, but columns do not match. Showing raw data instead.")
            st.write(df)
else:
        st.info("No assets found in the database. Run a scan to populate the records!")