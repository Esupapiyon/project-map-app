import streamlit as st
import datetime
import plotly.graph_objects as go
import random
import os
import pandas as pd

# ==========================================
# 1. Page Config & CSS (Ver Final_CTA_Fixed)
# ==========================================
st.set_page_config(
    page_title="Project MAP",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS定義
st.markdown("""
<style>
    /* 全体設定 */
    .stApp {
        background-color: #FFFFFF;
        color: #333333;
        font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", "Hiragino Sans", Meiryo, sans-serif;
        line-height: 1.8;
        letter-spacing: 0.03em;
    }
    
    /* タブ文字の視認性向上 */
    .stTabs [data-baseweb="tab"] {
        color: #666666;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #00C853;
        border-bottom-color: #00C853;
    }
    
    /* カードデザイン */
    .read-card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #F0F0F0;
        margin-bottom: 30px;
    }
    
    /* タイトル周り */
    .type-name-huge {
        font-size: 2.4rem;
        font-weight: 900;
        color: #222;
        line-height: 1.2;
        margin-bottom: 5px;
        text-align: center;
    }
    .catch-subtitle {
        font-size: 1.1rem;
        font-weight: 700;
        color: #D32F2F;
        margin-bottom: 20px;
        text-align: center;
        display: block;
    }
    
    /* 口癖（吹き出し風） */
    .phrase-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        margin-bottom: 25px;
    }
    .phrase-bubble {
        background-color: #F5F5F5;
        color: #333;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        border: 2px solid #E0E0E0;
    }

    /* 見出しスタイル */
    h3 {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #111 !important;
        margin-top: 40px !important;
        margin-bottom: 15px !important;
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
    }
    
    /* 評判リスト */
    .impression-box {
        padding: 15px;
        border-radius: 8px;
        font-size: 0.95rem;
        height: 100%;
    }
    .impression-good {
        background-color: #E8F5E9;
        color: #1B5E20;
    }
    .impression-bad {
        background-color: #FFEBEE;
        color: #B71C1C;
    }

    /* FATE Code解説エリア */
    .fate-meaning-box {
        background-color: #FAFAFA;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #EEE;
        font-size: 0.95rem;
    }
    .fate-char {
        font-weight: 900;
        color: #00C853;
        margin-right: 8px;
        font-family: monospace;
        font-size: 1.2rem;
    }

    /* 処方箋 */
    .golden-rule {
        background: linear-gradient(135deg, #212121 0%, #424242 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin-top: 30px;
    }
    
    /* チャート説明文 */
    .chart-desc {
        font-size: 0.9rem;
        background-color: #E3F2FD;
        color: #0D47A1;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        line-height: 1.6;
    }
    
    /* ロックオーバーレイ（CSSバックアップ） */
    .lock-overlay {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 90%;
        text-align: center;
        z-index: 10;
    }
    .lock-card {
        background: rgba(255,255,255,0.95);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Helper Functions
# ==========================================
def load_image(type_id):
    """画像パス探索"""
    target_id = type_id
    if type_id == 8: target_id = 9
    elif type_id == 9: target_id = 8
        
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG']
    base_dir = "images"
    
    if not os.path.exists(base_dir): return None
    for ext in extensions:
        path = os.path.join(base_dir, f"{target_id}{ext}")
        if os.path.exists(path): return path
    return None

# ==========================================
# 3. Logic Data (Part A: Content & Constants)
# ==========================================

# TIPI-J 質問項目
TIPI_QUESTIONS = {
    "Q1": "活発で、外向的だと思う", "Q2": "他人に不満をもち、もめごとを起こしやすいと思う",
    "Q3": "しっかりしていて、自分に厳しいと思う", "Q4": "心配性で、うろたえやすいと思う",
    "Q5": "新しいことが好きで、変わった考えを持つと思う", "Q6": "控えめで、おとなしいと思う",
    "Q7": "人に気を使う方で、やさしいと思う", "Q8": "だらしなく、うっかりしていると思う",
    "Q9": "冷静で、気分が安定していると思う", "Q10": "発想力に欠けた、平凡な人間だと思う"
}

# FATE Code マスター辞書
FATE_MEANINGS = {
    "L": "Logic (論理): 物事を事実とデータで客観的に捉える。",
    "S": "Sense (感覚): 直感やその場の空気感で本質を掴む。",
    "R": "Risk (堅実): リスクを回避し、確実な道を選ぶ。",
    "G": "Growth (成長): 変化を恐れず、拡大と挑戦を選ぶ。",
    "I": "Impulse (衝動): 瞬発力があり、走りながら考える。",
    "D": "Deliberate (熟考): 計画を練り、慎重に行動に移す。",
    "M": "Me (自我): 自分の価値観や願望を最優先する。",
    "Y": "You (協調): 他者との調和や貢献を原動力にする。"
}

# 全タイプ共通CTAテキスト
COMMON_CTA = "ここから先は、膨大な行動データから導き出されたあなたの運命の『裏側』を無料で解析します。"

# 診断コンテンツ (Ver Final_CTA_Fixed)
DIAGNOSIS_CONTENT = {
    0: { # Type 1: 甲 (Wood+)
        "name": "鬼軍曹 (THE DRILL SERGEANT)",
        "color": "#2E7D32", 
        "catch": "1ミリのズレで発狂する整理整頓の鬼",
        "phrases": ["結論から言って", "ルールなんで", "はぁ…（深いため息）"],
        "fate_code_type": "LRDM",
        "default_scores": {'Identity':5, 'Create':3, 'Economy':2, 'Status':2, 'Vitality':4},
        "intro": "あなたには、生まれながらにして人々を惹きつけ、自然と集団の中心に立ってしまう引力があります。それは単なる明るさではなく、「この人は何かを変えてくれるかもしれない」と他人に予感させる、圧倒的な頼もしさと威厳です。大樹が大地に根を張るように、あなたは揺るぎない「自分軸」を持っており、混沌とした状況においてこそ、その存在感は際立ちます。しかし、その真っ直ぐすぎる姿勢は、時に周囲に「近寄りがたい」「完璧すぎて息が詰まる」という緊張感を与えているかもしれません。あなたは自身の弱さを隠すのが上手ですが、実は誰よりも「正しくあろう」と必死にもがいている孤独な努力家でもあります。",
        "social_style": "【対人スタイル：守護と支配のパラドックス】\nあなたは「身内」と認定した人間に対しては、海よりも深い愛情と責任感で守り抜きます。部下のミスを被ったり、友人の窮地には損得抜きで駆けつける親分肌です。その愛は深く、一度懐に入れた人間は一生面倒を見る覚悟を持っています。\nしかし、その反面、自分の価値観やルールに反する人間に対しては容赦がありません。「無能」「不誠実」と判断した相手には、氷のように冷徹な態度を取り、心のシャッターを完全に下ろします。議論においては、感情論を嫌い、正論という名の凶器で相手を黙らせてしまう傾向があります。論破した後に感じるのは、勝利の快感ではなく、「なぜわかってくれないのか」という深い孤独感ではないでしょうか。",
        "inner_drive": "【本音と欠点：完全への渇望と恐怖】\nあなたがこれほどまでに強く振る舞うのは、実は心の奥底に「混沌」や「無秩序」に対する根源的な恐怖があるからです。「自分がしっかりしなければ組織が崩壊する」「自分が折れたら終わりだ」という強迫観念にも似た責任感が、あなたを突き動かしています。\n愛すべき欠点は、その「不器用なほどの融通の利かなさ」です。誰もが適当に流すような小さな不正義も許せず、一人でカリカリしてしまう姿。それは周囲から見れば「面倒くさい人」ですが、同時に「絶対に裏切らない信頼できる人」という評価にも繋がっています。",
        "shadow_phase": "【ストレス反応：孤立する暴君】\n精神的な余裕を失うと、あなたは「どうして誰も私のレベルで動けないんだ」と周囲を断罪し始めます。完璧主義が暴走し、他人の些細な欠点をあげつらったり、独善的な命令を下したりして、自ら孤立を深めていきます。最終的には「もう全部一人でやる」と殻に閉じこもり、心身ともに燃え尽きるまで走り続けてしまう危険性があります。",
        "trivia": [
            "歩くのが遅い人の後ろにいると、露骨にイライラしてしまう",
            "「とりあえず」という言葉が大嫌い",
            "曲がったネクタイや、整っていない資料を見ると直したくて手が震える",
            "実は涙もろいが、人前では絶対に泣かないと決めている",
            "誰も見ていないところでも、赤信号は絶対に渡らない"
        ],
        "impression_good": ["圧倒的な安心感と統率力", "嘘をつかない誠実さ", "どんな混乱も鎮める解決力"],
        "impression_bad": ["息が詰まるほどの威圧感", "正論すぎて逃げ場がない", "デリカシーが行方不明"],
        "golden_rule_long": "『負けるが勝ち』を、戦略としてインストールせよ。\nあなたの正しさは誰もが認めています。だからこそ、あえて相手に花を持たせ、頭を下げる「演技」を覚えたとき、あなたは単なる実力者から、誰もが心服する真の王になります。",
        "cta_text": COMMON_CTA
    },
    1: { # Type 2: 乙 (Wood-)
        "name": "裏回し (THE COORDINATOR)",
        "color": "#2E7D32",
        "catch": "息をするように話を盛って場を繋ぐ",
        "phrases": ["わかる〜！", "なんでもいいよー", "怒ってない？"],
        "fate_code_type": "SGIY",
        "default_scores": {'Identity':4, 'Create':4, 'Economy':3, 'Status':2, 'Vitality':3},
        "intro": "あなたは、コンクリートの隙間からでも花を咲かせる草花のように、どんな過酷な環境でも生き残る「生存戦略の天才」です。決して声高に自己主張するわけではありませんが、気づけばキーマンの隣に座り、最も居心地の良いポジションを確保している。そんな「柔よく剛を制す」しなやかさがあなたの武器です。一見、無害で人当たりの良い人物に見えますが、その笑顔の裏には、周囲のパワーバランスを冷静に見極める計算高い瞳が隠されています。あなたは誰よりも早く「空気」を読み、その場の最適解を演じることができます。",
        "social_style": "【対人スタイル：全方位外交と依存】\nあなたは「敵を作らない」ことにかけては世界一の才能を持っています。相手によって声のトーンや話題を瞬時に変え、誰とでも心地よい関係を築くカメレオンのような社交術を持っています。剛腕なリーダータイプとも、気難しい職人タイプとも上手くやれるのはあなただけです。\nしかし、それは「嫌われたくない」という防衛本能の裏返しでもあります。決断を迫られると「私はどっちでもいいよ」と判断を相手に委ね、責任を回避する傾向があります。集団の調和を乱すまいとするあまり、八方美人になりすぎて、信用を失うリスクを常に抱えています。",
        "inner_drive": "【本音と欠点：孤独への恐怖】\nあなたがこれほどまでに空気を読むのは、集団から弾き出されることへの強烈な恐怖があるからです。「一人では生きていけない」と本能的に悟っており、常に誰かと繋がっていることで安心感を得ようとします。自立することよりも、強い何かに巻きつかれる（所属する）ことを選びます。\n愛すべき欠点は、その「わかりやすすぎる計算高さ」です。メリットのある人には尻尾を振るのに、どうでもいい人には少し雑になる。その人間臭い現金さが、逆に「憎めないキャラ」として定着しています。",
        "shadow_phase": "【ストレス反応：悲劇のヒロイン】\n追い詰められると、急に被害者面をして責任転嫁を始めます。「あの人が言ったから」「私は悪くないのに」と周囲に吹聴し、同情を買うことで自分を守ろうとします。また、強いものに巻かれる傾向が強まり、自分の意思を完全に放棄して、操り人形のように振る舞うことで思考停止しようとします。",
        "trivia": [
            "興味のない話でも、笑顔で「すごーい！」と言える",
            "LINEの返信スタンプを選ぶのに3分悩むことがある",
            "「何食べたい？」と聞かれるのが死ぬほど苦手",
            "強い人の意見には、とりあえず0.5秒で同意する",
            "一人焼肉や一人映画には、実は行けない（寂しいから）"
        ],
        "impression_good": ["物腰が柔らかく話しやすい", "空気が読める調整役", "敵を作らない世渡り上手"],
        "impression_bad": ["本心がどこにあるか不明", "八方美人で信用できない", "決断を人任せにする"],
        "golden_rule_long": "『嫌われる勇気』が、最強の鎧になる。\n全員に好かれようとすることは、誰からも信頼されないことと同義です。10人のうち2人に嫌われても、自分の意志をはっきり示すことで、残りの8人との絆は、単なる「馴れ合い」を超えた本物の信頼へと変わります。",
        "cta_text": COMMON_CTA
    },
    2: { # Type 3: 丙 (Fire+)
        "name": "センター (THE STAR)",
        "color": "#C62828",
        "catch": "他人の話を聞く機能が「未実装」",
        "phrases": ["ねえ見て見て！", "すごくない！？（私が）", "飽きた"],
        "fate_code_type": "SGIM",
        "default_scores": {'Identity':5, 'Create':5, 'Economy':3, 'Status':2, 'Vitality':2},
        "intro": "あなたは、真夏の太陽のように強烈な光と熱を放つ、天性のエンターテイナーです。あなたが部屋に入ってきた瞬間、場の空気がパッと明るくなるような、不思議なオーラを纏っています。論理よりも感情、計画よりも情熱。「なんとかなるさ！」という根拠のない自信で突き進み、いつの間にか皆をあなたのペースに乗せてしまう。良くも悪くも、世界はあなた中心に回っていると言っても過言ではありません。隠し事ができず、感情がすべて顔に出るため、周囲からは「わかりやすい人」として愛されています。",
        "social_style": "【対人スタイル：巻き込み型カリスマ】\n誰に対してもオープンマインドで、裏表のない性格は多くの人を惹きつけます。沈んでいる人を強引に外へ連れ出し、豪快に笑い飛ばして元気づけるような、圧倒的な陽のエネルギーを持っています。\n一方で、自分の話をするのが大好きで、相手の話を聞いているようで聞いていない「ジャイアン」的な側面も。自分の興味がある話題には食いつきますが、そうでないと露骨に退屈そうな顔をします。しかし、その自己中心性すらも「まあ、あの人だから仕方ないか」と許させてしまう愛嬌こそが、あなたの最大の武器です。",
        "inner_drive": "【本音と欠点：承認への渇望】\nあなたの行動の原動力は、シンプルに「見てほしい」「褒めてほしい」という承認欲求です。注目されないことは、あなたにとって存在していないも同然です。\n愛すべき欠点は、その「驚くべき飽きっぽさ」です。昨日まで「一生の趣味にする！」と熱中していた道具が、今日はもう部屋の隅で埃を被っている。その子供のような移り気さは、周囲を呆れさせつつも、常に新しい風を運んできます。",
        "shadow_phase": "【ストレス反応：極端な無気力】\n普段の明るさが嘘のように、電池が切れたように落ち込みます。「もうダメだ、終わった」と大げさに騒ぎ立てますが、それは「そんなことないよ」と慰めてほしいサインでもあります。批判されると過剰に反応し、一時的に攻撃的になりますが、一晩寝ると忘れていることが多いのも特徴です。",
        "trivia": [
            "スマホの充電が20%を切ると、パニックになる",
            "秘密の話を「ここだけの話」として3人に喋ったことがある",
            "褒められると、顔に出るのを隠しきれない",
            "長文の説明書は、最初の3行しか読まない",
            "買ったばかりの服を、その日に着て帰る"
        ],
        "impression_good": ["裏表がなく付き合いやすい", "行動力と決断力がある", "場を明るくするムードメーカー"],
        "impression_bad": ["自己中心的で話を聞かない", "熱しやすく冷めやすい", "デリカシーがない"],
        "golden_rule_long": "『継続』こそが、最大のエンターテインメント。\nあなたの爆発力は最強ですが、持続力がありません。飽きてからが本当の勝負。「あと一歩」踏ん張るだけで、あなたは単なる「一発屋」ではなく、時代を作る「レジェンド」になれます。",
        "cta_text": COMMON_CTA
    },
    3: { # Type 4: 丁 (Fire-)
        "name": "教祖 (THE GURU)",
        "color": "#C62828",
        "catch": "勝手に期待して勝手に裏切られた気になる",
        "phrases": ["別に…", "全部わかってる", "……（既読スルー）"],
        "fate_code_type": "LRDM",
        "default_scores": {'Identity':4, 'Create':5, 'Economy':2, 'Status':2, 'Vitality':3},
        "intro": "あなたは、夜空に浮かぶ月や、暗闇で揺れる蝋燭の炎のように、静かでミステリアスな引力を持つ人です。大声で自己主張することはありませんが、その内側には、誰よりも激しい情熱と、鋭い反骨精神、そして独自の美学が渦巻いています。多くの人が見過ごすような些細な変化や、言葉の裏にある感情を読み取る洞察力を持ち、組織においては「静かなる参謀」や「孤高のクリエイター」として一目置かれる存在です。あなたの放つ言葉には、人をハッとさせる魔力があります。",
        "social_style": "【対人スタイル：狭く深く、濃密に】\nあなたは「量」より「質」の人間関係を求めます。表面的な付き合いや、中身のない世間話は時間の無駄だと感じています。心を許した少数の相手とは、夜通し人生や哲学について語り合うような濃密な関係を築きます。\n一方で、一度「敵」とみなした相手には、表向きは穏やかに接しながらも、心の中で静かにシャッターを下ろし、永久にアクセス禁止にする冷徹さを持っています。その境界線は非常にシビアで、一度外された人が戻れることは稀です。",
        "inner_drive": "【本音と欠点：理解への渇望と選民意識】\nあなたが最も恐れているのは「ありきたりな人間だと思われること」です。「変わってるね」はあなたにとって最高の褒め言葉であり、凡人扱いされることを嫌います。\n愛すべき欠点は、めんどくさいほどの「察してちゃん」気質。「言わなくてもわかってよ」というオーラを出し、相手が気づかないと勝手に傷ついて殻に閉じこもる。その繊細で手のかかる部分は、理解者にとってはたまらない魅力となります。",
        "shadow_phase": "【ストレス反応：疑心暗鬼と攻撃】\nストレスが極限に達すると、被害妄想が膨らみます。「あの人のあの一言は、私への当てつけに違いない」とネガティブな深読みをし、周囲を敵視します。また、溜め込んだ感情が爆発すると、過去の恨みつらみを理路整然と並べ立て、相手を精神的に追い詰める怖さがあります。",
        "trivia": [
            "深夜に書いたポエムのようなLINEを、翌朝消したくなる",
            "「普通」と言われると、密かに傷つく",
            "人の好き嫌いは激しいが、顔には出さない",
            "10年前に言われた嫌な一言を、一字一句覚えている",
            "占いや心理テストの結果を、こっそり信じている"
        ],
        "impression_good": ["思慮深く知的な雰囲気", "独特の世界観とセンス", "本質を突く鋭さがある"],
        "impression_bad": ["何を考えているか不明", "気難しく近寄りがたい", "急に不機嫌になる"],
        "golden_rule_long": "『言葉にする』手間を、惜しんではならない。\nあなたの繊細な感性は素晴らしいですが、テレパシーは使えません。察してほしいと願う前に、泥臭く言葉で伝える努力をすることで、あなたの孤独な世界は、多くの人に愛される共感の庭になります。",
        "cta_text": COMMON_CTA
    },
    4: { # Type 5: 戊 (Earth+)
        "name": "長老 (THE ELDER)",
        "color": "#F9A825",
        "catch": "新しいやり方をとりあえず一度否定する",
        "phrases": ["一旦様子見で", "それ、今やる必要ある？", "めんどくさい"],
        "fate_code_type": "LRDY",
        "default_scores": {'Identity':4, 'Create':2, 'Economy':5, 'Status':3, 'Vitality':3},
        "intro": "あなたは、雄大な山のように、そこに存在するだけで周囲に安心感を与える「器の大きい」人物です。細かいことには動じず、来るもの拒まずの姿勢で、清濁併せ呑む包容力を持っています。自分からガツガツ動くことは少ないですが、どっしりと構えているだけで自然と人やお金が集まってくる、生まれながらの「社長・オーナー」のような風格を漂わせています。変化の激しい現代において、あなたの変わらぬ安定感は、迷える人々の道しるべとなります。",
        "social_style": "【対人スタイル：受け身の信頼】\nあなたは基本的に「聞き役」です。相談事をされると、ただ「うんうん」と頷いているだけで、相手が勝手に癒やされ、解決した気になって帰っていくような不思議な力があります。\nしかし、自分のテリトリーやペースを乱されることを極端に嫌います。普段は温厚ですが、自分の流儀を強引に変えようとする相手には、テコでも動かない頑固さで対抗し、無言の圧力で撃退します。一度「No」と言ったら、二度と意見を覆さない頑なさがあります。",
        "inner_drive": "【本音と欠点：変化への恐怖】\nあなたの安定感の裏には、「変わることへの面倒くささ」や「現状維持への執着」があります。リスクを冒して新しいことに挑戦するよりは、今の確実な利益を守りたいというのが本音です。\n愛すべき欠点は、その「腰の重さ」です。周りが「早くして！」と焦っていても、あなただけワンテンポ遅れて動いている。そのマイペースさは、時として周囲をイライラさせますが、パニック時には最強の安定剤となります。",
        "shadow_phase": "【ストレス反応：完全な閉鎖】\n許容量を超えると、あなたは外界との接触を完全に遮断します。殻に閉じこもり、電話にも出ず、誰の言葉も耳に入らなくなります。それは、あなたが「最後の砦」として一人ですべてを抱え込みすぎた反動であり、動かざる山が噴火する前兆でもあります。",
        "trivia": [
            "お気に入りの店がメニューを変えると、一日中不機嫌になる",
            "LINEの返信は「了解」の一言か、スタンプのみ",
            "貯金通帳の数字が増えるのを見るのが、密かな楽しみ",
            "動き出すまでに時間がかかるが、一度動くと止まらない",
            "「昔は良かった」と、つい口にしてしまう"
        ],
        "impression_good": ["一緒にいると安心する", "頼りがいと包容力がある", "感情的にならず冷静"],
        "impression_bad": ["頑固で融通が利かない", "腰が重く行動が遅い", "何を考えているかわからない"],
        "golden_rule_long": "『とりあえずやってみる』精神を、意図的に持て。\nあなたの慎重さは武器ですが、時には足枷になります。考えすぎる前に、まず靴を履いて外に出る。その一歩の軽やかさを身につければ、あなたの圧倒的な実力は、さらに広い世界で輝きます。",
        "cta_text": COMMON_CTA
    },
    5: { # Type 6: 己 (Earth-)
        "name": "オカン (THE MOM)",
        "color": "#F9A825",
        "catch": "良かれと思ってダメ人間を製造してしまう",
        "phrases": ["あんたのためを思って！", "大丈夫、あんたならできる！", "ほら言ったでしょ"],
        "fate_code_type": "SGDY",
        "default_scores": {'Identity':3, 'Create':3, 'Economy':5, 'Status':2, 'Vitality':4},
        "intro": "あなたは、豊かな土壌が作物を育てるように、他人の才能を見抜き、慈しみ、開花させる天性の「育成者」です。困っている人を見ると放っておけず、つい手を差し伸べてしまう母性的な優しさを持っています。自分自身が脚光を浴びることよりも、あなたが育てた誰かが成功し、輝く姿を見ることに無上の喜びを感じる、究極のサポーター気質と言えるでしょう。その献身的な姿勢は、組織において「なくてはならない空気」のような存在感を放っています。",
        "social_style": "【対人スタイル：過干渉な愛】\n「大丈夫？」「ご飯食べた？」と、常に周囲を気にかけるあなたの周りには、自然と人が集まります。複雑なことを噛み砕いて教えるのが天才的に上手く、チームの教育係やメンターとして絶大な信頼を得ます。\nしかし、その愛は時として「重たい」ものになりがちです。良かれと思って先回りしすぎたり、相手の課題まで肩代わりしてしまったりすることで、無意識のうちに相手の自立心を奪い、「あなたなしでは生きられない人（ダメンズ）」を量産してしまう傾向があります。",
        "inner_drive": "【本音と欠点：感謝への渇望】\nあなたの献身の裏には、「必要とされたい」という強い承認欲求があります。「誰かの役に立っている」という実感が、あなたのアイデンティティそのものなのです。\n愛すべき欠点は、見返りがないと途端に不機嫌になる「恩着せがましさ」です。「あんなにしてあげたのに」と過去の献身を持ち出して愚痴をこぼす姿は、人間臭くもあり、あなたの愛がいかに情熱的であったかの証明でもあります。",
        "shadow_phase": "【ストレス反応：愚痴と干渉】\n精神的に追い詰められると、視野が狭くなり、細かいことへの干渉が激しくなります。「私の言う通りにすればいいのよ」と相手をコントロールしようとしたり、周囲への不満や愚痴が止まらなくなったりします。愛が執着へと変わり、泥沼化する前に距離を置く必要があります。",
        "trivia": [
            "バッグの中に、絆創膏や常備薬が必ず入っている",
            "ダメな異性ほど、可愛く見えて放っておけない",
            "教え方が上手いと言われると、最高に嬉しい",
            "サプライズをするのは好きだが、されるとリアクションに困る",
            "「私がいないとダメね」と言いながら、実は嬉しそう"
        ],
        "impression_good": ["面倒見が良く優しい", "教え方がわかりやすい", "細やかな気配りができる"],
        "impression_bad": ["お節介で過干渉", "恩着せがましい", "愚痴っぽい"],
        "golden_rule_long": "『手放す愛』を、勇気を持って知れ。\n手を貸すことだけが愛ではありません。時には突き放し、転ぶのを見守る勇気を持つこと。相手の力を信じて「何もしない」という選択ができた時、あなたは依存関係を超えた、真の教育者へと進化します。",
        "cta_text": COMMON_CTA
    },
    6: { # Type 7: 庚 (Metal+)
        "name": "特攻隊長 (THE CAPTAIN)",
        "color": "#546E7A",
        "catch": "「悪気はない」と言えば刺してもいいと思っている",
        "phrases": ["それって意味ある？", "効率悪いね", "要するにさ"],
        "fate_code_type": "LGIM",
        "default_scores": {'Identity':4, 'Create':2, 'Economy':3, 'Status':5, 'Vitality':3},
        "intro": "あなたは、切れ味鋭い日本刀のように、停滞した空気を一撃で切り裂く「変革者」です。「長いものに巻かれる」という発想が皆無で、誰もが言いにくいことでも「それはおかしい」と堂々と声を上げる強さを持っています。そのスピード感と決断力は、硬直した組織や古い慣習を打ち破るための、最強の武器となります。敵も作りますが、それ以上に熱狂的な信者を生むカリスマです。",
        "social_style": "【対人スタイル：直球勝負】\n嘘や駆け引きが大嫌いで、常に本音でぶつかります。結論のないダラダラした会話には露骨に退屈な顔をし、「で、結論は？」と急かしてしまうことも。\nあなたの言葉には裏表がないため、サッパリとした気持ちの良い付き合いができますが、デリカシーのなさも天下一品です。悪気なく相手の痛いところを突き、場を凍らせてから「あれ、言い過ぎた？」と気づく、不器用な愛嬌があります。",
        "inner_drive": "【本音と欠点：闘争本能】\nあなたが戦うのは、単に攻撃的だからではなく、「より良い世界（正解）」への純粋な希求があるからです。現状維持は後退と同じだと考えており、常に前進し、勝利することを求めています。\n愛すべき欠点は、その「子供のような短気さ」です。信号待ちやレジの行列でイライラして貧乏ゆすりをしたり、負けず嫌いすぎてゲームで本気になったりする姿は、周囲に「手のかかる暴れん坊」として愛されています。",
        "shadow_phase": "【ストレス反応：破壊的衝動】\n自分の正義が通じない環境に置かれると、すべてをリセットしたくなります。関係をバッサリ切ったり、積み上げたものを自ら壊したりと、衝動的な行動に出がちです。「もう知らない！」とちゃぶ台をひっくり返す前に、一度深呼吸が必要です。",
        "trivia": [
            "「結論から言うと」が口癖",
            "行列に並ぶくらいなら、店を変える",
            "負けず嫌いすぎて、じゃんけんでも勝ちたい",
            "お世辞を言われても「何が狙いだ？」と疑う",
            "即断即決すぎて、後でたまに後悔する"
        ],
        "impression_good": ["裏表がなく信頼できる", "決断が早くて頼もしい", "正義感が強い"],
        "impression_bad": ["デリカシーがない", "攻撃的で怖い", "人の話を聞かない"],
        "golden_rule_long": "『剣を収める』美学を、身につけよ。\nあなたの鋭さは誰もが認めています。だからこそ、あえてその剣を抜かずに、言葉と態度で相手を納得させる包容力を身につけた時、あなたは単なる「暴れん坊」から、時代を創る「英雄」になります。",
        "cta_text": COMMON_CTA
    },
    7: { # Type 8: 辛 (Metal-)
        "name": "貴族 (THE ARISTOCRAT)",
        "color": "#546E7A",
        "catch": "「一般人扱い」されると原因不明の体調不良になる",
        "phrases": ["私って可哀想", "ありえない", "そうかなぁ？（もっと褒めて）"],
        "fate_code_type": "SRDM",
        "default_scores": {'Identity':3, 'Create':2, 'Economy':3, 'Status':5, 'Vitality':4},
        "intro": "あなたは、泥の中から掘り出され、磨かれることで輝きを放つ宝石のように、特別なオーラを纏った人です。生まれながらにして「その他大勢」とは違う気品や美意識を持っており、俗世間の雑多なものとは一線を画しています。試練や苦労が多い人生かもしれませんが、それを乗り越えるたびに人間的な深みと魅力が増し、人々を魅了するカリスマへと成長していきます。",
        "social_style": "【対人スタイル：高貴な選民】\nプライドが高く、自分を安売りしません。誰とでも仲良くするわけではなく、自分の美意識に敵う相手だけをテリトリーに入れます。\n一方で、心を許した相手には非常に甘えん坊で、ワガママな一面を見せます。「私のことを一番に扱ってほしい」という願望が強く、少しでも蔑ろにされると、この世の終わりのように傷つき、殻に閉じこもってしまいます。",
        "inner_drive": "【本音と欠点：特別への執着】\nあなたが最も恐れているのは「埋没すること」です。自分は何者かであるはずだ、という強い自負があり、常に完璧で美しい自分であろうと努力しています。\n愛すべき欠点は、その「メンタルの弱さ」です。普段はツンとしていても、批判されるとガラスのように砕け散り、メソメソと悩み続ける。そのギャップが、守ってあげたいという周囲の庇護欲を刺激します。",
        "shadow_phase": "【ストレス反応：自虐と他責】\n傷つくことを極端に恐れるあまり、先回りして「どうせ私なんて」と自虐するか、逆に「周りのレベルが低い」と他責にして自分を守ろうとします。自尊心が傷つけられると、相手を徹底的に無視するなど、攻撃的ではなく「遮断」によって報復します。",
        "trivia": [
            "汚い言葉や、下品な振る舞いが生理的に無理",
            "LINEの既読スルーは「重罪」だと認定している",
            "褒められるときは「具体的」じゃないと響かない",
            "自分へのご褒美（スイーツや服）が多すぎる",
            "プライドが高すぎて、謝るのが死ぬほど下手"
        ],
        "impression_good": ["センスが良く洗練されている", "プロ意識が高い", "独特のカリスマ性がある"],
        "impression_bad": ["プライドが高くて面倒", "傷つきやすく扱いづらい", "ワガママなお姫様・王子様"],
        "golden_rule_long": "『傷』を『勲章』に、変える強さを持て。\n傷つくことを恐れないでください。原石は削られなければ輝きません。辛い経験やコンプレックスさえも、あなたという物語を彩るスパイスとして愛せた時、あなたは誰よりも美しく輝きます。",
        "cta_text": COMMON_CTA
    },
    8: { # Type 9: 壬 (Water+)
        "name": "宇宙人 (THE ALIEN)",
        "color": "#1565C0",
        "catch": "予定が決まった瞬間にドタキャンしたくなる",
        "phrases": ["なんとかなるっしょ", "行けたら行く", "束縛しないで"],
        "fate_code_type": "SGIM",
        "default_scores": {'Identity':3, 'Create':5, 'Economy':2, 'Status':2, 'Vitality':5},
        "intro": "あなたは、留まることを知らない大河や、大海原のように、圧倒的なスケールと流動性を持った自由人です。既存の枠組みや常識に囚われず、常に新しい世界、新しい価値観を求めて彷徨っています。「普通はこうする」という言葉は、あなたにとっては何の意味も持ちません。そのダイナミックな生き様と、夢を語るロマンチストな一面は、多くの人を惹きつけ、新しい風を吹き込みます。",
        "social_style": "【対人スタイル：来る者拒まず去る者追わず】\n誰とでもフランクに接し、すぐに打ち解けるコミュニケーション能力を持っています。しかし、誰か一人に執着することはなく、風のように現れては去っていきます。\n「束縛」を何よりも嫌い、責任や約束で縛られそうになると、本能的に逃げ出します。つかみどころがなく、本心がどこにあるのか誰にも（自分でも）わからないミステリアスな魅力があります。",
        "inner_drive": "【本音と欠点：停滞への恐怖】\nあなたが動き続けるのは、止まると水が澱んでしまうように、自分が腐ってしまう気がするからです。常に「ここではないどこか」を探しています。\n愛すべき欠点は、驚くべき「無責任さ」です。大事な局面で「飽きた」と言い出したり、面倒な約束をドタキャンしたり。しかし、その悪びれない天真爛漫さが、なぜか許されてしまう徳を持っています。",
        "shadow_phase": "【ストレス反応：氾濫と逃走】\n狭いルールに押し込められると、感情が決壊して大暴れするか、あるいは一切の連絡を絶って蒸発（逃亡）します。ストレス耐性は意外と低く、嫌なことがあると現実逃避に走り、長い眠りについたり、放浪の旅に出たりします。",
        "trivia": [
            "昨日と言っていることが180度違うことがある",
            "「一生のお願い」を人生で100回くらい使っている",
            "旅行の計画は立てず、当日の気分で決める",
            "束縛の激しい恋人とは3日で別れる自信がある",
            "知的好奇心は凄まじいが、持続力は3日坊主"
        ],
        "impression_good": ["スケールが大きく夢がある", "一緒にいるとワクワクする", "発想が柔軟"],
        "impression_bad": ["無責任でルーズ", "何を考えているかわからない", "すぐに逃げる"],
        "golden_rule_long": "『帰る場所』を、一つだけ作れ。\n自由であることと、根無し草であることは違います。どんなに遠くへ行っても、そこに戻れば自分らしくいられる「港（パートナーや拠点）」を持つことで、あなたの航海はより遠くまで、より安全に続くようになります。",
        "cta_text": COMMON_CTA
    },
    9: { # Type 10: 癸 (Water-)
        "name": "全肯定bot (THE YES-MAN)",
        "color": "#1565C0",
        "catch": "争いを避けるためなら死んだふりもする",
        "phrases": ["いいと思います", "すいません", "あ、大丈夫です"],
        "fate_code_type": "LRDY",
        "default_scores": {'Identity':2, 'Create':4, 'Economy':3, 'Status':2, 'Vitality':5},
        "intro": "あなたは、大地を潤す雨や霧のように、静かに周囲に浸透し、人々の心に寄り添う癒やしの存在です。派手な自己主張はしませんが、驚くほどの知識と知恵を蓄えており、物事の裏側や人の本質を冷静に見抜いています。他人の痛みや悲しみを、まるで自分のことのように感じる共感能力（エンパス）を持っており、傷ついた人々が最後に辿り着く「避難所」のような役割を果たします。",
        "social_style": "【対人スタイル：同調と献身】\nあなたは「水」のように、相手の形に合わせて自分を変えることができます。攻撃的な人の前では受け流し、悲しむ人の前では共に泣く。その柔軟性は組織の潤滑油として重宝されます。\nしかし、自分の意見を飲み込み、ニコニコしてやり過ごすことが多いため、ストレスを内側に溜め込みがちです。表面上は穏やかですが、内面では冷静に相手を分析し、評価を下しているシビアな一面もあります。",
        "inner_drive": "【本音と欠点：自己の希薄さ】\n相手に合わせすぎて、「本当の自分がわからない」という悩みを抱えがちです。誰かの役に立つことで自分の輪郭を確かめようとします。\n愛すべき欠点は、限界を超えた時の「サイレント絶交」です。嫌だと言えずに我慢し続け、ある日突然、何の前触れもなく連絡先をブロックして関係を断ち切る。その静かなる拒絶は、周囲を震撼させます。",
        "shadow_phase": "【ストレス反応：自己卑下と遮断】\nネガティブな感情に支配されると、「私なんていない方がいい」と極端に落ち込み、殻に閉じこもります。外界からの情報をすべて遮断し、内面世界に沈み込んでいくため、周囲からは急に連絡が取れなくなったように見えます。",
        "trivia": [
            "大人数の飲み会より、サシ飲みが好き",
            "妄想や空想をしている時間が一番幸せ",
            "嫌なことがあると、寝てリセットしようとする",
            "「何でもいいよ」と言うときは、本当に何でもいい",
            "実は、かなりマニアックなオタク趣味がある"
        ],
        "impression_good": ["聞き上手で癒やされる", "知識が豊富で賢い", "空気が読める"],
        "impression_bad": ["本音が見えない", "ネガティブで暗い", "急に心を閉ざす"],
        "golden_rule_long": "『自分』という器を、意識的に持て。\n水は器によって形を変えますが、あなた自身の形も大切にしてください。「私はこう思う」「私はこれが嫌だ」という核を持つことで、あなたは周囲に流されるだけでなく、自らの意思で大河のような流れを作れる賢者になります。",
        "cta_text": COMMON_CTA
    }
}

# --- 定数データ ---
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
    0: ["No.6 オカン", "No.7 特攻隊長", "No.4 教祖"], 
    1: ["No.7 特攻隊長", "No.8 貴族", "No.3 センター"],
    2: ["No.8 貴族", "No.9 宇宙人", "No.5 長老"], 
    3: ["No.9 宇宙人", "No.10 全肯定bot", "No.6 オカン"],
    4: ["No.10 全肯定bot", "No.1 鬼軍曹", "No.7 特攻隊長"], 
    5: ["No.1 鬼軍曹", "No.2 裏回し", "No.8 貴族"],
    6: ["No.2 裏回し", "No.3 センター", "No.9 宇宙人"], 
    7: ["No.3 センター", "No.4 教祖", "No.10 全肯定bot"],
    8: ["No.4 教祖", "No.5 長老", "No.1 鬼軍曹"], 
    9: ["No.5 長老", "No.6 オカン", "No.2 裏回し"]
}

# ==========================================
# 4. Logic Engines (Fortune & Science)
# ==========================================

def calculate_big5(answers):
    """TIPI-Jの回答からビッグファイブスコアを算出"""
    scores_raw = {
        "Extraversion": answers["Q1"] + (8 - answers["Q6"]),
        "Agreeableness": (8 - answers["Q2"]) + answers["Q7"],
        "Conscientiousness": answers["Q3"] + (8 - answers["Q8"]),
        "Neuroticism": answers["Q4"] + (8 - answers["Q9"]),
        "Openness": answers["Q5"] + (8 - answers["Q10"])
    }
    # 1-5段階へ正規化
    scores_norm = {k: round(1 + (v - 2) * 4 / 12, 1) for k, v in scores_raw.items()}
    return scores_raw, scores_norm

def analyze_big5_gap(scores_norm, fate_type_id):
    """宿命(Type)と現在(Big5)のギャップからフック文章を生成"""
    is_gap = False
    # 簡易ギャップ判定ロジック
    if fate_type_id in [0, 2, 6] and scores_norm["Extraversion"] < 2.5: is_gap = True
    elif fate_type_id in [1, 9] and scores_norm["Agreeableness"] < 2.5: is_gap = True
    elif fate_type_id in [4, 7] and scores_norm["Conscientiousness"] < 2.5: is_gap = True
    
    if is_gap: return "⚠️ 注意：あなたの本来の才能が、現在60%死んでいます。"
    else: return "✨ 素晴らしい：宿命通りに才能が発揮されています。ただし…"

class FortuneEngineIntegrated:
    """四柱推命ベースの運命解析エンジン"""
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

        axis_1 = "L" if counts["Vitality"] >= counts["Create"] else "S"
        defensive = counts["Status"] + counts["Vitality"]
        offensive = counts["Economy"] + counts["Create"]
        axis_2 = "R" if defensive >= offensive else "G"
        energy_sum = ENERGY_STRENGTH[gan][zhi] + ENERGY_STRENGTH[gan][m_zhi] + ENERGY_STRENGTH[gan][y_zhi]
        axis_3 = "I" if energy_sum >= 6 else "D"
        social = counts["Economy"] + counts["Status"]
        axis_4 = "M" if counts["Identity"] * 1.5 >= social else "Y"
        fate_code = f"{axis_1}{axis_2}{axis_3}{axis_4}"

        return {"gan": gan, "scores": normalized_scores, "fate_code": fate_code, "partners": COMPATIBILITY_MAP.get(gan, [])}

# ==========================================
# 5. UI Component Function (Ver Final_CTA_Fixed)
# ==========================================
def render_result_component(content, fate_code, fate_scores, big5_norm=None, is_catalog=False, key_suffix=""):
    """
    診断結果と図鑑で共通して使用する表示コンポーネント
    """
    theme_color = content.get('color', '#333')
    
    # 修正1: FATE Code説明文をここに移動
    st.info("【FATE Codeとは？】\nInput（情報の取り方） / Process（判断基準） / Output（行動特性） / Drive（原動力） の4要素であなたの行動原理を解明するコードです。この『クセ』を知ることで、なぜ同じ失敗を繰り返すのかが分かり、あなただけの『勝ちパターン』が見えてきます。")
    
    # --- 1. HERO SECTION (表の顔) ---
    st.subheader("【表の顔】社会的役割としてのあなた")
    
    st.markdown(f'<div class="read-card" style="border-top: 10px solid {theme_color};">', unsafe_allow_html=True)
    
    # Name & Catch
    st.markdown(f"<div class='type-name-huge' style='color:{theme_color};'>{content['name']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='catch-subtitle'>{content['catch']}</div>", unsafe_allow_html=True)
    
    # Phrases (Bubbles)
    phrases_html = "".join([f"<div class='phrase-bubble'>{p}</div>" for p in content['phrases']])
    st.markdown(f"<div class='phrase-container'>{phrases_html}</div>", unsafe_allow_html=True)
    
    # Image Logic
    type_id = 1
    for k, v in DIAGNOSIS_CONTENT.items():
        if v['name'] == content['name']:
            type_id = k + 1
            break
            
    img_path = load_image(type_id)
    if img_path: st.image(img_path, use_container_width=True)
    else: st.image("https://placehold.co/400x400/F0F0F0/333?text=No+Image", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 2. FATE CODE EXPLANATION ---
    st.markdown(f"<h3>🧬 【あなたのFATE Code解析】</h3>", unsafe_allow_html=True)
    st.markdown('<div class="read-card" style="padding: 15px;">', unsafe_allow_html=True)
    st.write(f"あなたのコード: **{fate_code}**")
    for char in list(fate_code):
        meaning = FATE_MEANINGS.get(char, "不明")
        st.markdown(f"<div class='fate-meaning-box'><span class='fate-char'>{char}</span> {meaning}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 3. STORY SECTION ---
    st.markdown('<div class="read-card">', unsafe_allow_html=True)
    
    # 修正2: 「表の性格」タイトルの追加
    st.markdown(f"<h3 style='border-color:{theme_color};'>【表の性格】</h3>", unsafe_allow_html=True)
    
    st.markdown(f"<div style='font-size:1.1rem; font-weight:bold; margin-bottom:20px; line-height:2.0;'>{content['intro']}</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f"<h3 style='border-color:{theme_color};'>① 対人関係のスタイル</h3>", unsafe_allow_html=True)
    st.write(content['social_style'])

    st.markdown(f"<h3 style='border-color:{theme_color};'>② 隠された本音と欠点</h3>", unsafe_allow_html=True)
    st.write(content['inner_drive'])

    st.markdown(f"<h3 style='border-color:{theme_color};'>③ ストレス時の『影』</h3>", unsafe_allow_html=True)
    st.write(content['shadow_phase'])

    # Impression
    st.markdown(f"<h3 style='border-color:{theme_color};'>④ 周囲からの評判</h3>", unsafe_allow_html=True)
    col_g, col_b = st.columns(2)
    with col_g:
        st.markdown(f"<div class='impression-box impression-good'><b>Good</b><br>{'<br>'.join(['・'+i for i in content['impression_good']])}</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"<div class='impression-box impression-bad'><b>Bad</b><br>{'<br>'.join(['・'+i for i in content['impression_bad']])}</div>", unsafe_allow_html=True)

    # Trivia
    st.markdown(f"<h3 style='border-color:{theme_color};'>⑤ あなたの『あるある』</h3>", unsafe_allow_html=True)
    for t in content['trivia']:
        st.markdown(f"✔ {t}")

    # Golden Rule
    st.markdown(f"<div class='golden-rule'><b>GOLDEN RULE</b><br><br><span style='font-size:1.2rem; font-weight:bold;'>{content['golden_rule_long']}</span></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 4. ANALYSIS SECTION (裏の顔) ---
    st.subheader("【裏の顔】潜在的な本質とズレ")
    
    # チャートエリア
    st.markdown('<div class="read-card" style="position:relative; overflow:hidden;">', unsafe_allow_html=True)
    
    # チャート説明文
    st.markdown("""
    <div class="chart-desc">
    <b>オレンジ（表の顔）</b>に対し、<b>青（裏の顔）が大きすぎる場合は『才能の暴走（空回り）』、小さすぎる場合は『ポテンシャル不足』</b>を示します。<br>
    この『出力のズレ』を調整し、あなたの本来の力を100%発揮させるための『精密心理分析ロジック』がここにあります。
    </div>
    """, unsafe_allow_html=True)
    
    # チャート描画
    categories = ['外向性', '開放性', '協調性', '勤勉性', '安定性']
    fig = go.Figure()
    
    # 宿命 (Orange)
    f_vals = [fate_scores['Identity'], fate_scores['Create'], fate_scores['Economy'], fate_scores['Status'], fate_scores['Vitality']]
    fig.add_trace(go.Scatterpolar(r=f_vals, theta=categories, fill='toself', name='宿命(表)', line_color='#E65100'))
    
    # 現在 (Blue) - 診断時のみ
    if not is_catalog and big5_norm:
        s_vals = [big5_norm['Extraversion'], big5_norm['Openness'], big5_norm['Agreeableness'], big5_norm['Conscientiousness'], 6 - big5_norm['Neuroticism']]
        fig.add_trace(go.Scatterpolar(r=s_vals, theta=categories, fill='toself', name='現在(裏)', line_color='#1A237E'))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(color='#999')),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(t=20, b=20, l=40, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#333')),
        font=dict(color='#333')
    )
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True}, key=f"radar_{key_suffix}")

   # === CTA AREA (診断時のみ) ===
    if not is_catalog:
        # CTAボタン1
        st.link_button("👉 ズレを武器に変える『裏・攻略法』を見る（LINE登録）", "https://line.me/R/ti/p/dummy_id", type="primary", use_container_width=True)
        
        # 修正: インデントなしのHTML定義（デザイン強化版）
        cta_html = """
<div style="margin-top: 30px; background-color: #FAFAFA; border: 3px solid #D32F2F; border-radius: 15px; padding: 20px; text-align: center; position: relative; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
<div style="background: #D32F2F; color: #fff; font-weight: 900; font-size: 1.1rem; padding: 8px 20px; border-radius: 30px; display: inline-block; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">🔒 LINE限定：心理学ロジックで解き明かす『あなたの真実』</div>

<div style="text-align: left; margin: 0 auto 25px auto; display: inline-block; width: 95%;">
<div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 12px; color: #333; line-height: 1.5;">
<span style="color: #D32F2F; font-size: 1.3rem;">⚠️ 【警告】</span>あなたの才能が『自滅』するパターンの特定
</div>
<div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 12px; color: #333; line-height: 1.5;">
<span style="color: #D32F2F; font-size: 1.3rem;">💰 【仕事】</span>『裏の武器』を使って年収を倍にする具体的戦略
</div>
<div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 12px; color: #333; line-height: 1.5;">
<span style="color: #D32F2F; font-size: 1.3rem;">💘 【恋愛】</span>あなたの『本性』を全肯定してくれる運命の相手
</div>
</div>

<div style="background-color: #FFFDE7; border: 2px solid #FFD600; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
<div style="color: #E65100; font-weight: 900; font-size: 1.3rem; line-height: 1.4;">
📊 【相性】全タイプ網羅！<br>『運命の相関マトリクス図』
</div>
</div>

<div style="background-color: #FFEBEE; border: 2px solid #FF5252; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
<div style="color: #C62828; font-weight: 900; font-size: 1.3rem; line-height: 1.4; margin-bottom: 8px;">
🎁 【登録特典】あなたの『表と裏』を一枚に！<br>『ステータス診断カード』
</div>
<div style="font-size: 0.95rem; font-weight: bold; color: #555;">
※ 登録後すぐに自動で送られます。<br>インスタでシェアして本当の自分を表現しよう。
</div>
</div>

<div style="filter: blur(5px); opacity: 0.6; user-select: none; font-size: 0.8rem;">
ここにあなたの性格の裏側に関する詳細なレポートが表示されます。なぜあなたは人間関係で同じ失敗を繰り返してしまうのか？その原因は幼少期の体験にあるかもしれません。このレポートを読むことで、あなたは二度と同じ過ちを繰り返さず、本来の輝きを取り戻すことができるでしょう...
</div>

<div style="position: absolute; top: 65%; left: 50%; transform: translate(-50%, -50%); width: 100%; z-index: 10;">
<div style="background: rgba(255,255,255,0.9); display: inline-block; padding: 10px 20px; border-radius: 50px; border: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
<span style="font-weight:bold; font-size:1rem; color:#333;">🔓 封印されたレポートを今すぐ読む</span>
</div>
</div>
</div>
"""
        st.markdown(cta_html, unsafe_allow_html=True)
        
        # CTAボタン2
        st.link_button("🔓 封印されたレポートを今すぐ読む（無料）", "https://line.me/R/ti/p/dummy_id", type="primary", use_container_width=True)
    else:
        st.caption("※ 実際の診断では、ここに詳細な「裏性格レポート」と「相性マトリクス」が表示されます。")

# ==========================================
# 6. Main UI Application (Ver Final_CTA_Fixed)
# ==========================================

st.title("Project MAP")
main_tab, catalog_tab = st.tabs(["運命を診断する", "全タイプ図鑑"])

# --- Tab 1: 診断 & 結果 ---
with main_tab:
    # A. 入力フォーム
    with st.form("diagnosis_form"):
        # FATE Code説明文は render_result_component に移動したため削除
        
        st.markdown("### 1. 生年月日")
        col_y, col_m, col_d = st.columns([1.2, 1, 1])
        with col_y: year = st.selectbox("年", list(range(1900, 2031)), index=95)
        with col_m: month = st.selectbox("月", list(range(1, 13)), index=0)
        with col_d: day = st.selectbox("日", list(range(1, 32)), index=0)
            
        st.markdown("---")
        st.markdown("### 2. 性格診断 (任意)")
        st.caption("直感で答えてください（1:全く違う 〜 7:強くそう思う）")
        
        tipi_answers = {}
        for q_id, q_text in TIPI_QUESTIONS.items():
            st.markdown(f"**{q_text}**")
            tipi_answers[q_id] = st.slider("", 1, 7, 4, key=f"f_{q_id}", label_visibility="collapsed")
            st.markdown("") 
            
        submitted = st.form_submit_button("診断結果を見る", type="primary", use_container_width=True)
    
    # B. 結果表示
    if submitted:
        try:
            date_obj = datetime.date(year, month, day)
            date_str = date_obj.strftime("%Y/%m/%d")
            
            engine = FortuneEngineIntegrated()
            result = engine.analyze_basic(date_str)
            gan_id = result['gan']
            content = DIAGNOSIS_CONTENT[gan_id]
            fate_scores = result['scores']
            fate_code = result['fate_code']
            
            # Big Five 計算
            _, big5_norm = calculate_big5(tipi_answers)
            
            # 共通コンポーネント呼び出し
            render_result_component(content, fate_code, fate_scores, big5_norm, is_catalog=False, key_suffix="main")

        except ValueError:
            st.error("正しい日付を選択してください。")

# --- Tab 2: 全タイプ図鑑 ---
with catalog_tab:
    st.markdown("### 全10タイプ図鑑")
    st.caption("タップして詳細を展開")
    
    for i in range(10):
        c = DIAGNOSIS_CONTENT[i]
        
        with st.expander(f"Type {i+1}: {c['name']}"):
            # 図鑑用データ
            dummy_fate_code = c.get('fate_code_type', 'XXXX')
            dummy_scores = c.get('default_scores', {'Identity':3, 'Create':3, 'Economy':3, 'Status':3, 'Vitality':3})
            
            # 共通コンポーネント呼び出し
            render_result_component(c, dummy_fate_code, dummy_scores, big5_norm=None, is_catalog=True, key_suffix=f"cat_{i}")
