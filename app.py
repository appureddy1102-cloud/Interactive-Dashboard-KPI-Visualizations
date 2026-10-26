from pathlib import Path
import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from src.data_processing import load_data
from src.kpi_calculations import calculate_kpis

st.set_page_config(page_title="Retail Intelligence | Executive Dashboard", page_icon="📊", layout="wide")
PALETTE={"navy":"#102A43","blue":"#2563EB","teal":"#0F766E","muted":"#627D98","bg":"#F4F7FB","orange":"#D97706"}
st.markdown(f"""<style>
.stApp {{ background:{PALETTE['bg']}; }} .block-container {{padding-top:1.25rem;max-width:1500px;}}
[data-testid="stMetric"] {{background:white;border:1px solid #E5EAF0;padding:16px 18px;border-radius:12px;box-shadow:0 2px 6px #102a4310;}}
[data-testid="stMetricLabel"] p {{color:{PALETTE['muted']};font-weight:600;}} h1,h2,h3 {{color:{PALETTE['navy']};}}
</style>""",unsafe_allow_html=True)

@st.cache_data(show_spinner="Loading and validating the sample dataset…")
def get_data(): return load_data()

def money(v): return "—" if pd.isna(v) else f"${v:,.0f}"
def pct(v): return "—" if pd.isna(v) else f"{v:.1%}"

def make_pdf(d, k, title="Interactive Dashboard & KPI Visualizations"):
    buf=io.BytesIO(); doc=SimpleDocTemplate(buf,pagesize=letter,rightMargin=42,leftMargin=42,topMargin=36,bottomMargin=36)
    styles=getSampleStyleSheet(); story=[Paragraph(title,styles['Title']),Paragraph("Executive snapshot · Sample Superstore educational dataset",styles['Heading2']),Spacer(1,8)]
    story.append(Paragraph(f"Filtered period: {d['Order Date'].min():%Y-%m-%d} to {d['Order Date'].max():%Y-%m-%d} · {len(d):,} order lines",styles['BodyText']))
    story.append(Spacer(1,12))
    rows=[["KPI","Value","Definition"] , ["Revenue",money(k['revenue']),"Sum of sales for selected records"], ["AOV",money(k['aov']),"Revenue / unique order IDs"], ["Orders",f"{k['orders']:,}","Unique order IDs"], ["Customers",f"{k['customers']:,}","Unique customer IDs"], ["Revenue growth",pct(k['growth']),"Change vs immediately preceding equal-length date window"], ["Average discount",pct(k['discount']),"Mean line-item discount"], ["CAC / churn","Unavailable","Dataset lacks acquisition spend/flags and defined active-customer status"]]
    t=Table(rows,colWidths=[95,90,335]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(PALETTE['navy'])),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#D7E0EA')),('BACKGROUND',(0,1),(-1,-1),colors.white),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTSIZE',(0,0),(-1,-1),8),('PADDING',(0,0),(-1,-1),6)])); story.extend([t,Spacer(1,12)])
    def image_chart(df,kind):
        import matplotlib.pyplot as plt
        f,ax=plt.subplots(figsize=(7.1,2.7)); f.patch.set_facecolor('white')
        if kind=='trend':
            m=df.groupby('Order Month').Revenue.sum(); ax.fill_between(m.index,m.values,color='#93C5FD',alpha=.5); ax.plot(m.index,m.values,color=PALETTE['blue'],lw=2); ax.set_title('Monthly revenue'); ax.tick_params(axis='x',rotation=30)
        elif kind=='geo':
            g=df.groupby('Region').Revenue.sum().sort_values(); ax.barh(g.index,g.values,color='#0F766E'); ax.set_title('Revenue by region')
        elif kind=='category':
            g=df.groupby('Category').Revenue.sum().sort_values(); ax.barh(g.index,g.values,color='#2563EB'); ax.set_title('Revenue by category')
        else:
            g=df.groupby('Segment').Revenue.sum().sort_values(); ax.barh(g.index,g.values,color='#D97706'); ax.set_title('Revenue by segment')
        ax.set_xlabel('USD'); ax.grid(axis='x',alpha=.2); f.tight_layout(); out=io.BytesIO(); f.savefig(out,format='png',dpi=120); plt.close(f); out.seek(0); return out
    for kind in ['trend','geo','category','segment']:
        story.append(Image(image_chart(d,kind),width=505,height=192)); story.append(Spacer(1,6))
    story.extend([Paragraph("Key observations",styles['Heading2'])])
    if len(d):
        cat=d.groupby('Category').Revenue.sum(); reg=d.groupby('Region').Revenue.sum(); seg=d.groupby('Segment').Revenue.sum()
        items=[f"Revenue is {money(k['revenue'])} across {k['orders']:,} orders and {k['customers']:,} distinct customers.",f"Largest revenue category: {cat.idxmax()} ({money(cat.max())}); leading segment: {seg.idxmax()}.",f"Largest revenue region: {reg.idxmax()} ({money(reg.max())}).", "CAC, churn, channel and marketing-efficiency metrics are unavailable: the source contains no marketing cost/acquisition markers, channel, or explicit customer-status data.", "Recommendation: use this as a baseline performance view; pair it with marketing cost and customer lifecycle data before making acquisition or retention investment decisions."]
        for x in items: story.append(Paragraph("• "+x,styles['BodyText'])); story.append(Spacer(1,4))
    story.append(Spacer(1,8)); story.append(Paragraph("Metric definitions & limitations: Revenue is the sum of line-item Sales; profit is reported source Profit (not computed); AOV uses unique order IDs. Growth compares the selected period with an equal-length previous period. Sample Superstore is fictional instructional data and not real company performance. Country is US only. Line-item aggregation and mix effects can shape results. Churn is not estimated; a transaction extract alone does not provide a sufficiently defined active-customer population or censoring rule.",styles['Italic']))
    doc.build(story); buf.seek(0); return buf.getvalue()

