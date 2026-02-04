import streamlit as st
import datetime
import plotly.graph_objects as go
import random
import os
import pandas as pd

# ==========================================
# 1. Page Config & CSS (商用デザイン設定)
# ==========================================
st.set_page_config(
    page_title="Project MAP | AI性格診断",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 清潔感のある「カード型デザイン」と「見出し装飾」の定義
st.markdown("""
<style>
    /* 全体の背景とフォント調整 */
    .stApp {
        background-color: #f8f9fa;
        font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", "Hiragino Sans", Meiryo, sans-serif;
    }
    
    /* カード風コンテナのデザイン */
    .stCard {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        margin-bottom: 24px;
    }
    
    /* 左線付きの見出しデザイン */
    .custom-header {
        border-left: 6px solid #00c853; /* アクセントカラー */
        padding-left: 12px;
        font-size: 1.4rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
    }
    
    /* チップデザイン */
    .fate-chip {
        display: inline-block;
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.9rem;
        font-weight: bold;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
    /* ぼかしエリア */
    .blur-container {
        filter: blur(6px);
        opacity: 0.5;
        pointer-events: none;
        user-select: none;
    }
    
    /* キャッチコピー */
    .hero-catch {
        font-size: 1.8rem;
        background: linear-gradient(90deg, #2c3e50, #00c853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Helper Functions (Image Loader)
# ==========================================
def load_image(type_id):
    """画像のパスを柔軟に探す関数"""
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG']
    base_dir = "images"
    
    if not os.path.exists(base_dir):
        return None, f"Error: '{base_dir}' folder not found."
    
    for ext in extensions:
        filename = f"{type_id}{ext}"
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            return file_path, None
            
    return None, f"Image not found for Type {type_id} in {base_dir}"

# ==========================================
# 3. Logic Data & Content Expansion
# ==========================================

# --- FATE Code 解説データ ---
FATE_EXPLANATION = {
    "L": {"title": "Logic (論理)", "desc": "感情よりも事実とデータで判断する知性派。"},
    "S": {"title": "Sense (感覚)", "desc": "直感と美的センスで本質を掴むアーティスト肌。"},
    "R": {"title": "Risk (堅実)", "desc": "石橋を叩いて渡る、リスク管理のプロフェッショナル。"},
    "G": {"title": "Growth (成長)", "desc": "失敗を恐れずに挑戦し、拡大を目指す開拓者。"},
    "I": {"title": "Impulse (衝動)", "desc": "圧倒的なエネルギーで周囲を巻き込むカリスマ。"},
    "D": {"title": "Deliberate (熟考)", "desc": "静かに思考を巡らせ、最適解を導く参謀。"},
    "M": {"title": "Me (自我)", "desc": "「自分らしさ」を貫くことで輝く独立独歩タイプ。"},
    "Y": {"title": "You (協調)", "desc": "他者との関わりの中で価値を生み出すバランサー。"}
}

# --- 診断コンテンツ（拡張版） ---
DIAGNOSIS_CONTENT = {
    0: { # 甲
        "type_name": "No.1 甲：THE LEADER",
        "catch_copy": "折れない信念を持つ、\n孤高の統率者",
        "role_desc": "組織の背骨となるリーダー。迷うメンバーに「道」を示す灯台のような存在です。",
        "flaw_desc": "一度ポキっと心が折れると、再起不能になるガラスのメンタルを持っています。",
        "desire": "尊敬・成長",
        "work_style_title": "一本筋の通った専門職・経営",
        "work_style_desc": "妥協を許さない姿勢は、職人や経営者に最適。自分の裁量でルールを決められる環境でこそ輝きます。"
    },
    1: { # 乙
        "type_name": "No.2 乙：THE CONNECTOR",
        "catch_copy": "したたかに生き残る、\n柔軟な戦略家",
        "role_desc": "どんな過酷な環境でも生き残る調整役。剛腕リーダーの懐に入り操る影の実力者。",
        "flaw_desc": "八方美人になりすぎて、自分が本当はどうしたいのか見失うことがあります。",
        "desire": "調和・安全",
        "work_style_title": "チームの潤滑油・広報",
        "work_style_desc": "人当たりの良さを活かした交渉や、チームビルディングが得意。殺伐とした場を和ませる才能があります。"
    },
    2: { # 丙
        "type_name": "No.3 丙：THE PROTAGONIST",
        "catch_copy": "世界を照らす、\nあくなき挑戦者",
        "role_desc": "そこにいるだけで周囲が明るくなるムードメーカー。失敗を笑い飛ばす陽のエネルギーの塊。",
        "flaw_desc": "「私の話を聞いて！」という自己主張が強く、人の話を聞いていないジャイアン気質。",
        "desire": "注目・称賛",
        "work_style_title": "表舞台に立つプレゼンター",
        "work_style_desc": "ルーティンワークは不向き。営業、広報、芸能など、人前に出て注目を浴びる仕事が天職です。"
    },
    3: { # 丁
        "type_name": "No.4 丁：THE MUSE",
        "catch_copy": "静寂に燃える、\n知性の灯火",
        "role_desc": "物事の本質を鋭く見抜く参謀役。静かながら内側に激しい情熱と独自の美学を秘めています。",
        "flaw_desc": "「言わなくても察してよ」というオーラを出し、勝手に傷ついて爆発する面倒くさい一面も。",
        "desire": "理解・美学",
        "work_style_title": "鋭い洞察を活かすクリエイター",
        "work_style_desc": "コンサルタントや企画職、デザイナーなど、独自の視点と知性を活かして新しい価値を生む仕事に向いています。"
    },
    4: { # 戊
        "type_name": "No.5 戊：THE ANCHOR",
        "catch_copy": "すべてを受け入れる、\n揺るがぬ巨塔",
        "role_desc": "動じない安心感を与える守護神。彼がいるだけで「なんとかなりそう」と思わせる器の大きさ。",
        "flaw_desc": "テコでも動かない頑固オヤジ。変化を嫌い、腰が重すぎてチャンスを逃すことも。",
        "desire": "安定・信頼",
        "work_style_title": "組織を支えるバックオフィス・管理",
        "work_style_desc": "総務、経理、あるいは店舗オーナーなど、どっしりと構えて人や資産を管理・蓄積するポジションが最適です。"
    },
    5: { # 己
        "type_name": "No.6 己：THE NURTURER",
        "catch_copy": "才ある者を育む、\n慈愛の大地",
        "role_desc": "才能を見抜き育てる教育者。複雑なことを噛み砕いて教えるのが天才的に上手い。",
        "flaw_desc": "世話を焼きすぎて相手をダメにする「ダメンズ製造機」。感謝されないと根に持ちます。",
        "desire": "貢献・親密",
        "work_style_title": "人を育てる教育・メンター",
        "work_style_desc": "教育係、カスタマーサクセス、福祉など、直接的に人の役に立ち、感謝される仕事でやりがいを感じます。"
    },
    6: { # 庚
        "type_name": "No.7 庚：THE HERO",
        "catch_copy": "時代を切り拓く、\n鋼の革命家",
        "role_desc": "停滞した空気をぶち壊す起爆剤。正論という武器で悪習を断ち切るスピードスター。",
        "flaw_desc": "デリカシーがなく、正論で相手を追い詰めてしまうため、敵を作りやすい。",
        "desire": "変革・勝利",
        "work_style_title": "改革を推進するプロジェクトリーダー",
        "work_style_desc": "新規事業の立ち上げや、組織改革など、既存の枠組みを壊して新しいルールを作る仕事で輝きます。"
    },
    7: { # 辛
        "type_name": "No.8 辛：THE IDOL",
        "catch_copy": "試練を輝きに変える、\n美しきカリスマ",
        "role_desc": "妥協なき美学を持つ職人。試練を乗り越えるたびに磨かれ、輝きを増す宝石。",
        "flaw_desc": "プライドが高く、傷つきやすい。特別扱いされないとすぐに拗ねるお姫様・王子様。",
        "desire": "特別感・洗練",
        "work_style_title": "質を極めるスペシャリスト",
        "work_style_desc": "美容、宝飾、ITエンジニアなど、細部へのこだわりが評価される「美意識」が問われる仕事が向いています。"
    },
    8: { # 壬
        "type_name": "No.9 壬：THE NOMAD",
        "catch_copy": "境界を超えて流れる、\n自由の象徴",
        "role_desc": "スケールの大きい冒険家。既存の枠に囚われず、新しい情報やトレンドを運ぶ運び屋。",
        "flaw_desc": "責任や束縛が大嫌い。大事な場面で「飽きた」と言ってふらっと消える無責任さも。",
        "desire": "自由・流動",
        "work_style_title": "流動的なフリーランス・企画",
        "work_style_desc": "一箇所に留まらない営業、海外事業、イベント企画など、常に変化と刺激がある環境が必要です。"
    },
    9: { # 癸
        "type_name": "No.10 癸：THE COUNSELOR",
        "catch_copy": "静かに浸透する、\n慈愛の賢者",
        "role_desc": "組織の潤滑油となる知恵袋。派閥争いとは無縁の場所で、静かに人々を癒やす存在。",
        "flaw_desc": "影響を受けやすく、自分がない。ストレスが限界を超えると静かに連絡を断ちフェードアウトします。",
        "desire": "共感・貢献",
        "work_style_title": "心に寄り添うカウンセラー・研究",
        "work_style_desc": "心理カウンセラー、研究職、秘書など、静かな環境で深い知識や洞察力を活かす仕事が向いています。"
    }
}

# --- ロジック定数 ---
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

# ==========================================
# 4. Engine Logic (Ver 7.4 Integrated)
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
# 5. Main UI Application
# ==========================================

# サイドバー
with st.sidebar:
    st.title("🔮 Project MAP")
    st.markdown("生年月日を入力して、あなたの**隠された才能**と**運命の相性**を科学的に分析します。")
    
    input_date = st.date_input("生年月日", datetime.date(2000, 1, 1))
    input_time = st.selectbox("出生時間", ["不明", "00:00-01:59", "02:00-03:59", "04:00-05:59", "06:00-07:59", "08:00-09:59", "10:00-11:59", "12:00-13:59", "14:00-15:59", "16:00-17:59", "18:00-19:59", "20:00-21:59", "22:00-23:59"])
    input_gender = st.selectbox("性別", ["回答しない", "男性", "女性", "その他"])
    
    start_btn = st.button("診断する", type="primary")

# メイン処理
if start_btn:
    engine = FortuneEngineIntegrated()
    date_str = input_date.strftime("%Y/%m/%d")
    result = engine.analyze_basic(date_str)
    
    gan_id = result['gan']
    content = DIAGNOSIS_CONTENT[gan_id]
    scores = result['scores']
    fate_code = result['fate_code']

    # --- Header Section (Card) ---
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        # 画像表示
        type_id = gan_id + 1
        img_path, error_msg = load_image(type_id)
        if img_path:
            st.image(img_path, use_container_width=True)
        else:
            st.warning("画像準備中")
            st.image("https://placehold.co/400x400/f0f0f0/333?text=No+Image", use_container_width=True)

    with col2:
        # タイトル・FATEコード・キャッチコピー
        st.markdown(f"#### FATE CODE: <span style='color:#00c853; font-family:monospace; font-size:1.2em;'>{fate_code}</span>", unsafe_allow_html=True)
        st.title(content['type_name'])
        st.markdown(f"<div class='hero-catch'>{content['catch_copy']}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**基本的欲求 (Core Drive):** {content['desire']}")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- FATE Code Detail Section ---
    st.markdown('<div class="custom-header">🧬 FATE Code Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.write("あなたの行動原理を4つの軸で分解しました。")
    
    f_cols = st.columns(4)
    code_chars = list(fate_code) # ['L', 'R', 'I', 'M']
    labels = ["Input (情報の取り方)", "Process (判断基準)", "Output (行動特性)", "Drive (原動力)"]
    
    for i, char in enumerate(code_chars):
        with f_cols[i]:
            explanation = FATE_EXPLANATION.get(char, {"title": char, "desc": "..."})
            st.markdown(f"**{labels[i]}**")
            st.markdown(f"<div class='fate-chip'>{explanation['title']}</div>", unsafe_allow_html=True)
            st.caption(explanation['desc'])
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Radar Chart & Deep Analysis ---
    st.markdown('<div class="custom-header">📊 才能パラメーター & 欲求分析</div>', unsafe_allow_html=True)
    
    col_r1, col_r2 = st.columns([1, 1])
    
    with col_r1:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        categories = ['Identity (自我)', 'Create (創造)', 'Economy (経済)', 'Status (地位)', 'Vitality (知性)']
        r_values = [scores['Identity'], scores['Create'], scores['Economy'], scores['Status'], scores['Vitality']]
        
        # ライトモード用チャート配色
        fig = go.Figure(data=go.Scatterpolar(
            r=r_values,
            theta=categories,
            fill='toself',
            line_color='#00c853',
            fillcolor='rgba(0, 200, 83, 0.2)'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(color="#666")),
                angularaxis=dict(tickfont=dict(color="#333"))
            ),
            showlegend=False,
            margin=dict(t=20, b=20, l=40, r=40),
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r2:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("#### 💼 Work Style (働き方)")
        st.info(f"**{content['work_style_title']}**")
        st.write(content['work_style_desc'])
        st.markdown("---")
        st.markdown("#### ❤️ 愛すべき欠点")
        st.write(content['flaw_desc'])
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Role & Compatibility ---
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown("#### 🏢 社会的役割")
    st.write(content['role_desc'])
    
    st.markdown("---")
    st.markdown("#### 💞 運命の相性 Best 3")
    
    p_cols = st.columns(3)
    partners = result['partners']
    for i, p_name in enumerate(partners):
        with p_cols[i]:
            st.success(f"**{i+1}位** {p_name}")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- CTA (Locked Section) ---
    st.markdown('<div class="stCard" style="border: 2px solid #00c853;">', unsafe_allow_html=True)
    st.markdown("### 🔒 完全版レポート（無料）")
    
    # ぼかしエリア
    st.markdown('<div class="blur-container">', unsafe_allow_html=True)
    st.write("#### ④ コミュニケーションの癖")
    st.write("あなたが無意識に行ってしまう会話のパターンや、相手に与える印象の詳細分析...")
    st.write("#### ⑤ ストレス時の反応")
    st.write("限界を迎えたときの行動パターンと、そこからの回復方法...")
    st.write("#### ⑥ 科学的ソリューション")
    st.write("認知科学に基づく、あなた専用の行動変容プログラム...")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button(
        label="🔑 LINEで完全版を受け取る（無料）",
        url="https://line.me/R/ti/p/dummy_id", # LINE公式URL
        type="primary",
        use_container_width=True
    )
    st.caption("※ 登録後、すぐに詳細レポートがPDFで届きます。")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # 待機画面
    st.info("👈 サイドバーから生年月日を入力して「診断する」を押してください。")
    st.markdown("""
    <div style="text-align: center; padding: 50px; color: #666;">
        <h2>Project MAP</h2>
        <p>Science x Fortune Telling</p>
    </div>
    """, unsafe_allow_html=True)
