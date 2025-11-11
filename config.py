"""
JID×QUEST - ゲーム設定定数
スーパーファミコン風RPGの基本設定
"""

# 画面設定
SCREEN_WIDTH = 256  # SFC標準解像度
SCREEN_HEIGHT = 224
SCALE_FACTOR = 3  # 3倍拡大表示 (768x672)
DISPLAY_WIDTH = SCREEN_WIDTH * SCALE_FACTOR
DISPLAY_HEIGHT = SCREEN_HEIGHT * SCALE_FACTOR

# ゲーム設定
FPS = 60
TILE_SIZE = 16
LANGUAGE = 'ja'  # 日本語固定

# サーバー設定
SERVER_PORT = 4000  # ローカルサーバーポート
SERVER_HOST = 'localhost'

# カラーパレット (SFC風)
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'BLUE': (0, 88, 248),
    'DARK_BLUE': (0, 0, 168),
    'LIGHT_BLUE': (120, 168, 248),
    'TEXT_WHITE': (248, 248, 248),
    'WINDOW_BLUE': (0, 120, 248),
    'WINDOW_DARK': (0, 56, 136),
    'GOLD': (248, 184, 0),
}

# フォント設定
FONT_SIZE = 8
MESSAGE_SPEED = 2  # 文字表示速度（フレーム数）

# プレイヤー設定
PLAYER_SPEED = 2

# バトル設定
BATTLE_TRANSITION_FRAMES = 30
DAMAGE_VARIANCE = 0.1  # ダメージの乱数幅 (±10%)

# ゲームパス
SAVE_FILE = 'data/save_data.json'
CHARACTERS_DATA = 'data/game_data/characters.json'
MAPS_DIR = 'data/maps/'
DIALOGUES_DIR = 'data/dialogues/'

# ゲーム状態
class GameState:
    TITLE = 'title'
    FIELD = 'field'
    BATTLE = 'battle'
    MENU = 'menu'
    DIALOGUE = 'dialogue'
    EVENT = 'event'

# 役職レベル定義
RANK_LEVELS = {
    1: "アドバイザー",
    11: "スーパーバイザー",
    21: "チーフアドバイザー",
    31: "サブリーダー",
    41: "リーダー",
    51: "マネージャー",
    66: "部長",
    81: "役員",
}

def get_rank_name(level):
    """レベルから役職名を取得"""
    rank = "アドバイザー"
    for req_level, rank_name in sorted(RANK_LEVELS.items(), reverse=True):
        if level >= req_level:
            rank = rank_name
            break
    return rank
