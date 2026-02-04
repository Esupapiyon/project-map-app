import streamlit as st
import datetime
import plotly.graph_objects as go
import random
import os
import pandas as pd

# ==========================================
# 1. Page Config & CSS (LINE誘導特化)
# ==========================================
st.set_page_config(
    page_title="Project MAP",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* ベーススタイル */
    .stApp {
        background-color: #FFFFFF;
        color: #333333;
        font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
    }
    
    /* カードデザイン（宿命エリア用） */
    .identity-card {
        background-color: #F9F9F9;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #E0E0E0;
        margin-bottom: 30px;
        text-align: center;
    }
    
    /* カードデザイン（科学エリア・寸止め用） */
    .analysis-card {
        position: relative; /* オーバーレイの基準 */
        background-color: #FFFFFF;
        border: 2px solid #F0F0F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 30px;
        overflow: hidden;
    }
    
    /* ぼかしエフェクト（クラス付与で制御） */
    .blurred-content {
        filter: blur(8px);
        opacity: 0.6;
        pointer-events: none; /* クリック不可 */
        user-select: none;    /* コピー不可 */
    }
    
    /* タイトル類 */
    .section-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #333;
        margin-top: 40px;
        margin-bottom: 20px;
        border-bottom: 2px solid #333;
        display: inline-block;
    }
    
    .identity-name {
        font-size: 2.2rem;
        font-weight: 900;
        color: #2c3e50;
        margin-bottom: 15px;
    }
    
    .hook-text-warning {
        font-size: 1.2rem;
        font-weight: bold;
        color: #D32F2F; /* 赤 */
        background-color: #FFEBEE;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #D32F2F;
        margin-bottom: 20px;
    }
    
    .hook-text-success {
        font-size: 1.2rem;
        font-weight: bold;
        color: #388E3C; /* 緑 */
        background-color: #E8F5E9;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #388E3C;
        margin-bottom: 20px;
    }

    /* 質問文 */
    .q-text {
        font-weight: 600;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Helper Functions
# ==========================================
def load_image(type_id):
    """画像のパス探索（8と9の入れ替えロジック維持）"""
    target_id = type_id
    if type_id == 8: target_id = 9
    elif type_id == 9: target_id = 8
        
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG']
    base_dir = "images"
    
    if not os.path.exists(base_dir):
        return None
    
    for ext in extensions:
        filename = f"{target_id}{ext}"
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            return path
    return None

# ==========================================
# 3. Logic Data
# ==========================================

TIPI_QUESTIONS = {
    "Q1": "活発で、外向的だと思う", "Q2": "他人に不満をもち、もめごとを起こしやすいと思う",
    "Q3": "しっかりしていて、自分に厳しいと思う", "Q4": "心配性で、うろたえやすいと思う",
    "Q5": "新しいことが好きで、変わった考えを持つと思う", "Q6": "控えめで、おとなしいと思う",
    "Q7": "人に気を使う方で、やさしいと思う", "Q8": "だらしなく、うっかりしていると思う",
    "Q9": "冷静で、気分が安定していると思う", "Q10": "発想力に欠けた、平凡な人間だと思う"
}

FATE_EXPLANATION = {
    "L": "Logic (論理)", "S": "Sense (感覚)", "R": "Risk (堅実)", "G": "Growth (成長)",
    "I": "Impulse (衝動)", "D": "Deliberate (熟考)", "M": "Me (自我)", "Y": "You (協調)"
}

# 診断コンテンツ
DIAGNOSIS_CONTENT = {
    0: {
        "type_name": "頼れる親分肌 (THE LEADER)",
        "catch_copy": "折れない信念を持つ、孤高の統率者",
        "desc": "あなたは大樹のように真っ直ぐで、曲がったことが大嫌いな正義の人です。混乱した状況でも一本の道筋を示すことができるリーダーシップを持っており、周囲から絶大な信頼を集めます。",
        "work_style_title": "一本筋の通った専門職・経営",
        "work": "自分の裁量でルールを決められる環境が最適です。誰かの指示に従うだけの仕事や、曖昧な忖度が求められる組織では窒息します。責任と権限がセットになったポジションでこそ真価を発揮します。",
        "love": "恋愛においても「尊敬」が最重要基準。互いに自立し高め合える対等な関係を求めます。",
        "fate_code": "Input(L) Process(R) Output(D) Drive(M)",
        "desire": "尊敬・成長",
        "flaw_desc": "融通ゼロ。正論で相手を追い詰め、孤立することがあります。"
    },
    1: {
        "type_name": "愛され調整役 (THE CONNECTOR)",
        "catch_copy": "したたかに生き残る、柔軟な戦略家",
        "desc": "あなたはどんな環境でも、草花のように柔軟に形を変えて生き残るサバイバーです。笑顔で周囲を調整しながら、いつの間にか自分に有利なポジションを確保する賢さがあります。",
        "work_style_title": "チームの潤滑油・広報",
        "work": "殺伐とした会議を和ませたり、利害関係を調整したりする能力は天才的。広報、人事、秘書など、人と人を繋ぐハブとなる仕事が天職です。",
        "love": "常に誰かと繋がっていたいタイプ。LINEの返信速度など目に見える愛情表現を重視します。",
        "fate_code": "Input(S) Process(G) Output(I) Drive(Y)",
        "desire": "調和・安全",
        "flaw_desc": "八方美人すぎて本音を見失いがち。決断を人任せにする癖があります。"
    },
    2: {
        "type_name": "天性の主人公 (THE PROTAGONIST)",
        "catch_copy": "世界を照らす、あくなき挑戦者",
        "desc": "あなたはそこにいるだけでその場がパッと明るくなる、太陽のような存在です。「なんとかなる！」という根拠のない自信で突き進むパワーを持っています。",
        "work_style_title": "表舞台に立つプレゼンター",
        "work": "ルーティンワークは不向き。営業、広報、YouTuberなど、自分の個性やキャラクターを売り込む仕事が最適です。",
        "love": "恋愛は直感型。自分の話をニコニコ聞いてくれて、常に褒めてくれる相手を求めます。",
        "fate_code": "Input(S) Process(G) Output(I) Drive(M)",
        "desire": "注目・称賛",
        "flaw_desc": "自己主張が強く、人の話を聞いていないことがあります。"
    },
    3: {
        "type_name": "熱き夢想家 (THE MUSE)",
        "catch_copy": "静寂に燃える、知性の灯火",
        "desc": "あなたは一見穏やかですが、内側には独自の美学と反骨精神を秘めています。鋭い洞察力を持ち、本質を見抜くことができます。",
        "work_style_title": "鋭い洞察を活かすクリエイター",
        "work": "感性と知性を融合させる仕事が向いています。デザイナー、ライター、参謀役など、独自の視点で価値を生む職種。",
        "love": "言葉にしなくても通じ合える、深い精神的な繋がりを求めます。一度心を許すと非常に一途です。",
        "fate_code": "Input(L) Process(R) Output(D) Drive(M)",
        "desire": "理解・美学",
        "flaw_desc": "言葉にせず「察してよ」オーラを出し、勝手に傷つくことがあります。"
    },
    4: {
        "type_name": "不動の守護神 (THE ANCHOR)",
        "catch_copy": "すべてを受け入れる、揺るがぬ巨塔",
        "desc": "あなたはちょっとやそっとのことでは動じない、圧倒的な包容力の持ち主です。相談されると相手を安心させてしまう器の大きさがあります。",
        "work_style_title": "組織を支えるバックオフィス",
        "work": "変化の激しい現場よりも、どっしりと構えて全体を見渡すポジションが向いています。総務、経理、不動産管理など。",
        "love": "刺激よりも穏やかで家庭的な関係を望みます。自分から動くのは苦手なので、少し強引な相手と相性が良いでしょう。",
        "fate_code": "Input(L) Process(R) Output(D) Drive(Y)",
        "desire": "安定・信頼",
        "flaw_desc": "変化を嫌い、現状維持に固執しすぎてチャンスを逃すことも。"
    },
    5: {
        "type_name": "尽くす世話焼き (THE NURTURER)",
        "catch_copy": "才ある者を育む、慈愛の大地",
        "desc": "あなたは困っている人を放っておけない、根っからの教育者です。他人の才能を見抜き、育て、輝かせることに無上の喜びを感じます。",
        "work_style_title": "人を育てる教育・メンター",
        "work": "教師、インストラクター、カスタマーサクセスなど、直接的に人の役に立つ仕事が天職です。",
        "love": "「あなたのためなら」と尽くすタイプ。少し頼りない相手を好きになりがちです。",
        "fate_code": "Input(S) Process(G) Output(D) Drive(Y)",
        "desire": "貢献・親密",
        "flaw_desc": "尽くしすぎて相手をダメにすることがあります。見返りがないと不満を溜めます。"
    },
    6: {
        "type_name": "正義の切り込み隊長 (THE HERO)",
        "catch_copy": "時代を切り拓く、鋼の革命家",
        "desc": "あなたは「それはおかしい」と声を上げ、古い体制を一刀両断する改革者です。その決断力は組織の停滞を打破する起爆剤となります。",
        "work_style_title": "改革を推進するリーダー",
        "work": "新規事業の立ち上げ、組織改革など、正義感とスピード決断が求められる現場が向いています。",
        "love": "駆け引きは大の苦手。議論ができる知的な相手を求めます。",
        "fate_code": "Input(L) Process(G) Output(I) Drive(M)",
        "desire": "変革・勝利",
        "flaw_desc": "デリカシーがなく、正論で相手を追い詰めてしまうことがあります。"
    },
    7: {
        "type_name": "繊細な宝石 (THE IDOL)",
        "catch_copy": "試練を輝きに変える、美しきカリスマ",
        "desc": "あなたは生まれながらにして「特別感」を漂わせる、美意識の高い人です。試練を糧にして人間的な深みや魅力を増していきます。",
        "work_style_title": "質を極めるスペシャリスト",
        "work": "泥臭い仕事は不向き。美容、宝飾、ITエンジニアなど、細部へのこだわりと美意識が評価される仕事。",
        "love": "自分を特別扱いしてくれる相手でないと続きません。しかし一度愛した相手には深い愛情を注ぎます。",
        "fate_code": "Input(S) Process(R) Output(D) Drive(M)",
        "desire": "特別感・洗練",
        "flaw_desc": "プライドが高く傷つきやすい。自分から謝るのが苦手です。"
    },
    8: {
        "type_name": "自由な冒険家 (THE NOMAD)",
        "catch_copy": "境界を超えて流れる、自由の象徴",
        "desc": "あなたは一箇所に留まることができない、永遠の旅人です。「普通」の枠に収まらない発想を持ち、組織に新しい風を吹き込みます。",
        "work_style_title": "流動的な企画・フリーランス",
        "work": "デスクに縛り付けられる仕事は拷問です。商社、イベント企画、Webマーケターなど、移動や変化が多い仕事。",
        "love": "束縛されると逃げ出します。それぞれの時間を楽しめる自立した関係を求めます。",
        "fate_code": "Input(S) Process(G) Output(I) Drive(M)",
        "desire": "自由・流動",
        "flaw_desc": "責任や約束を重荷に感じ、大事な局面でふらっと消えることがあります。"
    },
    9: {
        "type_name": "癒やしの共感者 (THE COUNSELOR)",
        "catch_copy": "静かに浸透する、慈愛の賢者",
        "desc": "あなたは雨のように静かに、しかし確実に人の心に染み渡る存在です。派手な自己主張はしませんが、驚くほどの知識と知恵を持っています。",
        "work_style_title": "心に寄り添うカウンセラー",
        "work": "競争が激しい環境は消耗します。心理カウンセラー、研究職、秘書など、静かな環境でじっくり向き合う仕事。",
        "love": "心も体も溶け合うような一体感を求めます。献身的に尽くしますが、不満を溜め込みやすいです。",
        "fate_code": "Input(L) Process(R) Output(D) Drive(Y)",
        "desire": "共感・貢献",
        "flaw_desc": "嫌と言えずストレスを溜め込み、突然人間関係をリセットすることがあります。"
    }
}

GAN_ELEMENTS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
GAN_FIVE = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4] 
ZHI_FIVE = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4] 
SOLAR_TERMS = [6, 4, 6, 5, 6, 6, 7, 8, 8, 8, 7, 7] 
ENERGY_STRENGTH = [
    [3, 2, 3, 3, 2, 1, 1, 1, 1, 1, 2, 3], [3, 2, 3, 3, 2, 1, 1, 1, 1, 1, 2, 3],
    [1, 1, 3, 3, 2, 3, 3, 2, 1, 1, 1, 1], [1, 1, 3, 3, 2, 3, 3, 2, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 3, 3, 2, 1, 1, 1, 1], [1, 2, 3, 3, 3, 3, 3, 2, 1, 1, 1, 1],
    [1, 2, 1, 1, 2, 3, 3, 2, 3, 3, 2, 1], [1, 2, 1, 1, 2, 3, 3, 2, 3, 3, 2, 1],
    [3, 2, 1, 1, 2, 1, 1, 1, 3, 3, 2, 3], [3, 2, 1, 1, 2, 1, 1, 1, 3, 3, 2, 3]
]

