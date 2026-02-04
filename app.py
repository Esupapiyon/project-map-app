import streamlit as st
import datetime
import plotly.graph_objects as go
import random
import os

# ==========================================
# 0. ロジックエンジン (Ver 7.3)
# ==========================================

GAN_ELEMENTS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
GAN_FIVE = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4] 
ZHI_FIVE = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4] 
SOLAR_TERMS = [6, 4, 6, 5, 6, 6, 7, 8, 8, 8, 7, 7] 

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

# 簡易相性ロジック
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
# UI実装 (Streamlit)
# ==========================================

st.set_page_config(page_title="AI×占い科学診断", page_icon="🔮", layout="wide")
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
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🔮 AI性格診断")
input_date = st.sidebar.date_input("生年月日", datetime.date(2000, 1, 1))

if st.sidebar.button("診断する", type="primary"):
    engine = FortuneEngineIntegrated()
    date_str = input_date.strftime("%Y/%m/%d")
    result = engine.analyze_basic(date_str)
    gan_id = result['gan']
    content = DIAGNOSIS_CONTENT[gan_id]
    scores = result['scores']
    
    col_h1, col_h2 = st.columns([1, 2])
    
    with col_h1:
        # ★★★ 画像読み込みロジック (強化版) ★★★
        target_id = gan_id + 1
        found_path = None
        
        # 1. 複数の拡張子で探索
        search_exts = [".png", ".jpg", ".jpeg", ".PNG", ".JPG"]
        for ext in search_exts:
            trial_path = os.path.join("images", f"{target_id}{ext}")
            if os.path.exists(trial_path):
                found_path = trial_path
                break
        
        # 2. 結果に応じた表示
        if found_path:
            # 画像発見時
            st.image(found_path, caption=f"Type: {content['type_name'].split('：')[0]}", use_container_width=True)
        else:
            # 画像が見つからない場合（デバッグ表示）
            st.error(f"❌ 画像が見つかりません (ID: {target_id})")
            
            # imagesフォルダの存在確認
            if os.path.exists("images"):
                files = os.listdir("images")
                st.write("📂 現在の images フォルダの中身:", files)
            else:
                st.error("📂 'images' フォルダ自体が存在しません！")
                
            # ダミー画像を表示してレイアウト崩れを防ぐ
            st.image(
                "https://placehold.co/400x400/222/FFF?text=No+Image", 
                caption="画像ロードエラー", 
                use_container_width=True
            )
    
    with col_h2:
        st.markdown(f"<div class='fate-code-chip'>FATE-Code: {result['fate_code']}</div>", unsafe_allow_html=True)
        st.title(content['type_name'])
        st.markdown(f"<div class='big-catch'>{content['catch_copy']}</div>", unsafe_allow_html=True)

    st.divider()
    
    # 以下、チャート表示など既存ロジック
    categories = ['Identity', 'Create', 'Economy', 'Status', 'Vitality']
    r_values = [scores[c.split()[0]] for c in categories]
    fig = go.Figure(data=go.Scatterpolar(r=r_values, theta=categories, fill='toself', line_color='#00FF99'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False, height=300, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.success(f"社会的役割: {content['role_desc']}")
    st.error(f"愛すべき欠点: {content['flaw_desc']}")

    st.markdown("---")
    st.subheader("💞 運命の相性 Best 3")
    cols = st.columns(3)
    for i, p in enumerate(result['partners']):
        cols[i].success(f"{i+1}位: {p}")
        
    st.markdown("---")
    st.link_button("🔑 完全版レポート（無料）", "https://line.me/R/ti/p/dummy_id", type="primary", use_container_width=True)

else:
    st.info("サイドバーから診断を開始してください。")
