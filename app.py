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
    /* 全体設定 */
    .stApp {
        background-color: #f8f9fa;
        font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", "Hiragino Sans", Meiryo, sans-serif;
        color: #333333;
    }
    
    /* カードデザイン */
    .stCard {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        margin-bottom: 24px;
    }
    
    /* 見出しデザイン */
    .custom-header {
        border-left: 6px solid #00c853;
        padding-left: 12px;
        font-size: 1.4rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 20px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
    }
    
    /* FATE Codeチップ */
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
        font-size: 1.5rem;
        background: linear-gradient(90deg, #2c3e50, #00c853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        line-height: 1.4;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    
    /* タブのスタイル調整 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
        font-weight: bold;
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
    "Q1": "活発で、外向的だと思う", "Q2": "他人に不満をもち、もめごとを起こしやすいと思う",
    "Q3": "しっかりしていて、自分に厳しいと思う", "Q4": "心配性で、うろたえやすいと思う",
    "Q5": "新しいことが好きで、変わった考えを持つと思う", "Q6": "控えめで、おとなしいと思う",
    "Q7": "人に気を使う方で、やさしいと思う", "Q8": "だらしなく、うっかりしていると思う",
    "Q9": "冷静で、気分が安定していると思う", "Q10": "発想力に欠けた、平凡な人間だと思う"
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

# 診断コンテンツ（完全版：ここが重要です）
DIAGNOSIS_CONTENT = {
    0: { # 甲
        "type_name": "No.1 頼れる親分肌（THE LEADER）",
        "catch_copy": "折れない信念を持つ、\n孤高の統率者",
        "desc": "あなたは大樹のように真っ直ぐで、曲がったことが大嫌いな正義の人です。混乱した状況でも一本の道筋を示すことができるリーダーシップを持っており、周囲から「この人についていけば大丈夫」という絶対的な信頼を集めます。",
        "work_style_title": "一本筋の通った専門職・経営",
        "work": "自分の裁量でルールを決められる環境が最適です。誰かの指示に従うだけの仕事や、曖昧な忖度が求められる組織では窒息します。経営者、専門職、PMなど、責任と権限がセットになったポジションでこそ真価を発揮します。",
        "love": "恋愛においても「尊敬できるかどうか」が最重要基準。チャラチャラした相手や、芯のない相手には心が動きません。パートナーには、互いに自立し高め合える対等な関係を求めます。",
        "fate_code": "Input(論理)→Process(堅実)→Output(熟考)→Drive(自我)",
        "desire": "尊敬・成長",
        "flaw_desc": "融通ゼロ。正論で相手を追い詰め、孤立することがあります。「負けるが勝ち」を覚えましょう。"
    },
    1: { # 乙
        "type_name": "No.2 愛され調整役（THE CONNECTOR）",
        "catch_copy": "したたかに生き残る、\n柔軟な戦略家",
        "desc": "あなたはどんな環境でも、草花のように柔軟に形を変えて生き残るサバイバーです。表立って争うことを避け、笑顔で周囲を調整しながら、いつの間にか自分に有利なポジションを確保する賢さがあります。",
        "work_style_title": "チームの潤滑油・広報",
        "work": "殺伐とした会議を和ませたり、利害関係を調整したりする能力は天才的。広報、人事、秘書、またはコミュニティマネージャーなど、人と人を繋ぐハブとなる仕事が天職です。",
        "love": "常に誰かと繋がっていたい寂しがり屋。パートナーには、強いリーダーシップで自分を守ってくれる人か、自分の世話焼きを受け入れてくれる人を求めます。LINEの返信速度など目に見える愛情表現を重視します。",
        "fate_code": "Input(感覚)→Process(成長)→Output(衝動)→Drive(協調)",
        "desire": "調和・安全",
        "flaw_desc": "八方美人すぎて「で、本音は？」と言われがち。依存心が強く、決断を人任せにする癖があります。"
    },
    2: { # 丙
        "type_name": "No.3 天性の主人公（THE PROTAGONIST）",
        "catch_copy": "世界を照らす、\nあくなき挑戦者",
        "desc": "あなたはそこにいるだけでその場がパッと明るくなる、太陽のような存在です。裏表がなく、感情がすべて顔に出るため、誰からも愛されます。「なんとかなる！」という根拠のない自信で突き進むパワーを持っています。",
        "work_style_title": "表舞台に立つプレゼンター",
        "work": "ルーティンワークは死ぬほど退屈します。営業、広報、YouTuber、タレントなど、自分の個性やキャラクターを売り込む仕事が最適。短期集中型で、立ち上げ期に圧倒的な爆発力を発揮します。",
        "love": "恋愛は直感型。「好き！」と思ったら即アプローチします。相手には、自分の話をニコニコ聞いてくれて、常に「すごいね！」と褒めてくれるファン第一号のような存在を求めます。",
        "fate_code": "Input(感覚)→Process(成長)→Output(衝動)→Drive(自我)",
        "desire": "注目・称賛",
        "flaw_desc": "「私の話を聞け！」なジャイアン気質。人の話を聞いているようで、次は自分が何を話そうか考えています。"
    },
    3: { # 丁
        "type_name": "No.4 熱き夢想家（THE MUSE）",
        "catch_copy": "静寂に燃える、\n知性の灯火",
        "desc": "あなたは一見穏やかで物静かですが、内側にはドロドロとした情熱や独自の美学、そして反骨精神を秘めています。鋭い洞察力を持ち、誰も気づかないような微細な変化や本質を見抜くことができます。",
        "work_style_title": "鋭い洞察を活かすクリエイター",
        "work": "感性と知性を融合させる仕事が向いています。デザイナー、ライター、戦略コンサルタントなど、独自の視点で新しい価値を生み出す職種。また、組織のNo.2としての参謀役としても優秀です。",
        "love": "言葉にしなくても通じ合える、深い精神的な繋がりを求めます。表面的な付き合いは苦手で、少数の理解者と濃密な関係を築きます。一度心を許すと非常に一途です。",
        "fate_code": "Input(論理)→Process(堅実)→Output(熟考)→Drive(自我)",
        "desire": "理解・美学",
        "flaw_desc": "察してちゃん界のラスボス。言葉にせず「わかってよ」オーラを出し、勝手に傷つく面倒くさい一面も。"
    },
    4: { # 戊
        "type_name": "No.5 不動の守護神（THE ANCHOR）",
        "catch_copy": "すべてを受け入れる、\n揺るがぬ巨塔",
        "desc": "あなたはちょっとやそっとのことでは動じない、圧倒的な包容力の持ち主です。相談事をされると「うんうん」と聞いているだけで相手を安心させてしまう、人間パワースポットのような器の大きさがあります。",
        "work_style_title": "組織を支えるバックオフィス・管理",
        "work": "変化の激しい現場よりも、どっしりと構えて全体を見渡すポジションが向いています。総務、経理、不動産管理、あるいは店舗オーナーなど。一度築いたシステムや資産を守り育てる能力に長けています。",
        "love": "刺激的な恋よりも、穏やかで家庭的な関係を望みます。パートナーには誠実さと、自分のペースを乱さないことを求めます。自分から動くのは苦手なので、少し強引に引っ張ってくれる相手との相性が良いでしょう。",
        "fate_code": "Input(論理)→Process(堅実)→Output(熟考)→Drive(協調)",
        "desire": "安定・信頼",
        "flaw_desc": "テコでも動かない頑固オヤジ。変化を嫌い、現状維持バイアスがかかりすぎてチャンスを逃すことも。"
    },
    5: { # 己
        "type_name": "No.6 尽くす世話焼き（THE NURTURER）",
        "catch_copy": "才ある者を育む、\n慈愛の大地",
        "desc": "あなたは困っている人を放っておけない、根っからの教育者でありサポーターです。自分自身がトップに立つよりも、他人の才能を見抜き、育て、輝かせることに無上の喜びを感じます。",
        "work_style_title": "人を育てる教育・メンター",
        "work": "教師、インストラクター、カスタマーサクセス、福祉関係など、直接的に人の役に立つ仕事が天職です。また、データの整理や収集など、地味だが重要な作業をコツコツ積み上げることも得意とします。",
        "love": "「あなたのためなら」と尽くすタイプ。少し頼りない、放っておけない相手を好きになりがちです。結婚後は家族を何よりも大切にする良き夫・良き妻になります。",
        "fate_code": "Input(感覚)→Process(成長)→Output(熟考)→Drive(協調)",
        "desire": "貢献・親密",
        "flaw_desc": "尽くしすぎてダメンズ製造機。感謝の見返りがないと「あんなにしてあげたのに」と愚痴っぽくなります。"
    },
    6: { # 庚
        "type_name": "No.7 正義の切り込み隊長（THE HERO）",
        "catch_copy": "時代を切り拓く、\n鋼の革命家",
        "desc": "あなたは「それはおかしい」と声を上げ、古い体制や悪習を一刀両断する改革者です。白黒ハッキリつけないと気が済まない性格で、そのスピード感と決断力は組織の停滞を打破する起爆剤となります。",
        "work_style_title": "改革を推進するプロジェクトリーダー",
        "work": "新規事業の立ち上げ、組織改革、外科医、警察官など、正義感とスピード決断が求められる現場。または、エンジニアとしてバグを潰していくような、論理的かつ攻撃的な解決能力を活かせる仕事が向いています。",
        "love": "駆け引きは大の苦手。好きなら好きとはっきり伝えます。パートナーには、自分と同じくらい自立していて、議論ができる知的な相手を求めます。ウジウジ悩む相手にはイライラしてしまうことも。",
        "fate_code": "Input(論理)→Process(成長)→Output(衝動)→Drive(自我)",
        "desire": "変革・勝利",
        "flaw_desc": "デリカシー？何それ美味しいの？ 正論というナイフで相手を滅多刺しにしてしまうことがあります。"
    },
    7: { # 辛
        "type_name": "No.8 繊細な宝石（THE IDOL）",
        "catch_copy": "試練を輝きに変える、\n美しきカリスマ",
        "desc": "あなたは生まれながらにして「特別感」を漂わせる、美意識の高い人です。宝石が研磨されて輝くように、人生の試練や苦労を糧にして、人間的な深みや魅力を増していきます。感受性が鋭く、独自のセンスを持っています。",
        "work_style_title": "質を極めるスペシャリスト",
        "work": "泥臭い仕事や、粗雑な環境は耐えられません。美容、ファッション、宝飾、ITエンジニアなど、細部へのこだわりと美意識が評価される仕事。あるいは「あなたにしかできない」と指名されるようなブランド力を持つ仕事。",
        "love": "自分を「お姫様・王子様」として扱ってくれる相手でないと続きません。デートの場所やプレゼントのセンスにも厳しく、スマートなエスコートを求めます。しかし、一度愛した相手には深い愛情を注ぎます。",
        "fate_code": "Input(感覚)→Process(堅実)→Output(熟考)→Drive(自我)",
        "desire": "特別感・洗練",
        "flaw_desc": "メンタル強度スライム級のワガママ。プライドが高く、自分から謝るのが死ぬほど嫌いです。"
    },
    8: { # 壬
        "type_name": "No.9 自由な冒険家（THE NOMAD）",
        "catch_copy": "境界を超えて流れる、\n自由の象徴",
        "desc": "あなたは一箇所に留まることができない、永遠の旅人です。スケールが大きく、常に新しい刺激や知識を求めて流動しています。「普通こうだよね」という枠に収まらない発想を持ち、組織に新しい風を吹き込みます。",
        "work_style_title": "流動的なフリーランス・企画",
        "work": "デスクに縛り付けられる仕事は拷問です。商社、貿易、イベント企画、Webマーケターなど、移動や変化が多い仕事。または、複数の拠点を持ち、プロジェクト単位で動くフリーランス的な働き方が最も能力を発揮します。",
        "love": "束縛されると窒息して逃げ出します。「どこで何してるの？」と聞かれるのが大嫌い。パートナーには、それぞれの時間を楽しみ、会った時には刺激的な会話ができるような、自立した大人の関係を求めます。",
        "fate_code": "Input(感覚)→Process(成長)→Output(衝動)→Drive(自我)",
        "desire": "自由・流動",
        "flaw_desc": "ふらっと消える音信不通の常習犯。責任や約束を重荷に感じ、大事な局面で逃亡することも。"
    },
    9: { # 癸
        "type_name": "No.10 癒やしの共感者（THE COUNSELOR）",
        "catch_copy": "静かに浸透する、\n慈愛の賢者",
        "desc": "あなたは雨のように静かに、しかし確実に大地（人の心）に染み渡る存在です。派手な自己主張はしませんが、驚くほどの知識と知恵を持っており、ここぞという時に核心を突くアドバイスをします。",
        "work_style_title": "心に寄り添うカウンセラー・研究",
        "work": "競争が激しい環境や、ノルマに追われる仕事は消耗します。心理カウンセラー、研究職、秘書、占い師など、静かな環境でじっくりと物事や人と向き合う仕事。また、裏方として組織の知能中枢を担う役割も適しています。",
        "love": "愛する人とは心も体も溶け合うような一体感を求めます。相手の色に染まることができ、献身的に尽くします。しかし、不満を溜め込みやすいため、ある日突然何も言わずに「サイレント・ブロック」をして関係を絶つことがあります。",
        "fate_code": "Input(論理)→Process(堅実)→Output(熟考)→Drive(協調)",
        "desire": "共感・貢献",
        "flaw_desc": "影響受けすぎ！な自分がないスライム。嫌と言えずストレスを溜め込み、突然人間関係をリセットします。"
    }
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
# 4. Logic Engines (Fortune & Science)
# ==========================================

# --- 科学的性格診断ロジック (Big Five) ---
def calculate_big5(answers):
    scores_raw = {
        "Extraversion": answers["Q1"] + (8 - answers["Q6"]),
        "Agreeableness": (8 - answers["Q2"]) + answers["Q7"],
        "Conscientiousness": answers["Q3"] + (8 - answers["Q8"]),
        "Neuroticism": answers["Q4"] + (8 - answers["Q9"]),
        "Openness": answers["Q5"] + (8 - answers["Q10"])
    }
    # 1-5段階へ正規化 (2-14点 -> 1-5点)
    scores_norm = {k: round(1 + (v - 2) * 4 / 12, 1) for k, v in scores_raw.items()}
    return scores_raw, scores_norm

def analyze_big5(scores_norm, fate_type_id):
    """
    BigFiveスコアの詳細分析と、宿命(Type)とのギャップ分析を行う
    """
    analysis = []
    
    # 1. 各パラメータの個別アドバイス
    if scores_norm["Conscientiousness"] <= 2.5:
        analysis.append("⚠️ **勤勉性が低めです:** アドリブに強い反面、計画性が不足しがち。締め切り直前で慌てないよう、タスク管理ツールを活用して「仕組み」でカバーしましょう。")
    if scores_norm["Neuroticism"] >= 4.0:
        analysis.append("🧠 **感受性が非常に高いです:** 小さなミスや他人の言動を気にしすぎる傾向があります。「まあいいか」を口癖にし、意識的に鈍感になる練習が必要です。")
    if scores_norm["Openness"] >= 4.0:
        analysis.append("✨ **高い開放性:** 新しいもの好きで好奇心旺盛。ルーティンワークは苦痛になるため、常に新しい刺激がある環境に身を置くことが幸福の鍵です。")
    
    # 2. 宿命とのギャップ分析
    warnings = []
    if fate_type_id in [0, 2, 6] and scores_norm["Extraversion"] < 2.5:
        warnings.append("本来は人を引っ張る力を持っていますが、現在は少し自信を失って内向的になっているかもしれません。小さな成功体験を積み重ねて、本来の輝きを取り戻しましょう。")
    if fate_type_id in [1, 9] and scores_norm["Agreeableness"] < 2.5:
        warnings.append("本来は人との和を大切にするタイプですが、現在は人間関係に疲れ、心を閉ざしている可能性があります。一人の時間を確保して、メンタルを回復させましょう。")
    if fate_type_id in [4, 7] and scores_norm["Conscientiousness"] < 2.5:
        warnings.append("本来は独自のこだわりや安定感を持つ人ですが、現在は生活リズムが乱れているかもしれません。ルーティンを見直すことで運気が安定します。")

    return analysis, warnings

# --- 運命分析ロジック (Fortune Engine) ---
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
# 6. Main UI Application (Tab Structure)
# ==========================================

# サイドバー入力
with st.sidebar:
    st.title("🔮 Project MAP")
    with st.expander("Step 1: 生年月日（必須）", expanded=True):
        input_date = st.date_input("生年月日", value=datetime.date(1995, 1, 1), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2030, 12, 31))
        input_time = st.selectbox("出生時間", ["不明", "00:00-01:59", "02:00-03:59", "etc"])
        input_gender = st.selectbox("性別", ["回答しない", "男性", "女性", "その他"])
    start_btn = st.button("診断する", type="primary")

if start_btn:
    engine = FortuneEngineIntegrated()
    date_str = input_date.strftime("%Y/%m/%d")
    result = engine.analyze_basic(date_str)
    gan_id = result['gan']
    content = DIAGNOSIS_CONTENT[gan_id]
    fate_scores = result['scores']
    
    # タブの定義
    tab1, tab2, tab3 = st.tabs(["📜 宿命の地図", "🧬 科学的分析", "🚀 戦略レポート"])

    # --- Tab 1: 宿命の地図 (Fortune View) ---
    with tab1:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        # 1. Title & Image
        st.markdown(f"<div class='type-title'>{content['type_name']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='hero-catch'>{content['catch_copy']}</div>", unsafe_allow_html=True)
        
        type_id = gan_id + 1
        img_path, _ = load_image(type_id)
        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
        with col_img2:
            if img_path: st.image(img_path, use_container_width=True)
            else: st.image("https://placehold.co/400x400/f0f0f0/333?text=No+Image", use_container_width=True)
        
        st.markdown(f"<div style='text-align:center;'><span class='fate-chip'>FATE CODE: {result['fate_code']}</span></div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. Basic Description
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("#### 👤 あなたの本質")
        st.write(content['desc'])
        st.markdown("---")
        st.markdown(f"**❤️ 愛すべき欠点:** {content['flaw_desc']}")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Tab 2: 科学的分析 (Science View) ---
    with tab2:
        st.info("👇 以下の10問に直感で答えると、科学的な性格分析グラフが追加されます。")
        
        # Input Form
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        tipi_answers = {}
        for q_id, q_text in TIPI_QUESTIONS.items():
            tipi_answers[q_id] = st.slider(f"{q_text}", 1, 7, 4, key=f"t2_{q_id}")
        st.markdown('</div>', unsafe_allow_html=True)

        # Analysis Result
        _, big5_norm = calculate_big5(tipi_answers)
        analysis_text, warnings = analyze_big5(big5_norm, gan_id)

        # Dual Chart
        st.markdown('<div class="custom-header">📊 宿命 vs 現在のギャップ</div>', unsafe_allow_html=True)
        col_chart, col_text = st.columns([1, 1])
        
        with col_chart:
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            categories = ['Identity/外向', 'Create/開放', 'Economy/協調', 'Status/勤勉', 'Vitality/安定']
            fate_vals = [fate_scores['Identity'], fate_scores['Create'], fate_scores['Economy'], fate_scores['Status'], fate_scores['Vitality']]
            science_vals = [big5_norm['Extraversion'], big5_norm['Openness'], big5_norm['Agreeableness'], big5_norm['Conscientiousness'], 6 - big5_norm['Neuroticism']]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=fate_vals, theta=categories, fill='toself', name='Fate(宿命)', line_color='#00c853', opacity=0.6))
            fig.add_trace(go.Scatterpolar(r=science_vals, theta=categories, fill='toself', name='Science(現在)', line_color='#2962ff', opacity=0.5))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True, margin=dict(t=20, b=20, l=40, r=40), height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_text:
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            st.write(analysis_text)
            if warnings:
                st.markdown("---")
                st.error("🚨 **宿命とのギャップ検知:**")
                for w in warnings: st.write(f"- {w}")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- Tab 3: 戦略レポート (Strategy View) ---
    with tab3:
        st.markdown('<div class="custom-header">💼 Work & Love Strategy</div>', unsafe_allow_html=True)
        
        col_w, col_l = st.columns(2)
        with col_w:
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            st.markdown(f"#### ⚔️ {content['work_style_title']}")
            st.write(content['work'])
            st.markdown('</div>', unsafe_allow_html=True)
        with col_l:
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            st.markdown("#### 💖 恋愛・パートナーシップ")
            st.write(content['love'])
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("#### 💞 運命の相性 Best 3")
        for i, p in enumerate(result['partners']):
            st.success(f"**{i+1}位** {p}")
        st.markdown('</div>', unsafe_allow_html=True)

        # CTA
        st.markdown('<div class="stCard" style="border: 2px solid #00c853;">', unsafe_allow_html=True)
        st.markdown("### 🔒 完全版レポート（無料）")
        st.markdown('<div class="blur-container">', unsafe_allow_html=True)
        st.write("#### ④ コミュニケーションの癖 / ⑤ ストレス時の反応 / ⑥ 科学的ソリューション")
        st.write("ここにあなたの人生を変える具体的な行動指針が表示されます...")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.link_button("🔑 LINEで完全版を受け取る", "https://line.me/R/ti/p/dummy_id", type="primary", use_container_width=True)
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
