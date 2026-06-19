import os
import json
import pandas as pd
import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go

# Set page configurations
st.set_page_config(
    layout="wide",
    page_title="판교 vs 위례 공간·통계적 대조 분석 대시보드",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# Custom Dark Mode styling
st.markdown("""
<style>
    /* Main Background and Text */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Header and Subheader Styling */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Outfit', 'Inter', sans-serif;
    }
    
    /* Segment separator styling */
    .section-title {
        border-bottom: 2px solid #2d3748;
        padding-bottom: 10px;
        margin-top: 40px;
        margin-bottom: 20px;
        font-weight: 700;
        font-size: 1.8rem;
    }
    
    /* Visual separation cards */
    .card {
        background-color: #1a202c;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .pangyo-border {
        border-left: 5px solid #00BFFF;
    }
    
    .wirye-border {
        border-left: 5px solid #F72585;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        line-height: 1.2;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Data Directories
workspace_dir = r"c:\Users\zhaka\Desktop\Zhaka"
data_dir = os.path.join(workspace_dir, "processed_data")

# Load preprocessed statistics
@st.cache_data
def load_data():
    # 1. LUM stats
    with open(os.path.join(data_dir, "lum_stats.json"), "r", encoding='utf-8') as f:
        lum_stats = json.load(f)
        
    # 2. Isochrone stats
    with open(os.path.join(data_dir, "isochrones_stats.json"), "r", encoding='utf-8') as f:
        iso_stats = json.load(f)
        
    # 3. Industry Comparison
    ind_comp = pd.read_csv(os.path.join(data_dir, "industry_comparison.csv"))
    
    return lum_stats, iso_stats, ind_comp

try:
    lum_stats, iso_stats, ind_comp = load_data()
except Exception as e:
    st.error(f"데이터를 로드하는 중 오류가 발생했습니다. 전처리 상태를 확인해주세요: {e}")
    st.stop()

# Helper mapping for UI
lum_map = {item['region']: item for item in lum_stats}

# ==============================================================================
# HEADER & OVERVIEW
# ==============================================================================
st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>자족형 중심지(판교) vs 배후 주거지(위례)의 공간·통계적 대조 분석</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0aec0; font-size: 1.1rem; margin-bottom: 30px;'>성남 판교테크노밸리(삼평동)와 위례신도시(송파/수정 위례동)의 토지이용 혼합도, 교통 접근성 배후인구 및 산업 구조 대조 분석</p>", unsafe_allow_html=True)

# Overview cards
col_p, col_w = st.columns(2)

with col_p:
    st.markdown("""
    <div class="card pangyo-border">
        <h3 style="margin-top: 0; color: #00BFFF !important;">🏢 제1판교테크노밸리 (삼평동)</h3>
        <p style="color: #cbd5e0; font-size: 0.95rem; line-height: 1.6;">
            <b>일자리 중심의 자족형 스마트 도시</b><br>
            판교 삼평동은 IT/테크 기반의 풍부한 업무용 연면적(약 70%)을 보유하여 낮 시간대에 폭발적인 유입 인구가 발생합니다. 
            주변 교통 인프라가 일자리 중심으로 직결되어 있어 거대한 경제 배후 인구를 흡수하는 일자리 유입 허브의 성격을 띱니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_w:
    st.markdown("""
    <div class="card wirye-border">
        <h3 style="margin-top: 0; color: #F72585 !important;">🏡 위례신도시 (송파·수정 위례동)</h3>
        <p style="color: #cbd5e0; font-size: 0.95rem; line-height: 1.6;">
            <b>주거 기능 중심의 전형적인 배후 주거지(베드타운)</b><br>
            위례는 아파트 및 단독주택 등의 주거 용도 비중이 압도적(70% 이상)입니다. 
            내부 고부가가치 산업 기반이 거의 없어 주민 대부분이 강남 및 판교 등 외부 업무 중심지로 출퇴근하며, 근린 상권 중심의 소비 위주 일자리 구조를 띱니다.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# SESSION 1: LAND USE MIXEDNESS (LUM)
# ==============================================================================
st.markdown("<div class='section-title'>📊 세션 1: 토지이용 혼합도 (LUM) — 건물 용도의 차이</div>", unsafe_allow_html=True)

# Metrics comparison
col_m1, col_m2 = st.columns(2)

with col_m1:
    p_lum = lum_map['Pangyo']
    st.markdown(f"""
    <div class="card pangyo-border" style="padding: 15px 20px;">
        <div class="metric-label">판교 토지이용 혼합도 점수 (Entropy Index)</div>
        <div class="metric-value" style="color: #00BFFF;">{p_lum['entropy_index']:.3f}</div>
        <p style="margin: 0; color: #a0aec0; font-size: 0.85rem;">
            업무용: <b>{p_lum['office_ratio']*100:.1f}%</b> | 주거용: <b>{p_lum['residential_ratio']*100:.1f}%</b> | 상업용: <b>{p_lum['commercial_ratio']*100:.1f}%</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    w_lum = lum_map['Wirye']
    st.markdown(f"""
    <div class="card wirye-border" style="padding: 15px 20px;">
        <div class="metric-label">위례 토지이용 혼합도 점수 (Entropy Index)</div>
        <div class="metric-value" style="color: #F72585;">{w_lum['entropy_index']:.3f}</div>
        <p style="margin: 0; color: #a0aec0; font-size: 0.85rem;">
            업무용: <b>{w_lum['office_ratio']*100:.1f}%</b> | 주거용: <b>{w_lum['residential_ratio']*100:.1f}%</b> | 상업용: <b>{w_lum['commercial_ratio']*100:.1f}%</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Maps side-by-side
col_map1, col_map2 = st.columns(2)

# Colors for dominant use mapping
# 주거용, 상업용, 업무용
use_colors = {
    '주거용': '#FF9F1C',   # Orange
    '상업용': '#FF1493',   # Deep Pink
    '업무용': '#00BFFF',   # Deep Sky Blue
    '기타/미확인': '#4A5568' # Grey
}

def style_function(feature):
    use = feature['properties'].get('dominant_use', '기타/미확인')
    color = use_colors.get(use, '#4A5568')
    return {
        'fillColor': color,
        'color': '#1A202C',
        'weight': 0.5,
        'fillOpacity': 0.75
    }

# Load GeoJSONs
@st.cache_data
def load_geojson(filename):
    path = os.path.join(data_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

geojson_pangyo = load_geojson("lum_map_Pangyo.geojson")
geojson_wirye = load_geojson("lum_map_Wirye.geojson")

with col_map1:
    st.markdown("<h4 style='text-align: center;'>판교 건물 용도 분포 지도 (삼평동)</h4>", unsafe_allow_html=True)
    # Center coordinates for Sampyeong-dong
    m_p = folium.Map(location=[37.4012, 127.1112], zoom_start=14, tiles='cartodb-darkmatter')
    
    # Tooltip and Layer
    folium.GeoJson(
        geojson_pangyo,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['JIBUN', 'dominant_use', '주거용', '상업용', '업무용'],
            aliases=['지번:', '대표 용도:', '주거 연면적(㎡):', '상업 연면적(㎡):', '업무 연면적(㎡):'],
            localize=True
        )
    ).add_to(m_p)
    
    # Legend
    legend_html = f"""
    <div style="position: fixed; bottom: 50px; left: 50px; width: 120px; height: 110px; 
                background-color: rgba(26, 32, 44, 0.85); z-index:9999; border:1px solid #2d3748; 
                border-radius: 8px; padding: 10px; font-size:11px; color:#e0e0e0; font-family:sans-serif;">
        <b>건물 주용도</b><br>
        <i style="background:{use_colors['주거용']};width:12px;height:12px;float:left;margin-right:8px;border-radius:2px;"></i>주거용<br>
        <i style="background:{use_colors['상업용']};width:12px;height:12px;float:left;margin-right:8px;border-radius:2px;"></i>상업용<br>
        <i style="background:{use_colors['업무용']};width:12px;height:12px;float:left;margin-right:8px;border-radius:2px;"></i>업무용<br>
        <i style="background:{use_colors['기타/미확인']};width:12px;height:12px;float:left;margin-right:8px;border-radius:2px;"></i>기타/공공<br>
    </div>
    """
    m_p.get_root().html.add_child(folium.Element(legend_html))
    folium_static(m_p, width=650, height=450)

with col_map2:
    st.markdown("<h4 style='text-align: center;'>위례 건물 용도 분포 지도 (창곡동)</h4>", unsafe_allow_html=True)
    # Center coordinates for Changgok-dong
    m_w = folium.Map(location=[37.4705, 127.1395], zoom_start=14, tiles='cartodb-darkmatter')
    
    folium.GeoJson(
        geojson_wirye,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['JIBUN', 'dominant_use', '주거용', '상업용', '업무용'],
            aliases=['지번:', '대표 용도:', '주거 연면적(㎡):', '상업 연면적(㎡):', '업무 연면적(㎡):'],
            localize=True
        )
    ).add_to(m_w)
    
    # Legend
    legend_html = f"""
    <div style="position: fixed; bottom: 50px; left: 50px; width: 120px; height: 110px; 
                background-color: rgba(26, 32, 44, 0.85); z-index:9999; border:1px solid #2d3748; 
                border-radius: 8px; padding: 10px; font-size:11px; color:#e0e0e0; font-family:sans-serif;">
        <b>건물 주용도</b><br>
        <i style="background:{use_colors['주거용']};width:12px;height:12px;float:left;margin-right:8px;border-radius:2px;"></i>주거용<br>
        <i style="background:{use_colors['상업용']};width:12px;height:12px;float:left;margin-right:8px;border-radius:2px;"></i>상업용<br>
        <i style="background:{use_colors['업무용']};width:12px;height:12px;float:left;margin-right:8px;border-radius:2px;"></i>업무용<br>
        <i style="background:{use_colors['기타/미확인']};width:12px;height:12px;float:left;margin-right:8px;border-radius:2px;"></i>기타/공공<br>
    </div>
    """
    m_w.get_root().html.add_child(folium.Element(legend_html))
    folium_static(m_w, width=650, height=450)


# ==============================================================================
# SESSION 2: SUBWAY ISOCHRONE & SERVICE POPULATION
# ==============================================================================
st.markdown("<div class='section-title'>🚆 세션 2: 지하철 생활권 배후 인구 — 접근성의 차이</div>", unsafe_allow_html=True)

# Selectbox to toggle time limit
time_choice = st.selectbox("지하철 이동 시간권 기준 선택", [30, 60], format_func=lambda x: f"이동 {x}분권 범위")

# Get statistics for the choice
p_iso = [item for item in iso_stats if item['region'] == 'Pangyo' and item['time_limit'] == time_choice][0]
w_iso = [item for item in iso_stats if item['region'] == 'Wirye' and item['time_limit'] == time_choice][0]

# Display population numbers
col_p_pop, col_w_pop = st.columns(2)

with col_p_pop:
    st.markdown(f"""
    <div class="card pangyo-border" style="padding: 15px 20px;">
        <div class="metric-label">판교역 {time_choice}분 생활권 배후 활동 인구</div>
        <div class="metric-value" style="color: #00BFFF;">{p_iso['population']:,} 명</div>
        <p style="margin: 0; color: #a0aec0; font-size: 0.85rem;">
            도달 가능한 전철역 수: <b>{p_iso['station_count']}개</b> (강남, 분당 등 광역 일자리축 연결)
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_w_pop:
    st.markdown(f"""
    <div class="card wirye-border" style="padding: 15px 20px;">
        <div class="metric-label">장지/남위례역 {time_choice}분 생활권 배후 활동 인구</div>
        <div class="metric-value" style="color: #F72585;">{w_iso['population']:,} 명</div>
        <p style="margin: 0; color: #a0aec0; font-size: 0.85rem;">
            도달 가능한 전철역 수: <b>{w_iso['station_count']}개</b> (송파, 성남 본도심 등 상대적 한정)
        </p>
    </div>
    """, unsafe_allow_html=True)

# Bar chart comparison of population
fig_pop = go.Figure()
fig_pop.add_trace(go.Bar(
    y=['판교 (판교역 기점)', '위례 (장지/남위례역 기점)'],
    x=[p_iso['population'], w_iso['population']],
    orientation='h',
    marker=dict(
        color=['#00BFFF', '#F72585'],
        line=dict(color='#1A202C', width=1)
    )
))
fig_pop.update_layout(
    title=dict(text=f"지하철 이동 {time_choice}분 내 도달가능 배후인구 규모 비교", font=dict(color='#ffffff')),
    plot_bgcolor='#1a202c',
    paper_bgcolor='#0e1117',
    xaxis=dict(title="인구수 (명)", gridcolor='#2d3748', tickformat=',', tickfont=dict(color='#cbd5e0')),
    yaxis=dict(tickfont=dict(color='#cbd5e0')),
    height=250,
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig_pop, use_container_width=True)

# Maps for isochrones
col_iso_map1, col_iso_map2 = st.columns(2)

geojson_iso_p = load_geojson(f"isochrone_Pangyo_{time_choice}m.geojson")
geojson_iso_w = load_geojson(f"isochrone_Wirye_{time_choice}m.geojson")

# Subway stations layer from shapefile inside zip
@st.cache_data
def get_station_markers():
    gdf_s = gpd.read_file(os.path.join(workspace_dir, "subway_network", "edit", "stations.shp"))
    # convert to epsg 4326
    gdf_s_4326 = gdf_s.to_crs(epsg=4326)
    return gdf_s_4326

stations_gdf = get_station_markers()

with col_iso_map1:
    st.markdown(f"<h4 style='text-align: center;'>판교역 기점 {time_choice}분 등시간권 그물망 (1km 버퍼)</h4>", unsafe_allow_html=True)
    m_iso_p = folium.Map(location=[37.44, 127.11], zoom_start=11, tiles='cartodb-darkmatter')
    
    # Draw Isochrone buffer
    folium.GeoJson(
        geojson_iso_p,
        style_function=lambda x: {
            'fillColor': '#00BFFF',
            'color': '#00BFFF',
            'weight': 1.5,
            'fillOpacity': 0.35
        }
    ).add_to(m_iso_p)
    
    # Draw reachable stations as small circles
    reachable_station_names = p_iso['stations']
    st_reach_p = stations_gdf[stations_gdf['statnm'].isin(reachable_station_names)]
    for idx, row in st_reach_p.iterrows():
        lat = row.geometry.y
        lon = row.geometry.x
        folium.CircleMarker(
            location=[lat, lon],
            radius=3.5,
            color='#00BFFF',
            fill=True,
            fill_color='#00BFFF',
            fill_opacity=0.9,
            popup=f"{row['statnm']}역 ({row['linenm']})"
        ).add_to(m_iso_p)
        
    # Mark origin station
    folium.Marker(
        location=[37.3947, 127.1112],
        popup="판교역 (출발지)",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m_iso_p)
    
    folium_static(m_iso_p, width=650, height=450)

with col_iso_map2:
    st.markdown(f"<h4 style='text-align: center;'>위례지역 역 기점 {time_choice}분 등시간권 그물망 (1km 버퍼)</h4>", unsafe_allow_html=True)
    m_iso_w = folium.Map(location=[37.47, 127.12], zoom_start=11, tiles='cartodb-darkmatter')
    
    # Draw Isochrone buffer
    folium.GeoJson(
        geojson_iso_w,
        style_function=lambda x: {
            'fillColor': '#F72585',
            'color': '#F72585',
            'weight': 1.5,
            'fillOpacity': 0.35
        }
    ).add_to(m_iso_w)
    
    # Draw reachable stations
    reachable_station_names_w = w_iso['stations']
    st_reach_w = stations_gdf[stations_gdf['statnm'].isin(reachable_station_names_w)]
    for idx, row in st_reach_w.iterrows():
        lat = row.geometry.y
        lon = row.geometry.x
        folium.CircleMarker(
            location=[lat, lon],
            radius=3.5,
            color='#F72585',
            fill=True,
            fill_color='#F72585',
            fill_opacity=0.9,
            popup=f"{row['statnm']}역 ({row['linenm']})"
        ).add_to(m_iso_w)
        
    # Mark origins
    folium.Marker(
        location=[37.478, 127.126], # 장지역 대략 위치
        popup="장지역 (출발지)",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m_iso_w)
    
    folium.Marker(
        location=[37.462, 127.143], # 남위례역 대략 위치
        popup="남위례역 (출발지)",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m_iso_w)
    
    folium_static(m_iso_w, width=650, height=450)


# ==============================================================================
# SESSION 3: JOBS & INDUSTRY STRUCTURE
# ==============================================================================
st.markdown("<div class='section-title'>💼 세션 3: 일자리 및 산업 구조 — 직주의 차이</div>", unsafe_allow_html=True)

# Prepare DataFrame for Plotly Express
ind_comp_melted = ind_comp.melt(
    id_vars=['industry_name'],
    value_vars=['ratio_Pangyo', 'ratio_Wirye'],
    var_name='Region',
    value_name='Ratio'
)

ind_comp_melted['Region'] = ind_comp_melted['Region'].map({
    'ratio_Pangyo': '판교 (삼평동)',
    'ratio_Wirye': '위례 (위례동 합산)'
})

# Filter out zero ratios to keep graph clean
ind_comp_filtered = ind_comp_melted[ind_comp_melted['Ratio'] > 0.1].sort_values(by='Ratio', ascending=True)

# Draw Side-by-side horizontal bar chart
fig_ind = px.bar(
    ind_comp_filtered,
    y='industry_name',
    x='Ratio',
    color='Region',
    barmode='group',
    orientation='h',
    color_discrete_map={
        '판교 (삼평동)': '#00BFFF',
        '위례 (위례동 합산)': '#F72585'
    },
    labels={
        'industry_name': '산업 대분류',
        'Ratio': '종사자수 비율 (%)',
        'Region': '지역'
    }
)

fig_ind.update_layout(
    title=dict(text="두 지역 내의 산업대분류별 종사자 비율 비교 (Side-by-side)", font=dict(color='#ffffff')),
    plot_bgcolor='#1a202c',
    paper_bgcolor='#0e1117',
    xaxis=dict(title="비율 (%)", gridcolor='#2d3748', tickfont=dict(color='#cbd5e0')),
    yaxis=dict(tickfont=dict(color='#cbd5e0')),
    height=600,
    legend=dict(font=dict(color='#cbd5e0'), bgcolor='rgba(26, 32, 44, 0.8)'),
    margin=dict(l=20, r=20, t=50, b=20)
)

st.plotly_chart(fig_ind, use_container_width=True)

# Highlights card below the graph
col_hl1, col_hl2 = st.columns(2)

with col_hl1:
    st.markdown("""
    <div class="card pangyo-border" style="padding: 15px 20px;">
        <h4 style="margin-top: 0; color: #00BFFF !important;">🎯 판교의 고부가가치 IT·테크 집중</h4>
        <p style="color: #cbd5e0; font-size: 0.9rem; line-height: 1.5; margin-bottom: 0;">
            판교는 <b>정보통신업(J) 44.4%</b> 및 <b>전문·과학·기술 서비스업(M) 20.1%</b>로, 두 첨단 테크 업종의 비중이 <b>64.5%</b>에 달해 독점적인 IT 국가 산업 밸리의 성격을 가감 없이 드러내고 있습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_hl2:
    st.markdown("""
    <div class="card wirye-border" style="padding: 15px 20px;">
        <h4 style="margin-top: 0; color: #F72585 !important;">🏪 위례의 생활 근린상권·베드타운형 산업</h4>
        <p style="color: #cbd5e0; font-size: 0.9rem; line-height: 1.5; margin-bottom: 0;">
            위례는 <b>도소매업(G) 19.3%</b>, <b>교육 서비스업(P) 18.7%</b>, <b>보건/복지 서비스(Q) 17.4%</b>, <b>숙박/음식점업(I) 15.0%</b> 등 주거생활을 지원하는 기초 동네 상권 및 교육시설 위주의 전형적인 소비 배후지 성격을 나타내고 있습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
