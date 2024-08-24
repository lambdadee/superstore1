import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Practice", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: Super Store EDA Dashboard")
st.markdown("<style>div.block-container{padding-top: 2rem;}</style>", unsafe_allow_html=True)

df = pd.read_csv("data/Sample - Superstore.csv", encoding="latin1")

col1, col2 = st.columns((2))

df["Order Date"] = pd.to_datetime(df["Order Date"])

startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >=date1) & (df["Order Date"]<= date2)].copy()

st.sidebar.header("Choose Filter: ")

region = st.sidebar.multiselect("Select Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Select State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

city = st.sidebar.multiselect("Select City", df3["City"].unique())

if not region and not state and not city:
    filtered_df = df
elif not state and city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and city:
    filtered_df = df[df["State"].isin(state)]
elif region and city:
    filtered_df = df3[(df3["Region"].isin(region)) & (df3["City"].isin(city))]
elif state and city:
    filtered_df = df3[(df3["State"].isin(state)) & (df3["City"].isin(city))]
elif region and state:
    filtered_df = df3[(df3["Region"].isin(region)) & (df3["State"].isin(state))]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[(df3["Region"].isin(region)) & (df3["State"].isin(state)) & (df3["City"].isin(city))]

category_df = filtered_df.groupby(by = "Category", as_index= False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=["${:,.2f}".format(x) for x in category_df["Sales"]], template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region wise Sales")
    fig1 = px.pie(filtered_df, values= "Sales", names= "Category", hole=0.5)
    fig1.update_traces(text = filtered_df["Sales"], textposition = "outside")
    st.plotly_chart(fig1, use_container_width=True)

region_df = filtered_df.groupby(by = ["Region"], as_index = False)["Sales"].sum()

with col1:
    with st.expander("View Category Dataset"):
        st.write(category_df.style.background_gradient(cmap="magma_r"))
        csv =category_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="txt/csv", help="Click here to download category dataset as csv file")

with col2:
    with st.expander("View Region Dataset"):
        st.write(region_df.style.background_gradient(cmap="Greens"))
        csv = region_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="txt/csv", help="Click here to download region data as csv file")

filtered_df["Month_Year"] = filtered_df["Order Date"].dt.to_period("M")

st.subheader("Time Series Analysis")
linechart_df = pd.DataFrame(filtered_df.groupby(filtered_df["Month_Year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart_df, x= "Month_Year", y="Sales", labels= {"Sales":"Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View TimeSeries Data"):
    st.write(linechart_df.T.style.background_gradient(cmap="Oranges_r"))
    csv = linechart_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Data", data=csv, file_name="TimeSeries.csv", mime="txt/csv", help="Click here to download timeseries data as csv file")

st.subheader("Hierarchical View of Sales Using Treemap")
fig4 = px.treemap(filtered_df, path= ["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"],
                  color="Sub-Category")
fig4.update_layout(width = 800, height= 650)
st.plotly_chart(fig4, use_container_width=True)

chart1, chart2 = st.columns((2))

with chart1:
    st.subheader("Category Wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", hole=0.4)
    fig.update_traces(text=filtered_df["Sales"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Region Wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.4)
    fig.update_traces(text=filtered_df["Sales"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff

st.subheader(":point_right: Month Wise Sub-Category Sales Summary")
with st.expander("Summary Table"):
    sample_df = df[0:30][["Region", "City", "Category", "Sales", "Profit", "Quantity"]]
    Table1 = ff.create_table(sample_df, colorscale="Cividis")
    st.plotly_chart(Table1, use_container_width=True)

with st.expander("Month Wise Sub-Category Table"):
    filtered_df["Month"] = filtered_df["Order Date"].dt.month_name()
    Table2 = pd.pivot_table(data=filtered_df,values= "Sales",index= ["Sub-Category"], columns="Month")
    st.write(Table2.style.background_gradient(cmap="magma_r"))  

data1 = px.scatter(filtered_df, x = "Sales", y = "Profit", size = "Quantity")
data1["layout"].update(title = "Relationship between Sales and Profit using Scatter Plot.",
                          titlefont = dict(size =20), xaxis = dict(title="Sale", titlefont = dict(size=19)),
                          yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap = "YlGnBu"))


csv = df.to_csv(index = False).encode('utf-8')
st.download_button("Download Data", data = csv, file_name = "Data.csv", mime = "text/csv")