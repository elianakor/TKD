import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="KickSFO | 태권도 선수 기술 특성 분석",
    layout="wide"
)

# --------------------------------------------------
# Header (Logo + Title)
# --------------------------------------------------
col_logo, col_title = st.columns([1, 9])
with col_logo:
    st.markdown("## 🥋 **KickSFO**")
with col_title:
    st.title("태권도 선수 기술 특성 분석 대시보드")
    st.caption("경기 데이터 기반 자동 점수 산출 · 선수 비교 방사형 분석")

st.divider()

# --------------------------------------------------
# Category definition
# --------------------------------------------------
CATEGORIES = {
    "얼굴": {
        "뒷발": ["돌려차기", "찍기", "이중발"],
        "앞발": ["빠른발", "앞발"]
    },
    "몸통": {
        "뒷발": ["돌려차기", "컷트"],
        "앞발": ["빠른발", "앞발", "앞발컷트"]
    }
}

AXES = []
for target, foots in CATEGORIES.items():
    for foot, skills in foots.items():
        for skill in skills:
            AXES.append(f"{target}-{foot}-{skill}")

# --------------------------------------------------
# Sample data (default view)
# --------------------------------------------------
def load_sample_data():
    data = [
        ["김선수", "얼굴", "앞발", "빠른발", 1, "공격형", "앞발 빠른발", "8년", "kim.png"],
        ["김선수", "몸통", "앞발", "앞발", 1, "공격형", "앞발 빠른발", "8년", "kim.png"],
        ["이선수", "몸통", "뒷발", "돌려차기", 1, "수비형", "뒷발 돌려차기", "10년", "lee.png"],
        ["이선수", "얼굴", "뒷발", "돌려차기", 0, "수비형", "뒷발 돌려차기", "10년", "lee.png"],
        ["박선수", "얼굴", "앞발", "빠른발", 1, "혼합형", "속임 동작", "6년", "park.png"],
    ]
    return pd.DataFrame(
        data,
        columns=["athlete", "target", "foot", "technique", "success", "style", "signature", "career", "photo"]
    )

# --------------------------------------------------
# Scoring logic
# --------------------------------------------------
def score_from_match_data(df):
    score_dict = {}
    grouped = df.groupby(["athlete", "target", "foot", "technique"])

    for (ath, tgt, foot, tech), g in grouped:
        axis = f"{tgt}-{foot}-{tech}"
        score_dict.setdefault(ath, {})
        score_dict[ath][axis] = round(g["success"].mean() * 100, 1)

    return score_dict

# --------------------------------------------------
# Radar chart
# --------------------------------------------------
def draw_radar(score_dict, players):
    fig = go.Figure()
    theta = AXES + [AXES[0]]

    for name in players:
        r = [score_dict[name].get(axis, 0) for axis in AXES]
        r.append(r[0])

        fig.add_trace(go.Scatterpolar(
            r=r,
            theta=theta,
            fill="toself",
            name=name
        ))

    fig.update_layout(
        template="plotly_dark",
        polar=dict(radialaxis=dict(range=[0, 100])),
        title="태권도 선수 기술 특성 비교"
    )
    return fig

# --------------------------------------------------
# Sidebar upload
# --------------------------------------------------
uploaded = st.sidebar.file_uploader(
    "태권도 경기 데이터 CSV 업로드",
    type="csv"
)

# --------------------------------------------------
# Main logic
# --------------------------------------------------
if uploaded:
    df = pd.read_csv(uploaded)
    st.subheader("데이터 미리보기")
    st.dataframe(df.head(), use_container_width=True)
else:
    st.info("📌 현재 샘플 데이터로 시연 중입니다. 좌측에서 CSV를 업로드하면 실제 데이터로 전환됩니다.")
    df = load_sample_data()

scores = score_from_match_data(df)
players = list(scores.keys())

selected = st.sidebar.multiselect(
    "비교할 선수 선택",
    players,
    default=players
)

if selected:
    fig = draw_radar(scores, selected)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("선수 프로파일")

    cols = st.columns(len(selected))
    for col, name in zip(cols, selected):
        with col:
            row = df[df["athlete"] == name].iloc[0]
            photo_path = Path("images") / row["photo"]
            if photo_path.exists():
                st.image(str(photo_path), use_container_width=True)
            else:
                st.image("https://via.placeholder.com/200x250?text=No+Image")

            st.markdown(f"**{name}**")
            st.markdown(f"스타일: {row['style']}")
            st.markdown(f"주특기: {row['signature']}")
            st.markdown(f"경력: {row['career']}")

    st.subheader("선수별 기술 점수")
    table = []
    for name in selected:
        row = {"선수": name}
        row.update(scores[name])
        table.append(row)

    st.dataframe(pd.DataFrame(table), use_container_width=True)

# --------------------------------------------------
# Footer (copyright)
# --------------------------------------------------
st.divider()
st.caption("© 2025 KickSFO. All rights reserved. · Research & Performance Analytics Platform")
