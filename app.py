import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# ==========================================
# 1. Page Config (Must be first)
# ==========================================
st.set_page_config(
    page_title="Project MAP 診断",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. Styles & Helper Functions
# ==========================================
def load_image(type_id):
    """
    画像のパスを柔軟に探す関数
    Streamlit CloudとColabの両方に対応
    """
    # 探す拡張子のリスト
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG']
    
    # ベースフォルダ（カレントディレクトリ直下のimages）
    base_dir = "images"
    
    # フォルダがあるか確認
    if not os.path.exists(base_dir):
        return None, f"Error: '{base_dir}' folder not found."
    
    # ファイル探索
    for ext in extensions:
        filename = f"{type_id}{ext}"
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            return file_path, None
            
    # 見つからなかった場合
    return None, f"Image not found for Type {type_id} in {base_dir}"

# ==========================================
# 3. Calculation Logic (Simplified for Demo)
# ==========================================
# ※実際のロジックに合わせて微調整してください
# ここではダミー関数として定義していますが、
# CEOの元のコードにある calculate_parameters 等があればそちらを使ってください

def get_fate_type(date):
    # （簡易ロジック: 日付から1~10を算出するダミー）
    # 実装済みのロジックがあればそのまま貼り付けてください
    day_num = int(date.strftime('%d'))
    type_id = (day_num % 10) 
    if type_id == 0: type_id = 10
    return type_id

def get_type_info(type_id):
    # 10タイプごとのデータ
    data = {
        1: {"name": "甲：THE PIONEER", "copy": "道を切り拓く孤高の樹木", "role": "リーダー", "flaw": "頑固すぎて折れる"},
        2: {"name": "乙：THE NETWORKER", "copy": "したたかに絡みつく蔦", "role": "調整役", "flaw": "依存心が強い"},
        3: {"name": "丙：THE SUN", "copy": "世界を照らす無邪気な太陽", "role": "中心人物", "flaw": "気分屋で飽きっぽい"},
        4: {"name": "丁：THE FLAME", "copy": "闇を燃やす情熱の灯火", "role": "革命家", "flaw": "内面の激しさが暴走"},
        5: {"name": "戊：THE MOUNTAIN", "copy": "動かざること山の如し", "role": "守護者", "flaw": "鈍感で腰が重い"},
        6: {"name": "己：THE EARTH", "copy": "全てを育む母なる大地", "role": "教育者", "flaw": "迷いすぎて動けない"},
        7: {"name": "庚：THE SWORD", "copy": "白黒つける正義の鋼", "role": "改革者", "flaw": "攻撃的すぎて敵を作る"},
        8: {"name": "辛：THE JEWEL", "copy": "試練で輝く高貴な宝石", "role": "美意識の塊", "flaw": "繊細すぎて傷つきやすい"},
        9: {"name": "壬：THE OCEAN", "copy": "変幻自在の冒険者", "role": "戦略家", "flaw": "流されやすく無責任"},
        10: {"name": "癸：THE RAIN", "copy": "慈愛と知性の恵みの雨", "role": "参謀", "flaw": "考えすぎてネガティブ"}
    }
    return data.get(type_id, data[10])

# ==========================================
# 4. Main App UI
# ==========================================
with st.sidebar:
    st.header("Project MAP")
    dob = st.date_input("生年月日", value=pd.to_datetime("1990-01-01"))
    birth_time = st.selectbox("出生時間", ["不明", "00:00-01:59", "02:00-03:59", "etc"])
    sex = st.selectbox("性別", ["男性", "女性", "その他"])
    
    if st.button("診断する", type="primary"):
        st.session_state['run'] = True

if st.session_state.get('run'):
    # 1. 計算
    type_id = get_fate_type(dob)
    info = get_type_info(type_id)
    
    # 2. 結果表示
    st.markdown(f"## {info['name']}")
    st.caption(info['copy'])
    
    # --- 画像表示ロジック（修正版） ---
    img_path, error_msg = load_image(type_id)
    if img_path:
        st.image(img_path, use_container_width=True)
    else:
        # 画像がない時のプレースホルダー
        st.warning(f"画像準備中: {error_msg}")
        st.info(f"現在のフォルダの中身: {os.listdir('.')}")
        if os.path.exists('images'):
             st.info(f"imagesフォルダの中身: {os.listdir('images')}")
    # --------------------------------
    
    # 3. パラメータ（ダミー）
    categories = ['Identity', 'Create', 'Economy', 'Status', 'Vitality']
    fig = go.Figure(data=go.Scatterpolar(
        r=[4, 5, 3, 2, 4], # ここは計算値を入れてください
        theta=categories,
        fill='toself',
        line_color='#00FF00'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # 4. 詳細データ
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ① 社会的役割")
        st.write(info['role'])
    with col2:
        st.markdown("### ② 愛すべき欠点")
        st.error(info['flaw'])
        
    st.divider()
    
    # 5. 寸止めエリア
    st.markdown("### ④ コミュニケーションの癖")
    st.markdown("🔒 ****************")
    st.markdown("### ⑤ ストレス時の反応")
    st.markdown("🔒 ****************")
    
    st.link_button(
        "🔑 完全版レポートと裏相性をLINEで受け取る（無料）",
        "https://line.me/R/ti/p/dummy_id", # ここにLINE URL
        type="primary",
        use_container_width=True
    )
