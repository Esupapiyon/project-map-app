import streamlit as st
import datetime
import plotly.graph_objects as go
import random
import os
import pandas as pd

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
# 2. Styles & CSS
# ==========================================
st.markdown("""
<style>
    .fate-code-chip {
        background-color: #2e2e2e;
        color: #00FF99;
        padding: 5px 15px;
        border-radius: 20px;
        font-family: monospace;
        font-weight: bold;
        border: 1px solid #00FF99;
        display: inline-block;
        margin-bottom: 10px;
    }
    .big-catch {
        font-size: 1.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF00CC, #333399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    /* ぼかしエリアのスタイル */
    .blur-container {
        filter: blur(5px);
        opacity: 0.6;
        pointer-events: none;
        user-select: none;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. Helper Functions (Image Loader)
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
# 4. Logic Data & Constants (Ver 7.4)
# ==========================================

GAN_ELEMENTS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
GAN_FIVE = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4] 
ZHI_FIVE = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4] 
SOLAR_TERMS = [6, 4, 6, 5, 6, 6, 7, 8, 8, 8, 7, 7] 

# 十二運エネルギー値
ENERGY_STRENGTH = [
    [3, 2, 3, 3, 2, 1, 1, 1, 1, 1, 2, 3], # 甲
    [3, 2, 3, 3, 2, 1, 1, 1, 1, 1, 2, 3], # 乙
    [1, 1, 3, 3, 2, 3, 3, 2, 1, 1, 1, 1], # 丙
    [1, 1, 3, 3, 2, 3, 3, 2, 1, 1, 1, 1], # 丁
    [1, 2, 3, 3, 3, 3, 3, 2, 1, 1, 1, 1], # 戊
    [1, 2, 3, 3, 3, 3, 3, 2, 1, 1, 1, 1], # 己
    [1, 2, 1, 1, 2, 3, 3, 2, 3, 3, 2, 1], # 庚
    [1, 2, 1, 1, 2, 3, 3, 2, 3, 3, 2, 1], # 辛
    [3, 2, 1, 1, 2, 1, 1, 1, 3, 3, 2, 3], # 壬
    [3, 2, 1, 1, 2, 1, 1, 1, 3, 3, 2, 3]  # 癸
]

# 相性ロジック
COMPATIBILITY_MAP = {
    0: ["己 (THE NURTURER)", "庚 (THE HERO)", "丁 (THE MUSE)"],
    1: ["庚 (THE HERO)", "辛 (THE IDOL)", "丙 (THE PROTAGONIST)"],
    2: ["辛 (THE IDOL)", "壬 (THE NOMAD)", "戊 (THE ANCHOR)"],
    3: ["壬 (THE NOMAD)", "癸 (THE COUNSELOR)", "己 (THE NURTURER)"],
    4: ["癸 (THE COUNSELOR)", "甲 (THE LEADER)", "庚 (THE HERO)"],
    5: ["甲 (THE LEADER)", "乙 (THE CONNECTOR)", "辛 (THE IDOL)"],
    6: ["乙 (THE CONNECTOR)", "丙 (THE PROTAGONIST)", "壬 (THE NOMAD)"],
    7: ["丙 (THE PROTAGONIST)", "丁 (THE MUSE)", "癸 (THE COUNSELOR)"],
    8: ["丁 (THE MUSE)", "戊 (THE ANCHOR)", "甲 (THE LEADER)"],
    9: ["戊 (THE ANCHOR)", "己 (THE NURTURER)", "乙 (THE CONNECTOR)"]
}

DIAGNOSIS_CONTENT = {
    0: {"type_name": "No.1 甲：THE LEADER", "catch_copy": "折れない信念を持つ、孤高の統率者", "role_desc": "組織の道しるべとなるリーダー。", "flaw_desc": "一度折れると再起不能のガラスの巨塔。", "desire": "尊敬と成長"},
    1: {"type_name": "No.2 乙：THE CONNECTOR", "catch_copy": "したたかに生き残る、柔軟な戦略家", "role_desc": "どんな環境でも生き残る調整役。", "flaw_desc": "八方美人すぎて自分を見失う。", "desire": "調和と安全"},
    2: {"type_name": "No.3 丙：THE PROTAGONIST", "catch_copy": "世界を照らす、あくなき挑戦者", "role_desc": "周囲を明るくするムードメーカー。", "flaw_desc": "私の話を聞け！なジャイアン気質。", "desire": "注目と称賛"},
    3: {"type_name": "No.4 丁：THE MUSE", "catch_copy": "静寂に燃える、知性の灯火", "role_desc": "本質を突く参謀・クリエイター。", "flaw_desc": "察してちゃん界のラスボス。", "desire": "理解と美学"},
    4: {"type_name": "No.5 戊：THE ANCHOR", "catch_copy": "すべてを受け入れる、揺るがぬ巨塔", "role_desc": "動じない安心感を与える守護神。", "flaw_desc": "テコでも動かない頑固オヤジ。", "desire": "安定と信頼"},
    5: {"type_name": "No.6 己：THE NURTURER", "catch_copy": "才ある者を育む、慈愛の大地", "role_desc": "才能を育て輝かせる育成者。", "flaw_desc": "尽くしすぎてダメンズ製造機。", "desire": "貢献と親密"},
    6: {"type_name": "No.7 庚：THE HERO", "catch_copy": "時代を切り拓く、鋼の革命家", "role_desc": "停滞を打破する起爆剤。", "flaw_desc": "デリカシー？何それ美味しいの？", "desire": "変革と勝利"},
    7: {"type_name": "No.8 辛：THE IDOL", "catch_copy": "試練を輝きに変える、美しきカリスマ", "role_desc": "美学を体現する職人・象徴。", "flaw_desc": "メンタル強度スライム級のワガママ。", "desire": "特別感と洗練"},
    8: {"type_name": "No.9 壬：THE NOMAD", "catch_copy": "境界を超えて流れる、自由の象徴", "role_desc": "新しい風を吹き込む冒険家。", "flaw_desc": "ふらっと消える音信不通の常習犯。", "desire": "自由と流動"},
    9: {"type_name": "No.10 癸：THE COUNSELOR", "catch_copy": "静かに浸透する、慈愛の賢者", "role_desc": "組織を潤滑にする癒やしの知恵袋。", "flaw_desc": "影響受けすぎ！な自分がないスライム。", "desire": "共感と貢献"}
}

# ==========================================
# 5. Logic Engine (Ver 7.4)
# ==========================================
class FortuneEngineIntegrated:
    def __init__(self):
        self.base_date = datetime.date(1900, 1, 1)

    def get_sexagenary_cycle(self, date_obj):
        days_diff = (date_obj - self.base_date).days
        return (10 + days_diff) % 60

    def get_month_pillar(self, year, month, day):
        is_after_setsuiri = day >= SOLAR_TERMS[month - 1]
        year_gan_idx = (year - 3) % 10
        month_base_map = {0: 2, 1: 2, 2: 4, 3: 4, 4: 6, 5: 6, 6: 8, 7: 8, 8: 0, 9: 0}
        month_start_gan = month_base_map[year_gan_idx]
        calc_month = month if is_after_setsuiri else month - 1
        if calc_month == 0: calc_month = 12
        month_offset = (calc_month + 10) % 12 
        m_gan = (month_start_gan + month_offset) % 10
        m_zhi = (2 + month_offset) % 12 
        return m_gan, m_zhi

    def get_star_category(self, day_gan, target_gan_five):
        me = GAN_FIVE[day_gan]
        target = target_gan_five
        if me == target: return "Identity"
        elif (me + 1) % 5 == target: return "Create"
        elif (target + 1) % 5 == me: return "Vitality"
        elif (me + 2) % 5 == target: return "Economy"
        elif (target + 2) % 5 == me: return "Status"
        return "Identity"

    def analyze_basic(self, dob_str):
        y, m, d = map(int, dob_str.split('/'))
        date_obj = datetime.date(y, m, d)
        
        day_seq = self.get_sexagenary_cycle(date_obj)
        gan = day_seq % 10
        zhi = day_seq % 12
        
        m_gan, m_zhi = self.get_month_pillar(y, m, d)
        y_gan = (y - 3) % 10
        y_zhi = (y - 3) % 12

        # 欲求パラメータ算出
        counts = {"Identity": 0, "Create": 0, "Economy": 0, "Status": 0, "Vitality": 0}
        targets = [
            (GAN_FIVE[y_gan], 1), (GAN_FIVE[m_gan], 1),
            (ZHI_FIVE[y_zhi], 1), (ZHI_FIVE[m_zhi], 2), (ZHI_FIVE[zhi], 1)
        ]
        for five_el, weight in targets:
            cat = self.get_star_category(gan, five_el)
            counts[cat] += weight

        normalized_scores = {}
        for k, v in counts.items():
            if v == 0: score_5 = 1
            elif v == 1: score_5 = 2
            elif v == 2: score_5 = 3
            elif v == 3: score_5 = 4
            else: score_5 = 5
            normalized_scores[k] = score_5

        # FATE-Code Logic
        scores_raw = counts
        axis_1 = "L" if scores_raw["Vitality"] >= scores_raw["Create"] else "S"
        defensive = scores_raw["Status"] + scores_raw["Vitality"]
        offensive = scores_raw["Economy"] + scores_raw["Create"]
        axis_2 = "R" if defensive >= offensive else "G"
        energy_sum = ENERGY_STRENGTH[gan][zhi] + ENERGY_STRENGTH[gan][m_zhi] + ENERGY_STRENGTH[gan][y_zhi]
        axis_3 = "I" if energy_sum >= 6 else "D"
        social = scores_raw["Economy"] + scores_raw["Status"]
        axis_4 = "M" if scores_raw["Identity"] * 1.5 >= social else "Y"
        fate_code = f"{axis_1}{axis_2}{axis_3}{axis_4}"

        return {
            "gan": gan,
            "scores": normalized_scores,
            "fate_code": fate_code,
            "partners": COMPATIBILITY_MAP.get(gan, [])
        }

# ==========================================
# 6. Main App UI
# ==========================================
with st.sidebar:
    st.header("Project MAP")
    # Date Input
    dob = st.date_input("生年月日", value=pd.to_datetime("2000-01-01"))
    birth_time = st.selectbox("出生時間", ["不明", "00:00-01:59", "02:00-03:59", "etc"])
    sex = st.selectbox("性別", ["男性", "女性", "その他"])
    
    if st.button("診断する", type="primary"):
        st.session_state['run'] = True

if st.session_state.get('run'):
    # 1. 計算エンジンの実行
    engine = FortuneEngineIntegrated()
    date_str = dob.strftime("%Y/%m/%d")
    result = engine.analyze_basic(date_str)
    
    gan_id = result['gan']
    content = DIAGNOSIS_CONTENT[gan_id]
    scores = result['scores']
    
    # 2. 結果表示（ヘッダーエリア）
    col_h1, col_h2 = st.columns([1, 2])
    
    with col_h1:
        # 画像表示ロジック（タイプIDは gan_id + 1）
        type_id = gan_id + 1
        img_path, error_msg = load_image(type_id)
        if img_path:
            st.image(img_path, caption=f"Type: {content['type_name']}", use_container_width=True)
        else:
            st.warning(f"画像準備中")
            st.caption(f"Debug: {error_msg}")
            
    with col_h2:
        st.markdown(f"<div class='fate-code-chip'>FATE-Code: {result['fate_code']}</div>", unsafe_allow_html=True)
        st.title(content['type_name'])
        st.markdown(f"<div class='big-catch'>{content['catch_copy']}</div>", unsafe_allow_html=True)
        st.markdown(f"**基本的欲求 (Core Drive):** {content['desire']}")
    
    st.divider()
    
    # 3. パラメータ（レーダーチャート）
    st.subheader("📊 才能パラメーター")
    
    categories = ['Identity (自我)', 'Create (創造)', 'Economy (経済)', 'Status (地位)', 'Vitality (知性)']
    r_values = [scores['Identity'], scores['Create'], scores['Economy'], scores['Status'], scores['Vitality']]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=r_values,
        theta=categories,
        fill='toself',
        line_color='#00FF99',
        fillcolor='rgba(0, 255, 153, 0.3)'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False,
        margin=dict(t=20, b=20, l=40, r=40),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white") # ダークモード対応
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 4. 詳細データ（コンテンツ）
    col1, col2 = st.columns(2)
    with col1:
        st.info("🏢 **社会的役割**")
        st.write(content['role_desc'])
    with col2:
        st.error("❤️ **愛すべき欠点**")
        st.write(content['flaw_desc'])
        
    st.markdown("---")
    st.subheader("💞 運命の相性 Best 3")
    partners = result['partners']
    cols = st.columns(3)
    for i, p_name in enumerate(partners):
        with cols[i]:
            st.success(f"**{i+1}位**\n\n{p_name}")
            
    # 5. 寸止めエリア（LINE誘導）
    st.markdown("---")
    st.markdown("### 🔒 ここから先は「完全版レポート」限定...")
    
    # ぼかしコンテナ
    st.markdown('<div class="blur-container">', unsafe_allow_html=True)
    st.markdown("#### ④ コミュニケーションの癖")
    st.write("ここに詳細なコミュニケーションの癖が表示されます。あなたが無意識に行ってしまう...")
    st.markdown("#### ⑤ ストレス時の反応")
    st.write("限界を迎えたとき、あなたは急に殻に閉じこもり...")
    st.markdown("#### ⑥ 科学的ソリューション")
    st.write("認知科学に基づく具体的な行動指針が表示されます...")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CTAボタン
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button(
        label="🔑 完全版レポートと裏相性をLINEで受け取る（無料）",
        url="https://line.me/R/ti/p/dummy_id", # ここにLINE公式のURLを入れる
        type="primary",
        use_container_width=True
    )
    st.caption("※ 登録後、すぐに詳細レポートが届きます。")
