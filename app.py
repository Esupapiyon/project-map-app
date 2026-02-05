import streamlit as st
import datetime
import plotly.graph_objects as go
import random
import os
import pandas as pd

# ==========================================
# 1. Page Config & CSS (Clean & Impactful)
# ==========================================
st.set_page_config(
    page_title="Project MAP",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 全体設定: 高級感のある白ベース */
    .stApp {
        background-color: #FFFFFF;
        color: #333333;
        font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", "Hiragino Sans", Meiryo, sans-serif;
        line-height: 1.8; /* 長文を読みやすく */
    }
    
    /* カードデザイン */
    .result-card {
        background-color: #FAFAFA;
        padding: 32px 24px;
        border-radius: 16px;
        border: 1px solid #EEEEEE;
        margin-bottom: 24px;
    }
    
    /* 強調ハイライト（黄色マーカー風） */
    .highlight {
        background: linear-gradient(transparent 60%, #FFF176 60%);
        font-weight: bold;
        padding: 0 4px;
    }

    /* アイデンティティエリア */
    .identity-header {
        text-align: center;
        margin-bottom: 20px;
    }
    .type-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #BDBDBD;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .type-name {
        font-size: 2.0rem;
        font-weight: 900;
        color: #212121;
        margin: 10px 0;
        line-height: 1.3;
    }
    .catch-copy {
        font-size: 1.1rem;
        font-weight: 600;
        color: #00C853; /* アクセントカラー */
        margin-bottom: 20px;
    }
    
    /* テキストセクション見出し */
    .text-label {
        font-size: 1.0rem;
        font-weight: 800;
        color: #424242;
        border-left: 4px solid #00C853;
        padding-left: 10px;
        margin-top: 30px;
        margin-bottom: 10px;
    }
    
    /* 引用風ボックス（Golden Rule用） */
    .quote-box {
        background-color: #E8F5E9;
        border-left: 5px solid #00C853;
        padding: 15px;
        border-radius: 4px;
        font-weight: bold;
        color: #2E7D32;
        margin: 20px 0;
    }

    /* CTAエリア */
    .cta-box {
        background-color: #212121;
        color: white;
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        margin-top: 40px;
    }
    
    /* ぼかし */
    .blurred {
        filter: blur(5px);
        opacity: 0.7;
        pointer-events: none;
        user-select: none;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Helper Functions
# ==========================================
def load_image(type_id):
    """画像のパスを柔軟に探す（8と9の入れ替えロジック含む）"""
    target_id = type_id
    if type_id == 8: target_id = 9
    elif type_id == 9: target_id = 8
        
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG']
    base_dir = "images"
    
    if not os.path.exists(base_dir): return None
    
    for ext in extensions:
        filename = f"{target_id}{ext}"
        path = os.path.join(base_dir, filename)
        if os.path.exists(path): return path
    return None

# ==========================================
# 3. Logic Data & Content Expansion
# ==========================================

TIPI_QUESTIONS = {
    "Q1": "活発で、外向的だと思う", "Q2": "他人に不満をもち、もめごとを起こしやすいと思う",
    "Q3": "しっかりしていて、自分に厳しいと思う", "Q4": "心配性で、うろたえやすいと思う",
    "Q5": "新しいことが好きで、変わった考えを持つと思う", "Q6": "控えめで、おとなしいと思う",
    "Q7": "人に気を使う方で、やさしいと思う", "Q8": "だらしなく、うっかりしていると思う",
    "Q9": "冷静で、気分が安定していると思う", "Q10": "発想力に欠けた、平凡な人間だと思う"
}

# 全タイプ共通のCTAテキスト
COMMON_CTA = "ここから先は、膨大な行動データから導き出されたあなたの運命の『裏側』を無料で解析します。"

DIAGNOSIS_CONTENT = {
    0: { # Type 1: 甲
        "name": "頼れる親分肌 (THE LEADER)",
        "catch": "折れない信念を持つ、孤高の統率者",
        "desc": "あなたは、漫画の主人公のような真っ直ぐな正義感を持つリーダーです。混乱した状況でも「私がやる」と声を上げる強さがありますが、**実は一人になると急に冷めて孤独を感じていませんか？**（アンビバレンス）。最近、何もないところで躓いたり、ちょっとしたルール違反に過剰にイライラしたはずです（ショットガン）。あなたは理解されにくい「ガラスの巨塔」ですが、その脆さこそが、誰も到達できない高みを目指す**王の証**なのです（レアリティ）。",
        "flaw": "【融通ゼロの繊細ゴリラ】\n一度折れると再起不能になるほど落ち込みます。しかしそれは、「妥協」という言葉が辞書にないほど、理想が高潔であることの裏返しです。",
        "desire": "尊敬・成長",
        "habit": "結論ファースト。既読無視は「了解」の合図。議論になると正論というナイフで相手をタコ殴りにしてしまう。",
        "shadow": "【過剰な批判者化】\nストレスが限界を超えると、周囲を攻撃し始めます。でもそれは、あなたが誰よりも責任を感じ、一人で背負い込んでいる証拠なのです（バリデーション）。",
        "golden_rule": "『負けるが勝ち』を覚えよ",
        "cta_text": COMMON_CTA
    },
    1: { # Type 2: 乙
        "name": "愛され調整役 (THE CONNECTOR)",
        "catch": "したたかに生き残る、柔軟な戦略家",
        "desc": "あなたはどんな過酷な環境でも、笑顔で生き残る雑草魂を持っています。ニコニコしていますが、**頭の中では常に電卓を叩いて損得勘定をしていますよね？**（アンビバレンス）。最近、興味のない話に笑顔で相槌を打ちながら、「今日の晩御飯なにしよう」と考えていましたね？（ショットガン）。あなたは単なる八方美人ではありません。剛腕リーダーをも裏で操る、真の**「影の支配者」**という才能の持ち主です（レアリティ）。",
        "flaw": "【自分を見失うカメレオン】\n人に合わせすぎて「で、本音は？」と聞かれるとフリーズします。しかしそれは、どんな器にも入れる水のような柔軟性を持っている証拠です。",
        "desire": "調和・安全",
        "habit": "傾聴の天才。相手の仕草を真似るミラーリングが得意。LINEでは相手の文量やスタンプに合わせる。",
        "shadow": "【依存と責任転嫁】\n「あの人が言ったから」と逃げたくなる時があります。それは、あなたが常に全体の調和を優先し、板挟みになって戦っているからです（バリデーション）。",
        "golden_rule": "『嫌われる勇気』を持て",
        "cta_text": COMMON_CTA
    },
    2: { # Type 3: 丙
        "name": "天性の主人公 (THE PROTAGONIST)",
        "catch": "世界を照らす、あくなき挑戦者",
        "desc": "あなたは歩く火力発電所です。その場にいるだけで照明が明るくなったと錯覚させるエネルギーがありますが、**家に帰った瞬間、電池が切れたように無表情になりますよね？**（アンビバレンス）。最近、スマホをどこに置いたか忘れたり、買ったばかりの物を失くしたりしませんでしたか？（ショットガン）。あなたは落ち着きのない子供のようですが、その「根拠のない自信」こそが、世界を変える**規格外のエンジン**なのです（レアリティ）。",
        "flaw": "【話を聞かないジャイアン】\n秘密を3秒で拡散してしまいます。しかしそれは、情報を独り占めせず、世界にオープンにするという圧倒的な陽のエネルギーの表れです。",
        "desire": "注目・称賛",
        "habit": "マシンガントーク。LINEは短文連投型。沈黙が怖くて喋り続けてしまう。",
        "shadow": "【極端な無気力】\n急に「もうダメだ」と大騒ぎします。それは、あなたが普段、常人の3倍のエネルギーで周りを照らし続けている反動なのです（バリデーション）。",
        "golden_rule": "『継続』こそが最大のエンタメ",
        "cta_text": COMMON_CTA
    },
    3: { # Type 4: 丁
        "name": "熱き夢想家 (THE MUSE)",
        "catch": "静寂に燃える、知性の灯火",
        "desc": "あなたは一見穏やかで物静かですが、内側にはドロドロとした情熱と、**過去10年分の恨みを記録したデスノート**を持っていますね？（アンビバレンス）。最近、夜中にふと人生について考え込み、ポエムのような長文を下書き保存しませんでしたか？（ショットガン）。あなたは理解されにくいミステリアスな存在ですが、その「狂気」に近い感受性こそが、芸術を生み出す**天才の源泉**です（レアリティ）。",
        "flaw": "【察してちゃん界のラスボス】\n言葉にせず「わかってよ」オーラを出します。しかしそれは、言葉では表現しきれないほど繊細で高解像度な世界を見ているからです。",
        "desire": "理解・美学",
        "habit": "核心を突く一言で場を凍らせる。深夜になるとLINEが長文化し、哲学的な内容を送りがち。",
        "shadow": "【疑心暗鬼と攻撃】\n「あの人は私を馬鹿にしている」と思い込みます。それは、あなたの洞察力が鋭すぎて、他人の微細な悪意まで感知してしまうからです（バリデーション）。",
        "golden_rule": "『言葉にする』手間を惜しむな",
        "cta_text": COMMON_CTA
    },
    4: { # Type 5: 戊
        "name": "不動の守護神 (THE ANCHOR)",
        "catch": "すべてを受け入れる、揺るがぬ巨塔",
        "desc": "あなたは何があっても動じない人間岩盤です。周囲からは「器が大きい」と頼られていますが、**実は単に動くのが面倒くさいだけだったりしますよね？**（アンビバレンス）。最近、お気に入りの店がメニューを変えただけで、一日中不機嫌になりませんでしたか？（ショットガン）。その頑固さは短所ではありません。嵐の中でも一歩も引かない、組織の**「絶対的なアンカー（錨）」**という才能です（レアリティ）。",
        "flaw": "【テコでも動かない頑固オヤジ】\n変化を極端に嫌います。しかしそれは、一度築き上げたものを死守し、永続させるための鉄壁の防御力なのです。",
        "desire": "安定・信頼",
        "habit": "基本は聞き役。LINEの返信は遅く、「了解」の一言などシンプル極まりない。",
        "shadow": "【完全な閉鎖】\n殻に閉じこもり、誰の言葉も届かなくなります。それは、あなたが「最後の砦」として、一人で重圧に耐えようとしているからです（バリデーション）。",
        "golden_rule": "『とりあえずやってみる』精神を持て",
        "cta_text": COMMON_CTA
    },
    5: { # Type 6: 己
        "name": "尽くす世話焼き (THE NURTURER)",
        "catch": "才ある者を育む、慈愛の大地",
        "desc": "あなたは困っている人を放っておけない「みんなのオカン」です。無償の愛を注いでいるつもりですが、**心のどこかで「これだけやったんだから感謝してよ」と見返りを求めていますよね？**（アンビバレンス）。最近、ダメな異性や手のかかる後輩ばかり構ってしまっていませんか？（ショットガン）。あなたはただのお人好しではありません。原石を見抜き、磨き上げる**「最強の育成者」**という特別な才覚を持っています（レアリティ）。",
        "flaw": "【ダメンズ製造機】\n世話を焼きすぎて相手の自立心を奪います。しかしそれは、相手の可能性を信じ抜くことができる、深すぎる愛情の裏返しです。",
        "desire": "貢献・親密",
        "habit": "話し方が教育的。LINEは長文で、日常の写真や「ご飯食べた？」などの確認が多い。",
        "shadow": "【愚痴と干渉】\n「あんなにしてあげたのに」と不満が爆発します。それは、あなたが自分のこと以上に他人のために命を削って尽くしてきた証拠です（バリデーション）。",
        "golden_rule": "『手放す愛』を知れ",
        "cta_text": COMMON_CTA
    },
    6: { # Type 7: 庚
        "name": "正義の切り込み隊長 (THE HERO)",
        "catch": "時代を切り拓く、鋼の革命家",
        "desc": "あなたは「それはおかしい」と声を上げられる特攻隊長です。サッパリしていますが、**デリカシーがなく、悪気なく正論で人を傷つけて、後で「言い過ぎたかな…」と1ミリだけ反省しますよね？**（アンビバレンス）。最近、結論の出ない会議にイライラして、貧乏ゆすりが止まらなくなりませんでしたか？（ショットガン）。その攻撃性は、停滞した世界をぶち壊すための**「聖なる剣」**です（レアリティ）。",
        "flaw": "【デリカシー？何それ美味しいの？】\n空気を読みません。しかしそれは、同調圧力に屈せず、雑音に惑わされずに「真実」だけを見抜く力が強すぎるのです。",
        "desire": "変革・勝利",
        "habit": "単刀直入。前置きなしで本題に入る。LINEは「うん」「わかった」「NG」の即レス。",
        "shadow": "【破壊的衝動】\n全てをリセットしたくなります。それは、あなたが妥協だらけの現実に絶望せず、理想を追い求め続けている戦士だからです（バリデーション）。",
        "golden_rule": "『剣を収める』美学を持て",
        "cta_text": COMMON_CTA
    },
    7: { # Type 8: 辛
        "name": "繊細な宝石 (THE IDOL)",
        "catch": "試練を輝きに変える、美しきカリスマ",
        "desc": "あなたは生まれながらの「選ばれし姫・王子」です。高貴なオーラを放っていますが、**メンタルはスライム級に弱く、特別扱いされないとすぐに拗ねますよね？**（アンビバレンス）。最近、LINEの既読スルーに傷つき、「もうブロックしてやる！」と一人で悲劇のヒロインになりませんでしたか？（ショットガン）。その面倒くささは、細部まで妥協できない**「美の求道者」**であることの証明です（レアリティ）。",
        "flaw": "【超・ワガママちゃん】\nプライドが高く謝れません。しかしそれは、自分自身をブランドとして確立し、安売りしないというプロ意識の高さゆえです。",
        "desire": "特別感・洗練",
        "habit": "美意識が高い言葉選び。汚い言葉を嫌う。既読スルーされるとこの世の終わりのように激怒する。",
        "shadow": "【自虐と他責】\n「どうせ私なんて」と卑下します。それは、あなたが誰よりも高い理想を自分に課し、必死にもがいている証拠なのです（バリデーション）。",
        "golden_rule": "『傷』を『勲章』に変えよ",
        "cta_text": COMMON_CTA
    },
    8: { # Type 9: 壬
        "name": "自由な冒険家 (THE NOMAD)",
        "catch": "境界を超えて流れる、自由の象徴",
        "desc": "あなたはスケールの大きい永遠の旅人です。夢を語らせたら右に出る者はいませんが、**飽きっぽすぎて、昨日言ったことと今日言ったことが全然違いますよね？**（アンビバレンス）。最近、面倒くさい約束を「体調不良」ということにしてドタキャンしたことがありますよね？（ショットガン）。その無責任さは、一つの場所に留まらず、世界に新しい風を吹き込む**「流動する知性」**だからこそ許される特権です（レアリティ）。",
        "flaw": "【音信不通の常習犯】\n責任から逃げ出します。しかしそれは、直感が「今は動くべき時ではない」と告げている、野生の勘が鋭すぎる結果なのです。",
        "desire": "自由・流動",
        "habit": "誰とでもタメ口で仲良くなれる。LINEは超・気分屋で、返信速度にムラがありすぎる。",
        "shadow": "【逃避と氾濫】\n全てを放り出して蒸発します。それは、あなたの器が大きすぎて、小さな枠組みに押し込められると氾濫してしまう大河だからです（バリデーション）。",
        "golden_rule": "『帰る場所』を作れ",
        "cta_text": COMMON_CTA
    },
    9: { # Type 10: 癸
        "name": "癒やしの共感者 (THE COUNSELOR)",
        "catch": "静かに浸透する、慈愛の賢者",
        "desc": "あなたは雨のように静かに人に寄り添う癒やし系です。ニコニコと人の話を聞いていますが、**心の中では「こいつ、バカだな」と冷静に見下している瞬間がありますよね？**（アンビバレンス）。最近、嫌なことがあって、何も言わずに連絡先をブロック・削除してスッキリしませんでしたか？（ショットガン）。あなたはただの大人しい人ではありません。世の中の裏側まで見通す**「静かなる賢者」**なのです（レアリティ）。",
        "flaw": "【自分がないスライム】\n影響を受けすぎて形が変わります。しかしそれは、相手の色に染まることで、相手の痛みを我が事のように理解できる究極の共感力です。",
        "desire": "共感・貢献",
        "habit": "受動的。自分からは発信しない。争いを避けるためなら、自分の意見を飲み込んでニコニコする。",
        "shadow": "【自己卑下と遮断】\n突然人間関係をリセット（サイレント絶交）します。それは、あなたが他人の負の感情を吸い取りすぎて、心がパンクしそうになっているSOSサインです（バリデーション）。",
        "golden_rule": "『自分』という器を持て",
        "cta_text": COMMON_CTA
    }
}

# --- 占術パラメータ（変更なし） ---
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
    is_gap = False
    # 簡易ギャップロジック
    if fate_type_id in [0, 2, 6] and scores_norm["Extraversion"] < 2.5: is_gap = True
    elif fate_type_id in [1, 9] and scores_norm["Agreeableness"] < 2.5: is_gap = True
    elif fate_type_id in [4, 7] and scores_norm["Conscientiousness"] < 2.5: is_gap = True
    
    if is_gap: return "WARNING", "⚠️ 注意：あなたの本来の強みが、現在60%死んでいます。"
    else: return "SUCCESS", "✨ 素晴らしい：宿命通りに才能が発揮されています。ただし…"

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
# 5. Main UI Application
# ==========================================

st.title("Project MAP")

main_tab, catalog_tab = st.tabs(["DIAGNOSIS (診断)", "ALL TYPES (図鑑)"])

# --- Tab 1: Diagnosis ---
with main_tab:
    # A. Form
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
            st.markdown(f"<div style='font-weight:bold;'>{q_text}</div>", unsafe_allow_html=True)
            tipi_answers[q_id] = st.slider(f"", 1, 7, 4, key=f"form_{q_id}")
            st.markdown("<br>", unsafe_allow_html=True)
            
        submitted = st.form_submit_button("運命を診断する", type="primary", use_container_width=True)
    
    # B. Result
    if submitted:
        try:
            date_obj = datetime.date(year, month, day)
            date_str = date_obj.strftime("%Y/%m/%d")
            
            engine = FortuneEngineIntegrated()
            result = engine.analyze_basic(date_str)
            gan_id = result['gan']
            content = DIAGNOSIS_CONTENT[gan_id]
            fate_code = result['fate_code']
            
            _, big5_norm = calculate_big5(tipi_answers)
            status, hook_text = get_gap_hook(gan_id, big5_norm)

            # === IDENTITY AREA ===
            st.markdown('<div class="result-card identity-header">', unsafe_allow_html=True)
            st.markdown(f"<div class='type-label'>FATE CODE: {fate_code}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='type-name'>{content['name']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='catch-copy'>{content['catch']}</div>", unsafe_allow_html=True)
            
            img_path = load_image(gan_id + 1)
            if img_path: st.image(img_path, use_container_width=True)
            else: st.image("https://placehold.co/400x400/F0F0F0/333?text=No+Image", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # === DEEP DIVE (Psychology) ===
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("<div class='text-label'>👤 あなたの本質と裏側</div>", unsafe_allow_html=True)
            st.write(content['desc'])
            
            st.markdown("<div class='text-label'>⚠️ 愛すべき欠点 (才能の裏返し)</div>", unsafe_allow_html=True)
            st.write(content['flaw'])
            
            st.markdown("<div class='text-label'>🔥 基本的欲求</div>", unsafe_allow_html=True)
            st.write(content['desire'])
            
            st.markdown("<div class='text-label'>🗣️ コミュニケーションの癖</div>", unsafe_allow_html=True)
            st.write(content['habit'])
            
            st.markdown("<div class='text-label'>🌑 ストレス時の反応 (Shadow)</div>", unsafe_allow_html=True)
            st.write(content['shadow'])
            
            st.markdown(f"<div class='quote-box'>💡 処方箋: {content['golden_rule']}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # === ANALYSIS (寸止め) ===
            st.markdown('<div class="section-title">📊 科学的分析 (現在)</div>', unsafe_allow_html=True)
            if status == "WARNING":
                st.error(hook_text)
            else:
                st.success(hook_text)
            
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown('<div class="blurred">', unsafe_allow_html=True)
            
            # Dummy Chart for Blur
            categories = ['外向', '開放', '協調', '勤勉', '安定']
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=[3,4,3,4,3], theta=categories, fill='toself'))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.write("ここに詳細な分析結果が表示されます..." * 5)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # CTA Overlay
            st.markdown(f"""
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 90%; text-align: center;">
                <div style="background:rgba(255,255,255,0.9); padding:20px; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.1);">
                    <p style="font-weight:bold; margin-bottom:15px; color:#333;">{content['cta_text']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Button outside the overlay div to ensure clickability
            st.link_button("LINEで『裏』解析レポートを見る (無料)", "https://line.me/R/ti/p/dummy_id", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        except ValueError:
            st.error("正しい日付を選択してください。")

# --- Tab 2: Catalog ---
with catalog_tab:
    st.markdown("### 全10タイプ図鑑")
    cols = st.columns(2)
    for i in range(10):
        c = DIAGNOSIS_CONTENT[i]
        with cols[i % 2]:
            st.markdown('<div class="result-card" style="padding:15px; text-align:center;">', unsafe_allow_html=True)
            img_path = load_image(i + 1)
            if img_path: st.image(img_path, use_container_width=True)
            st.caption(c['name'])
            st.markdown(f"**{c['catch']}**")
            st.markdown('</div>', unsafe_allow_html=True)