# ==========================================
# 4. Logic Engines
# ==========================================

def calculate_big5(answers):
    scores_raw = {
        "Extraversion": answers["Q1"] + (8 - answers["Q6"]),
        "Agreeableness": (8 - answers["Q2"]) + answers["Q7"],
        "Conscientiousness": answers["Q3"] + (8 - answers["Q8"]),
        "Neuroticism": answers["Q4"] + (8 - answers["Q9"]),
        "Openness": answers["Q5"] + (8 - answers["Q10"])
    }
    scores_norm = {k: round(1 + (v - 2) * 4 / 12, 1) for k, v in scores_raw.items()}
    return scores_raw, scores_norm

def get_gap_hook(fate_type_id, scores_norm):
    """
    宿命(Type)と現在(Big5)のギャップを判定し、フック文章を返す
    """
    is_gap = False
    
    # Type 0,2,6 (外向型) vs Extraversion
    if fate_type_id in [0, 2, 6] and scores_norm["Extraversion"] < 2.5:
        is_gap = True
    # Type 1,9 (協調型) vs Agreeableness
    elif fate_type_id in [1, 9] and scores_norm["Agreeableness"] < 2.5:
        is_gap = True
    # Type 4,7 (堅実型) vs Conscientiousness
    elif fate_type_id in [4, 7] and scores_norm["Conscientiousness"] < 2.5:
        is_gap = True
        
    if is_gap:
        return "WARNING", "⚠️ 注意：あなたの本来の強みが、現在60%死んでいます。"
    else:
        return "SUCCESS", "✨ 素晴らしい：宿命通りに才能が発揮されています。ただし…"

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
        targets = [(GAN_FIVE[y_gan], 1), (GAN_FIVE[m_gan], 1), (ZHI_FIVE[y_zhi], 1), (ZHI_FIVE[m_zhi], 2), (ZHI_FIVE[zhi], 1)]
        for five_el, weight in targets:
            cat = self.get_star_category(gan, five_el)
            counts[cat] += weight

        normalized_scores = {}
        for k, v in counts.items():
            score_5 = 1 if v==0 else (2 if v==1 else (3 if v==2 else (4 if v==3 else 5)))
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

        return {"gan": gan, "scores": normalized_scores, "fate_code": fate_code}