st.title("📊 Retail Intelligence")
st.caption("Interactive Dashboard & KPI Visualizations · Sample Superstore · Educational sample data, not actual company results")
try: df,audit=get_data()
except Exception as e:
    st.error(f"Could not load the source dataset: {e}"); st.stop()
min_date=df['Order Date'].min().date(); max_date=df['Order Date'].max().date()
with st.sidebar:
    st.header("Explore the data")
    if st.button("↺ Reset filters",width="stretch"): st.session_state.clear(); st.rerun()
    dates=st.date_input("Order date range",value=(min_date,max_date),min_value=min_date,max_value=max_date)
    date_start,date_end=(dates if isinstance(dates,tuple) and len(dates)==2 else (min_date,max_date))
    countries=sorted(df.Country.dropna().unique()); country_sel=st.multiselect("Country",countries,default=countries)
    regions=sorted(df.Region.dropna().unique()); region_sel=st.multiselect("Region",regions,default=regions)
    cats=sorted(df.Category.dropna().unique()); cat_sel=st.multiselect("Product category",cats,default=cats)
    segments=sorted(df.Segment.dropna().unique()); seg_sel=st.multiselect("Customer segment",segments,default=segments)
    st.caption("Sales/acquisition channel filter unavailable: channel is not recorded in the source.")
    grain=st.selectbox("Trend drill-down",["Month","Quarter","Year"],index=0)
    st.divider(); st.caption(f"Validated {audit['rows']:,} rows · {min_date} – {max_date}")
mask=(df['Order Date'].dt.date>=date_start)&(df['Order Date'].dt.date<=date_end)&df.Country.isin(country_sel)&df.Region.isin(region_sel)&df.Category.isin(cat_sel)&df.Segment.isin(seg_sel)
f=df.loc[mask].copy()
if f.empty:
    st.warning("No records match the selected filters. Adjust or reset your selections."); st.stop()
# Growth compare is based on same geography/category/segment selections, preceding duration.
duration=max((pd.Timestamp(date_end)-pd.Timestamp(date_start)).days+1,1)
prior_start=pd.Timestamp(date_start)-pd.Timedelta(days=duration); prior_end=pd.Timestamp(date_start)-pd.Timedelta(days=1)
prior=df[(df['Order Date']>=prior_start)&(df['Order Date']<=prior_end)&df.Country.isin(country_sel)&df.Region.isin(region_sel)&df.Category.isin(cat_sel)&df.Segment.isin(seg_sel)]
k=calculate_kpis(f,prior)
cols=st.columns(4)
metrics=[("Total Revenue",money(k['revenue']),"Sum of revenue under current filters"),("Customer Acquisition Cost","Unavailable","No marketing spend or new-customer flag in source"),("Churn Rate","Unavailable","No defined active-customer/status history"),("Average Order Value",money(k['aov']),"Filtered revenue ÷ unique orders")]
for c,(label,val,helptext) in zip(cols,metrics): c.metric(label,val,help=helptext)
cols=st.columns(4)
for c,(label,val,helptext) in zip(cols,[("Total Orders",f"{k['orders']:,}","Distinct Order IDs"),("Unique Customers",f"{k['customers']:,}","Distinct Customer IDs"),("Revenue Growth",pct(k['growth']),"Vs previous equal-length date interval"),("Average Discount",pct(k['discount']),"Mean discount across filtered lines")]): c.metric(label,val,help=helptext)
with st.expander("KPI definitions & data limitations"):
 st.markdown("**Revenue:** sum of Sales. **AOV:** revenue / unique Order ID. **CAC:** unavailable without acquisition spend and newly acquired-customer identifiers; no proxy is shown. **Churn:** unavailable because this transaction sample has no explicit customer activity/status definition. **Growth:** filtered revenue vs the immediately preceding interval of equal duration. **Discount:** mean line-item discount. Dataset has source Profit; no profit estimates are invented. No marketing, channel or product return data.")
