import streamlit as st
import numpy as np
import time
from streamlit_js_eval import streamlit_js_eval
from streamlit.components.v1 import html

# 设置页面配置
st.set_page_config(
    page_title="贪吃蛇游戏",
    page_icon="🐍",
    layout="centered"
)

# 游戏常量
GRID_SIZE = 20
CANVAS_SIZE = 400
INITIAL_SNAKE_LENGTH = 3
FOOD_PER_LEVEL = 10

# 初始化游戏状态
if 'snake' not in st.session_state:
    st.session_state.snake = []
if 'direction' not in st.session_state:
    st.session_state.direction = 'right'
if 'food' not in st.session_state:
    st.session_state.food = None
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'level' not in st.session_state:
    st.session_state.level = 1
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

# 游戏辅助函数
def init_snake():
    st.session_state.snake = []
    start_x = (CANVAS_SIZE // (2 * GRID_SIZE)) * GRID_SIZE
    start_y = (CANVAS_SIZE // (2 * GRID_SIZE)) * GRID_SIZE
    for i in range(INITIAL_SNAKE_LENGTH):
        st.session_state.snake.append({'x': start_x - (i * GRID_SIZE), 'y': start_y})

def generate_food():
    while True:
        x = np.random.randint(0, CANVAS_SIZE // GRID_SIZE) * GRID_SIZE
        y = np.random.randint(0, CANVAS_SIZE // GRID_SIZE) * GRID_SIZE
        valid_position = True
        for segment in st.session_state.snake:
            if segment['x'] == x and segment['y'] == y:
                valid_position = False
                break
        if valid_position:
            st.session_state.food = {'x': x, 'y': y}
            break

def reset_game():
    st.session_state.score = 0
    st.session_state.level = 1
    st.session_state.direction = 'right'
    st.session_state.game_over = False
    init_snake()
    generate_food()

# 创建游戏界面
st.title('🐍 贪吃蛇游戏')

# 显示游戏信息
col1, col2 = st.columns(2)
with col1:
    st.metric("分数", st.session_state.score)
with col2:
    st.metric("关卡", st.session_state.level)

# 添加游戏控制按钮
if st.button('开始新游戏'):
    reset_game()

# 添加键盘控制的JavaScript代码
keyboard_js = """
<script>
document.addEventListener('keydown', function(e) {
    if (e.key.startsWith('Arrow')) {
        e.preventDefault();
        window.parent.postMessage({type: 'keyboard', key: e.key}, '*');
    }
});
</script>
"""
html(keyboard_js, height=0)

# 游戏主循环
if not st.session_state.game_over and st.session_state.snake:
    # 处理键盘输入
    key_event = streamlit_js_eval(js_expressions='window.parent.keyEvent', key='keyboard')
    if key_event:
        if key_event == 'ArrowUp' and st.session_state.direction != 'down':
            st.session_state.direction = 'up'
        elif key_event == 'ArrowDown' and st.session_state.direction != 'up':
            st.session_state.direction = 'down'
        elif key_event == 'ArrowLeft' and st.session_state.direction != 'right':
            st.session_state.direction = 'left'
        elif key_event == 'ArrowRight' and st.session_state.direction != 'left':
            st.session_state.direction = 'right'

    # 更新蛇的位置
    head = dict(st.session_state.snake[0])
    if st.session_state.direction == 'up':
        head['y'] -= GRID_SIZE
    elif st.session_state.direction == 'down':
        head['y'] += GRID_SIZE
    elif st.session_state.direction == 'left':
        head['x'] -= GRID_SIZE
    elif st.session_state.direction == 'right':
        head['x'] += GRID_SIZE

    # 检查碰撞
    if (head['x'] < 0 or head['x'] >= CANVAS_SIZE or
        head['y'] < 0 or head['y'] >= CANVAS_SIZE):
        st.session_state.game_over = True
    
    for segment in st.session_state.snake[1:]:
        if head['x'] == segment['x'] and head['y'] == segment['y']:
            st.session_state.game_over = True

    if not st.session_state.game_over:
        # 检查是否吃到食物
        if head['x'] == st.session_state.food['x'] and head['y'] == st.session_state.food['y']:
            st.session_state.snake.insert(0, head)
            st.session_state.score += 1
            if st.session_state.score % FOOD_PER_LEVEL == 0:
                st.session_state.level += 1
            generate_food()
        else:
            st.session_state.snake.insert(0, head)
            st.session_state.snake.pop()

# 使用Streamlit的canvas组件绘制游戏画面
from streamlit_drawable_canvas import st_canvas

# 创建画布
canvas_data = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 4), dtype=np.uint8)

# 绘制蛇
for segment in st.session_state.snake:
    x, y = segment['x'], segment['y']
    canvas_data[y:y+GRID_SIZE-2, x:x+GRID_SIZE-2] = [76, 175, 80, 255]  # 蛇身颜色 #4CAF50

# 绘制蛇头
if st.session_state.snake:
    head = st.session_state.snake[0]
    canvas_data[head['y']:head['y']+GRID_SIZE-2, head['x']:head['x']+GRID_SIZE-2] = [56, 142, 60, 255]  # 蛇头颜色 #388E3C

# 绘制食物
if st.session_state.food:
    food_x, food_y = st.session_state.food['x'], st.session_state.food['y']
    canvas_data[food_y:food_y+GRID_SIZE-2, food_x:food_x+GRID_SIZE-2] = [244, 67, 54, 255]  # 食物颜色 #F44336

# 显示画布
st_canvas(
    fill_color="#ffffff",
    stroke_width=0,
    background_color="#f1f8e9",
    height=CANVAS_SIZE,
    width=CANVAS_SIZE,
    drawing_mode="freedraw",
    key="canvas",
    initial_drawing=canvas_data
)

# 显示游戏结束信息
if st.session_state.game_over:
    st.error('游戏结束！点击"开始新游戏"重新开始')

# 添加自动刷新
time.sleep(0.2)
st.experimental_rerun()