# ==========================================
# 5. Main UI Application
# ==========================================

st.title("Project MAP")

# タブ区分
main_tab, catalog_tab = st.tabs(["DIAGNOSIS", "ALL TYPES"])

# --- Tab 1: 診断 ---
with main_tab:
    # A. 入力フォーム
    with st.form("diagnosis_form"):
        st.markdown("### 1. 生年月日")
        col_y, col_m, col_d = st.columns([1.2, 1, 1])
        with col_y: year = st.selectbox("年", list(range(1900, 2031)), index=95)
        with col_m: month = st.selectbox("月", list(range(1, 13)), index=0)
        with col_d: day = st.selectbox("日", list(range(1, 32)), index=0)
            
        st.markdown("---")
        st.markdown("### 2. 科学的性格診断 (TIPI-J)")
        st.caption("直感で答えてください（1:全く違う 〜 7:強くそう思う）")
        
        tipi_answers = {}
        for q_id, q_text in TIPI_QUESTIONS.items():
            st.markdown(f"<div class='q-text'>{q_text}</div>", unsafe_allow_html=True)
            tipi_answers[q_id] = st.slider(f"", 1, 7, 4, key=f"form_{q_id}")
            st.markdown("<br>", unsafe_allow_html=True)
            
        submitted = st.form_submit_button("診断結果を見る", type="primary", use_container_width=True)
    
    # B. 結果表示 (Identity=公開, Analysis=寸止め)
    if submitted:
        try:
            date_obj = datetime.date(year, month, day)
            date_str = date_obj.strftime("%Y/%m/%d")
            
            # ロジック実行
            engine = FortuneEngineIntegrated()
            result = engine.analyze_basic(date_str)
            gan_id = result['gan']
            content = DIAGNOSIS_CONTENT[gan_id]
            fate_code = result['fate_code']
            
            # Big Five & Gap Analysis
            _, big5_norm = calculate_big5(tipi_answers)
            status, hook_text = get_gap_hook(gan_id, big5_norm)

            # === AREA 1: IDENTITY (全公開) ===
            st.markdown('<div class="section-title">IDENTITY (宿命)</div>', unsafe_allow_html=True)
            st.markdown('<div class="identity-card">', unsafe_allow_html=True)
            
            st.markdown(f"<div class='identity-name'>{content['type_name']}</div>", unsafe_allow_html=True)
            
            img_path = load_image(gan_id + 1)
            if img_path:
                st.image(img_path, use_container_width=True)
            else:
                st.image("https://placehold.co/400x400/F0F0F0/333?text=No+Image", use_container_width=True)
            
            st.markdown(f"**{content['catch_copy']}**")
            st.markdown(f"<br><span class='fate-chip'>{fate_code}</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # 詳細テキスト (Work/Love/Desire)
            st.markdown('<div class="identity-card" style="text-align:left;">', unsafe_allow_html=True)
            st.markdown("#### 👤 基本性格")
            st.write(content['desc'])
            st.markdown(f"#### ⚔️ {content['work_style_title']}")
            st.write(content['work'])
            st.markdown("#### 💖 恋愛スタイル")
            st.write(content['love'])
            st.markdown("#### 🧠 欲求 (Core Drive)")
            st.write(content['desire'])
            st.markdown('</div>', unsafe_allow_html=True)

            # === AREA 2: ANALYSIS (寸止め・チラ見せ) ===
            st.markdown('<div class="section-title">ANALYSIS (科学的分析)</div>', unsafe_allow_html=True)
            
            # フック文章のみ表示 (赤 or 緑)
            if status == "WARNING":
                st.markdown(f"<div class='hook-text-warning'>{hook_text}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='hook-text-success'>{hook_text}</div>", unsafe_allow_html=True)
            
            # 寸止めエリア (グラフなどはぼかす)
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            
            # ぼかし対象コンテンツ
            st.markdown('<div class="blurred-content">', unsafe_allow_html=True)
            categories = ['外向性', '開放性', '協調性', '勤勉性', '情緒安定']
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=[3,3,3,3,3], theta=categories, fill='toself', name='宿命'))
            fig.add_trace(go.Scatterpolar(r=[2,4,2,4,2], theta=categories, fill='toself', name='現在'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.write("ここに詳細な分析結果が表示されます。あなたの性格の歪みや、ストレス反応、具体的な解決策などが記述されます...")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # CTAボタン (オーバーレイ)
            st.markdown("""
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 80%; text-align: center;">
                <p style="font-weight:bold; background:white; padding:5px;">🔒 続きはLINEで確認</p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("LINEで完全な分析レポートを見る (無料)", "https://line.me/R/ti/p/dummy_id", type="primary", use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        except ValueError:
            st.error("正しい日付を選択してください。")

# --- Tab 2: 図鑑 ---
with catalog_tab:
    st.markdown("### 全10タイプ図鑑")
    cols = st.columns(2)
    for i in range(10):
        c = DIAGNOSIS_CONTENT[i]
        with cols[i % 2]:
            st.markdown('<div class="identity-card" style="padding:15px; margin-bottom:15px;">', unsafe_allow_html=True)
            path = load_image(i + 1)
            if path: st.image(path, use_container_width=True)
            st.caption(f"No.{i+1}")
            st.markdown(f"**{c['type_name']}**")
            st.markdown('</div>', unsafe_allow_html=True)