st.markdown("### Revenue & geographic performance")
left,right=st.columns([1.55,1])
with left:
 if grain=="Month": f['_period']=f['Order Month'].dt.strftime('%Y-%m')
 elif grain=="Quarter": f['_period']=f['Order Date'].dt.to_period('Q').astype(str)
 else: f['_period']=f['Order Date'].dt.year.astype(str)
 tr=f.groupby('_period',as_index=False).agg(Revenue=('Revenue','sum'),Profit=('Profit','sum'))
 fig=go.Figure(); fig.add_trace(go.Scatter(x=tr._period,y=tr.Revenue,mode='lines+markers',name='Revenue',fill='tozeroy',line=dict(color=PALETTE['blue'],width=3),hovertemplate='%{x}<br>Revenue $%{y:,.0f}<extra></extra>')); fig.add_trace(go.Scatter(x=tr._period,y=tr.Profit,mode='lines+markers',name='Profit (source)',line=dict(color=PALETTE['orange'],width=2),yaxis='y2',hovertemplate='%{x}<br>Profit $%{y:,.0f}<extra></extra>')); fig.update_layout(title=f"Revenue and profit by {grain.lower()}",xaxis_title=grain,yaxis_title="Revenue (USD)",yaxis2=dict(title="Profit (USD)",overlaying='y',side='right'),hovermode='x unified',legend=dict(orientation='h',y=1.1),margin=dict(l=10,r=15,t=55,b=10)); st.plotly_chart(fig,width="stretch")
with right:
 geo=f.pivot_table(index='Region',columns='Category',values='Revenue',aggfunc='sum',fill_value=0)
 fig=px.imshow(geo,text_auto='.2s',aspect='auto',color_continuous_scale='Teal',labels=dict(x='Product category',y='US region',color='Revenue (USD)'),title="Geographic revenue heatmap · region × category"); fig.update_layout(margin=dict(l=5,r=5,t=45,b=5)); st.plotly_chart(fig,width="stretch")
st.markdown("### Product, customer and efficiency mix")
c1,c2=st.columns(2)
with c1:
 cat=f.groupby('Category',as_index=False).agg(Revenue=('Revenue','sum'),Profit=('Profit','sum')); fig=px.bar(cat,x='Revenue',y='Category',orientation='h',color='Profit',color_continuous_scale='Tealgrn',hover_data={'Revenue':':$,.0f','Profit':':$,.0f'},title="Revenue by product category (color = source profit)"); fig.update_layout(margin=dict(l=5,r=5,t=45,b=5)); st.plotly_chart(fig,width="stretch")
with c2:
 sg=f.groupby('Segment',as_index=False).agg(Revenue=('Revenue','sum'),Orders=('Order ID','nunique'),Customers=('Customer ID','nunique')); fig=px.bar(sg,x='Segment',y='Revenue',color='Segment',hover_data={'Revenue':':$,.0f','Orders':True,'Customers':True},title="Revenue by customer segment"); fig.update_layout(showlegend=False,margin=dict(l=5,r=5,t=45,b=5)); st.plotly_chart(fig,width="stretch")
c3,c4=st.columns(2)
with c3:
 m=f.groupby('Order Month',as_index=False).agg(AOV=('Revenue',lambda x:x.sum()/f.loc[x.index,'Order ID'].nunique()),Customers=('Customer ID','nunique'),Revenue=('Revenue','sum')); fig=px.line(m,x='Order Month',y='AOV',markers=True,title="Monthly average order value",hover_data={'AOV':':$,.2f','Customers':True}); st.plotly_chart(fig,width="stretch")
 m['Revenue Growth']=m.Revenue.pct_change(); fig=px.bar(m,x='Order Month',y='Revenue Growth',title='Month-over-month revenue growth',hover_data={'Revenue Growth':':.1%'}); fig.add_hline(y=0,line_color='#64748B'); st.plotly_chart(fig,width="stretch")
with c4:
 state=f.groupby('State',as_index=False).agg(Revenue=('Revenue','sum'),Profit=('Profit','sum')); fig=px.treemap(state,path=['State'],values='Revenue',color='Profit',color_continuous_scale='RdYlGn',title="US state performance · region filter applies",hover_data={'Revenue':':$,.0f','Profit':':$,.0f'}); st.plotly_chart(fig,width="stretch")
st.info("Marketing acquisition and efficiency visuals are omitted: marketing spend and new-customer attribution are not present. Sales-channel breakdown is also unavailable. Geographic charts use regions and US states; country is US-only.")
with st.expander("Data audit details"):
 st.write({"Rows after cleaning":audit['rows'],"Duplicate rows removed":audit['duplicate_rows_removed'],"Date range":f"{audit['date_min'].date()} through {audit['date_max'].date()}","Filtered order lines":len(f),"Source fields missing from dataset":["Marketing spend","Acquisition/new-customer flag","Sales channel","Explicit churn/activity status"]})
st.download_button("⬇ Download filtered executive report (PDF)",data=make_pdf(f,k),file_name="Dashboard_Report.pdf",mime="application/pdf",width="content")
