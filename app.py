import streamlit as st
import datetime
import plotly.graph_objects as go
import random
import os
import pandas as pd

# ==========================================
# 1. Page Config & CSS
# ==========================================
st.set_page_config(
    page_title="Project MAP | AI性格診断",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* 全体の背景とフォント調整 */
    .stApp {
        background-color: #f8f9fa;
        font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", "Hiragino Sans", Meiryo, sans-serif;
        color: #333333;
    }
    
    /* カード風コンテナ */
    .stCard {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        margin-bottom: 24px;
    }
    
    /* 左線付き見出し */
    .custom-header {
        border-left: 6px solid #00c853;
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
        border: 1px solid #c8e6c9;
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
        margin-top: 10px;
        margin-bottom: 20px;
    }
    
    /* タイプ名 */
    .type-title {
        font-size: 1.4rem;
        font-weight: bold;
        color: #555;
        margin-bottom: 5px;
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

# TIPI-J (Big Five) 質問項目
TIPI_QUESTIONS = {
    "Q1": "活発で、外向的だと思う",
    "Q2": "他人に不満をもち、もめごとを起こしやすいと思う",
    "Q3": "しっかりしていて、自分に厳しいと思う",
    "Q4": "心配性で、うろたえやすいと思う",
    "Q5": "新しいことが好きで、変わった考えを持つと思う",
    "Q6": "控えめで、おとなしいと思う",
    "Q7": "人に気を使う方で、やさしいと思う",
    "Q8": "だらしなく、うっかりしていると思う",
    "Q9": "冷静で、気分が安定していると思う",
    "Q10": "発想力に欠けた、平凡な人間だと思う"
}

# FATE Code 解説
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

# 診断コンテンツ（最新版名称反映）
DIAGNOSIS_CONTENT = {
    0: {"type_name": "No.1 頼れる親分肌（THE LEADER）", "catch_copy": "折れない信念を持つ、\n孤高の統率者", "role_desc": "組織の背骨となるリーダー。迷うメンバーに「道」を示す灯台のような存在です。", "flaw_desc": "一度ポキっと心が折れると、再起不能になるガラスのメンタルを持っています。", "desire": "尊敬・成長", "work_style_title": "一本筋の通った専門職・経営", "work_style_desc": "妥協を許さない姿勢は、職人や経営者に最適。自分の裁量でルールを決められる環境でこそ輝きます。"},
    1: {"type_name": "No.2 愛され調整役（THE CONNECTOR）", "catch_copy": "したたかに生き残る、\n柔軟な戦略家", "role_desc": "どんな過酷な環境でも生き残る調整役。剛腕リーダーの懐に入り操る影の実力者。", "flaw_desc": "八方美人になりすぎて、自分が本当はどうしたいのか見失うことがあります。", "desire": "調和・安全", "work_style_title": "チームの潤滑油・広報", "work_style_desc": "人当たりの良さを活かした交渉や、チームビルディングが得意。殺伐とした場を和ませる才能があります。"},
    2: {"type_name": "No.3 天性の主人公（THE PROTAGONIST）", "catch_copy": "世界を照らす、\nあくなき挑戦者", "role_desc": "そこにいるだけで周囲が明るくなるムードメーカー。失敗を笑い飛ばす陽のエネルギーの塊。", "flaw_desc": "「私の話を聞いて！」という自己主張が強く、人の話を聞いていないジャイアン気質。", "desire": "注目・称賛", "work_style_title": "表舞台に立つプレゼンター", "work_style_desc": "ルーティンワークは不向き。営業、広報、芸能など、人前に出て注目を浴びる仕事が天職です。"},
    3: {"type_name": "No.4 熱き夢想家（THE MUSE）", "catch_copy": "静寂に燃える、\n知性の灯火", "role_desc": "物事の本質を鋭く見抜く参謀役。静かながら内側に激しい情熱と独自の美学を秘めています。", "flaw_desc": "「言わなくても察してよ」というオーラを出し、勝手に傷ついて爆発する面倒くさい一面も。", "desire": "理解・美学", "work_style_title": "鋭い洞察を活かすクリエイター", "work_style_desc": "コンサルタントや企画職、デザイナーなど、独自の視点と知性を活かして新しい価値を生む仕事に向いています。"},
    4: {"type_name": "No.5 不動の守護神（THE ANCHOR）", "catch_copy": "すべてを受け入れる、\n揺るがぬ巨塔", "role_desc": "動じない安心感を与える守護神。彼がいるだけで「なんとかなりそう」と思わせる器の大きさ。", "flaw_desc": "テコでも動かない頑固オヤジ。変化を嫌い、腰が重すぎてチャンスを逃すことも。", "desire": "安定・信頼", "work_style_title": "組織を支えるバックオフィス・管理", "work_style_desc": "総務、経理、あるいは店舗オーナーなど、どっしりと構えて人や資産を管理・蓄積するポジションが最適です。"},
    5: {"type_name": "No.6 尽くす世話焼き（THE NURTURER）", "catch_copy": "才ある者を育む、\n慈愛の大地", "role_desc": "才能を見抜き育てる教育者。複雑なことを噛み砕いて教えるのが天才的に上手い。", "flaw_desc": "世話を焼きすぎて相手をダメにする「ダメンズ製造機」。感謝されないと根に持ちます。", "desire": "貢献・親密", "work_style_title": "人を育てる教育・メンター", "work_style_desc": "教育係、カスタマーサクセス、福祉など、直接的に人の役に立ち、感謝される仕事でやりがいを感じます。"},
    6: {"type_name": "No.7 正義の切り込み隊長（THE HERO）", "catch_copy": "時代を切り拓く、\n鋼の革命家", "role_desc": "停滞した空気をぶち壊す起爆剤。正論という武器で悪習を断ち切るスピードスター。", "flaw_desc": "デリカシーがなく、正論で相手を追い詰めてしまうため、敵を作りやすい。", "desire": "変革・勝利", "work_style_title": "改革を推進するプロジェクトリーダー", "work_style_desc": "新規事業の立ち上げや、組織改革など、既存の枠組みを壊して新しいルールを作る仕事で輝きます。"},
    7: {"type_name": "No.8 繊細な宝石（THE IDOL）", "catch_copy": "試練を輝きに変える、\n美しきカリスマ", "role_desc": "妥協なき美学を持つ職人。試練を乗り越えるたびに磨かれ、輝きを増す宝石。", "flaw_desc": "プライドが高く、傷つきやすい。特別扱いされないとすぐに拗ねるお姫様・王子様。", "desire": "特別感・洗練", "work_style_title": "質を極めるスペシャリスト", "work_style_desc": "美容、宝飾、ITエンジニアなど、細部へのこだわりが評価される「美意識」が問われる仕事が向いています。"},
    8: {"type_name": "No.9 自由な冒険家（THE NOMAD）", "catch_copy": "境界を超えて流れる、\n自由の象徴", "role_desc": "スケールの大きい冒険家。既存の枠に囚われず、新しい情報やトレンドを運ぶ運び屋。", "flaw_desc": "責任や束縛が大嫌い。大事な場面で「飽きた」と言ってふらっと消える無責任さも。", "desire": "自由・流動", "work_style_title": "流動的なフリーランス・企画", "work_style_desc": "一箇所に留まらない営業、海外事業、イベント企画など、常に変化と刺激がある環境が必要です。"},
    9: {"type_name": "No.10 癒やしの共感者（THE COUNSELOR）", "catch_copy": "静かに浸透する、\n慈愛の賢者", "role_desc": "組織の潤滑油となる知恵袋。派閥争いとは無縁の場所で、静かに人々を癒やす存在。", "flaw_desc": "影響を受けやすく、自分がない。ストレスが限界を超えると静かに連絡を断ちフェードアウトします。", "desire": "共感・貢献", "work_style_title": "心に寄り添うカウンセラー・研究", "work_style_desc": "心理カウンセラー、研究職、秘書など、静かな環境で深い知識や洞察力を活かす仕事が向いています。"}
}

# --- 占術パラメータ定数 ---
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
COMPATIBILITY_MAP = {
    0: ["No.6 尽くす世話焼き", "No.7 正義の切り込み隊長", "No.4 熱き夢想家"], 1: ["No.7 正義の切り込み隊長", "No.8 繊細な宝石", "No.3 天性の主人公"],
    2: ["No.8 繊細な宝石", "No.9 自由な冒険家", "No.5 不動の守護神"], 3: ["No.9 自由な冒険家", "No.10 癒やしの共感者", "No.6 尽くす世話焼き"],
    4: ["No.10 癒やしの共感者", "No.1 頼れる親分肌", "No.7 正義の切り込み隊長"], 5: ["No.1 頼れる親分肌", "No.2 愛され調整役", "No.8 繊細な宝石"],
    6: ["No.2 愛され調整役", "No.3 天性の主人公", "No.9 自由な冒険家"], 7: ["No.3 天性の主人公", "No.4 熱き夢想家", "No.10 癒やしの共感者"],
    8: ["No.4 熱き夢想家", "No.5 不動の守護神", "No.1 頼れる親分肌"], 9: ["No.5 不動の守護神", "No.6 尽くす世話焼き", "No.2 愛され調整役"]
}

# ==========================================
# 4. Big Five & Analysis Functions
# ==========================================
def calculate_big5(answers):
    scores_raw = {
        "Extraversion": answers["Q1"] + (8 - answers["Q6"]),
        "Agreeableness": (8 - answers["Q2"]) + answers["Q7"],
        "Conscientiousness": answers["Q3"] + (8 - answers["Q8"]),
        "Neuroticism": answers["Q4"] + (8 - answers["Q9"]),
        "Openness": answers["Q5"] + (8 - answers["Q10"])
    }
    scores_normalized = {}
    for k, v in scores_raw.items():
        norm = 1 + (v - 2) * 4 / 12
        scores_normalized[k] = round(norm, 1)
    return scores_raw, scores_normalized

def get_big5_analysis(scores_norm):
    analysis_text = ""
    high_traits = [k for k, v in scores_norm.items() if v >= 3.8]
    low_traits = [k for k, v in scores_norm.items() if v <= 2.2]
    
    translate = {
        "Extraversion": "外向性", "Agreeableness": "協調性", 
        "Conscientiousness": "勤勉性", "Neuroticism": "神経症傾向", "Openness": "開放性"
    }
    
    if high_traits:
        traits_str = "、".join([translate[t] for t in high_traits])
        analysis_text += f"**🌟 強みと特徴:**\nあなたは「{traits_str}」が非常に高い傾向にあります。これは、社会的な場面や新しい環境で大きな武器となります。\n\n"
    if low_traits:
        traits_str = "、".join([translate[t] for t in low_traits])
        analysis_text += f"**⚠️ 注意点:**\n「{traits_str}」が控えめな数値が出ています。これは慎重さや落ち着きの裏返しでもありますが、意識して行動することでバランスが整います。"
    if not high_traits and not low_traits:
        analysis_text += "**⚖️ バランス型:**\n全ての要素が平均的で、極端な偏りがありません。状況に合わせて柔軟に対応できるバランス感覚の持ち主です。"
    return analysis_text

# ==========================================
# 5. Fortune Engine (Ver 7.4)
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

        return {"gan": gan, "scores": normalized_scores, "fate_code": fate_code, "partners": COMPATIBILITY_MAP.get(gan, [])}

# ==========================================
# 6. Main UI Application
# ==========================================

# サイドバー
with st.sidebar:
    st.title("🔮 Project MAP")
    
    with st.expander("Step 1: 生年月日（必須）", expanded=True):
        # ★改善点：日付入力の範囲を1900-2030に拡大し、デフォルトを1995年に設定
        input_date = st.date_input(
            "生年月日", 
            value=datetime.date(1995, 1, 1),
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date(2030, 12, 31)
        )
        input_time = st.selectbox("出生時間", ["不明", "00:00-01:59", "02:00-03:59", "04:00-05:59", "06:00-07:59", "08:00-09:59", "10:00-11:59", "12:00-13:59", "14:00-15:59", "16:00-17:59", "18:00-19:59", "20:00-21:59", "22:00-23:59"])
        input_gender = st.selectbox("性別", ["回答しない", "男性", "女性", "その他"])

    with st.expander("Step 2: 科学的性格診断（任意）", expanded=False):
        st.caption("「1.全く違う」〜「7.強くそう思う」で回答してください")
        tipi_answers = {}
        for q_id, q_text in TIPI_QUESTIONS.items():
            tipi_answers[q_id] = st.slider(f"{q_text}", 1, 7, 4, key=q_id)
            
    start_btn = st.button("診断する", type="primary")

# メイン処理
if start_btn:
    engine = FortuneEngineIntegrated()
    date_str = input_date.strftime("%Y/%m/%d")
    result = engine.analyze_basic(date_str)
    
    gan_id = result['gan']
    content = DIAGNOSIS_CONTENT[gan_id]
    fate_scores = result['scores']
    fate_code = result['fate_code']
    
    # Big Five 計算
    _, big5_norm = calculate_big5(tipi_answers)
    
    # --- Header Section (順序変更: 名前 -> 画像 -> FATE Code) ---
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    
    # 1. 名前とキャッチコピー (一番上)
    st.markdown(f"<div class='type-title'>{content['type_name']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-catch'>{content['catch_copy']}</div>", unsafe_allow_html=True)
    
    # 2. キャラクター画像 (真ん中、中央揃え)
    type_id = gan_id + 1
    img_path, error_msg = load_image(type_id)
    
    col_img1, col_img2, col_img3 = st.columns([1, 2, 1]) # 画像を中央に寄せるためのカラム
    with col_img2:
        if img_path:
            st.image(img_path, use_container_width=True)
        else:
            st.image("https://placehold.co/400x400/f0f0f0/333?text=No+Image", use_container_width=True)
    
    # 3. FATE Codeと欲求 (画像の下)
    st.markdown(f"<div style='text-align: center; margin-top: 15px;'>", unsafe_allow_html=True)
    st.markdown(f"<span class='fate-chip'>FATE CODE: {fate_code}</span>", unsafe_allow_html=True)
    st.markdown(f"**Core Drive:** {content['desire']}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- FATE Code Detail ---
    st.markdown('<div class="custom-header">🧬 FATE Code Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    f_cols = st.columns(4)
    code_chars = list(fate_code)
    labels = ["Input", "Process", "Output", "Drive"]
    for i, char in enumerate(code_chars):
        with f_cols[i]:
            explanation = FATE_EXPLANATION.get(char, {"title": char, "desc": "..."})
            st.markdown(f"**{labels[i]}**")
            st.markdown(f"<div class='fate-chip'>{explanation['title']}</div>", unsafe_allow_html=True)
            st.caption(explanation['desc'])
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Dual Radar Chart ---
    st.markdown('<div class="custom-header">📊 宿命(Fate) vs 現在(Science)</div>', unsafe_allow_html=True)
    col_r1, col_r2 = st.columns([1, 1])
    
    with col_r1:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        categories = ['Identity / 外向性', 'Create / 開放性', 'Economy / 協調性', 'Status / 勤勉性', 'Vitality / 安定性']
        fate_vals = [fate_scores['Identity'], fate_scores['Create'], fate_scores['Economy'], fate_scores['Status'], fate_scores['Vitality']]
        science_vals = [big5_norm['Extraversion'], big5_norm['Openness'], big5_norm['Agreeableness'], big5_norm['Conscientiousness'], 6 - big5_norm['Neuroticism']]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=fate_vals, theta=categories, fill='toself', name='Fate (宿命)', line_color='#00c853', opacity=0.7))
        fig.add_trace(go.Scatterpolar(r=science_vals, theta=categories, fill='toself', name='Personality (現在)', line_color='#2962ff', opacity=0.6))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(t=30, b=20, l=40, r=40), height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("※緑: 生来の資質 / 青: 現在の性格")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r2:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("#### 🧬 科学的分析レポート")
        st.write(get_big5_analysis(big5_norm))
        st.markdown("---")
        st.markdown("#### ❤️ 愛すべき欠点 (Fate)")
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

    # --- CTA ---
    st.markdown('<div class="stCard" style="border: 2px solid #00c853;">', unsafe_allow_html=True)
    st.markdown("### 🔒 完全版レポート（無料）")
    st.markdown('<div class="blur-container">', unsafe_allow_html=True)
    st.write("#### ④ コミュニケーションの癖 / ⑤ ストレス時の反応 / ⑥ 科学的ソリューション")
    st.write("認知科学に基づく、あなた専用の行動変容プログラム...")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button("🔑 LINEで完全版を受け取る（無料）", "https://line.me/R/ti/p/dummy_id", type="primary", use_container_width=True)
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
