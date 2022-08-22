import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

st.set_page_config(page_title="OI Stats List", page_icon="", layout="wide")

if 'counter' not in st.session_state:
    st.session_state.counter = 1

st.header("")

uploaded_file = st.file_uploader("Upload Files",type=['csv'])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    df_fut = df.loc[(df['INSTRUMENT']=="FUTSTK")]
    df_opt = df.loc[(df['INSTRUMENT']=="OPTSTK")]

    df_fut = df_fut[['SYMBOL', 'EXPIRY_DT', 'CLOSE']]
    df_opt = df_opt[['SYMBOL', 'EXPIRY_DT', 'STRIKE_PR', 'OPTION_TYP', 'CHG_IN_OI']]

    exp = st.sidebar.selectbox(
            'Expiry DATE',
            df_fut['EXPIRY_DT'].unique())
    
    df_opt = df_opt.loc[(df['EXPIRY_DT']==exp)]

    all_strikes = st.sidebar.checkbox('Show All Strikes', False)

    df_fut = df_fut.loc[((df_fut['EXPIRY_DT']==exp))]
    df_fut_sym = df_fut['SYMBOL'].to_list()

    len = len(df_fut_sym) - 1
    sym_per_page = 50
    len2 = round(len / sym_per_page)

    st.sidebar.write("")
    col5, col6 = st.sidebar.columns([1,1])
    with col5:
        if st.button("Prev. Page"):
            if st.session_state.counter >= 2:
                st.session_state.counter -= 1
    with col6:     
        if st.button("Next Page"):
            if st.session_state.counter < len2:
                st.session_state.counter += 1

    # st.sidebar.write("len: " + str(len))
    # st.sidebar.write("len2: " + str(len2))

    page_no = st.session_state.counter
    # st.sidebar.write("page_no: " + str(page_no))

    x1 = sym_per_page * (page_no - 1)
    if (x1 + sym_per_page - 1) > len:
        x2 = len
    else:
        x2 = x1 + sym_per_page - 1

    # st.sidebar.write(str(x1) + " to " + str(x2))
    
    # df_fut_sym_list = df_fut_sym[x1:x2]

    for x in range(x1, x2 + 1):

        sym = df_fut_sym[x]
        df_opt_sym = df_opt[(df_opt['SYMBOL'] == sym)]
        df_opt_sym.reset_index(inplace = True, drop=True)
        opt_strikes = df_opt_sym['STRIKE_PR'].unique().tolist()

        fut_price = df_fut.loc[(df_fut['SYMBOL'] == sym) & (df_fut['EXPIRY_DT'] == exp), 'CLOSE'].values[0]

        atm_strike_index = df_opt_sym.iloc[(df_opt_sym['STRIKE_PR']-fut_price).abs().argsort()[:2]].index.tolist()
        atm_strike_index.sort(reverse=True)
        len = df_opt_sym.shape[0] - 1
        atm_strike = df_opt_sym['STRIKE_PR'][atm_strike_index[0]]
        
        chg_in_ce = df_opt_sym[((df_opt_sym['OPTION_TYP']=='CE') & (df_opt_sym['STRIKE_PR']==atm_strike))]['CHG_IN_OI'].values
        chg_in_pe = df_opt_sym[((df_opt_sym['OPTION_TYP']=='PE') & (df_opt_sym['STRIKE_PR']==atm_strike))]['CHG_IN_OI'].values

        tot_chg_in_oi_ce = df_opt_sym[df_opt_sym['OPTION_TYP']=="CE"]['CHG_IN_OI'].sum()
        tot_chg_in_oi_pe = df_opt_sym[df_opt_sym['OPTION_TYP']=="PE"]['CHG_IN_OI'].sum()

        plot_graph = True
        st.write(sym + " - Change in OI")

        if plot_graph:
            if atm_strike_index[1] > 10:
                ce_x = atm_strike_index[1] - 10
                pe_x = atm_strike_index[0] - 10
            else:
                ce_x = 0
                pe_x = atm_strike_index[0] - atm_strike_index[1]

            if (atm_strike_index[0] + 10) > len:
                ce_y = atm_strike_index[1] + (len - atm_strike_index[0])
                pe_y = len
            else:
                ce_y = atm_strike_index[1] + 10
                pe_y = atm_strike_index[0] + 10

            try:
                df_opt_final = df_opt_sym if all_strikes else df_opt_sym.iloc[np.r_[ce_x:ce_y,pe_x:pe_y]]
            except:
                'Error plotting graph'

        
            tot_coi = {'TYPE': ['CE', 'PE'],
                    'OI': [df_opt_sym[df_opt_sym['OPTION_TYP']=="CE"]['CHG_IN_OI'].sum(), df_opt_sym[df_opt_sym['OPTION_TYP']=="PE"]['CHG_IN_OI'].sum()],
                    '' : ['','']
                }

            tot_coi_chart = px.bar(
                    tot_coi, 
                    x='',
                    y='OI',
                    labels={
                        "CPE": "",
                        "OI": ""
                        },
                    barmode='group',
                    color='TYPE',
                    color_discrete_map={
                        'CE': 'green',
                        'PE': 'red'
                    },
                    height=600,
                    width=0,
                    title=""
                )

            tot_coi_chart.update_layout(showlegend=False, margin_l=0, margin_r=0)
            tot_coi_chart.update_layout(hovermode='x unified', font=dict(
                size=16
            ),    title={
                'text': " ",
                'y':1,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
            tot_coi_chart.update_traces(hovertemplate = '')

            coi_chart = px.bar(
                    df_opt_final, 
                    x='STRIKE_PR',
                    y='CHG_IN_OI',
                    labels={
                        "STRIKE_PR": "",
                        "CHG_IN_OI": ""
                        },
                    barmode='group',
                    color='OPTION_TYP',
                    color_discrete_map={
                        'CE': 'green',
                        'PE': 'red'
                    },
                    height=600,
                    width=0,
                    title=""
                )

            coi_chart.update_layout(showlegend=False, margin_l=0, margin_r=0)
            coi_chart.add_vline(atm_strike, line_width=1, line_dash="dash", line_color="black", annotation_text="Future Price: "+ str(fut_price), annotation_position="top")
            coi_chart.update_layout(hovermode='x unified', font=dict(
                size=16
            ))
            coi_chart.update_traces(hovertemplate = '')
            col3, col4 = st.columns([1,10], gap="small")
            with col3:
                st.plotly_chart(tot_coi_chart, config = {'displayModeBar': False}, use_container_width=True)
            with col4:
                st.plotly_chart(coi_chart, config = {'displayModeBar': False}, use_container_width=True)
    
    st.sidebar.write(f"Page {st.session_state.counter} of {len2}")

components.html(
    f"""
        <p>{st.session_state.counter}</p>
        <script>
            window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
    """,
    height=0
)



