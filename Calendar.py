import calendar
import datetime
import json
import os
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="정윤우의 스마트 과제 스케줄러", page_icon="🦖", layout="wide"
)

# 모던 네이비 톤 및 세련된 카드 레이아웃 CSS 적용
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* 메인 타이틀 배너 카드 (네이비 톤) */
    .dashboard-header {
        background: linear-gradient(135deg, #1E3A8A 100%, #3B82F6 0%);
        padding: 25px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .dashboard-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .dashboard-header p {
        margin: 5px 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* 그룹 섹션 스타일 */
    .group-section-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.01);
    }
    .group-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 2px solid #F1F5F9;
        padding-bottom: 10px;
    }
    
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    </style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = "yunwoo_tasks.json"

# 기본 고정 과제 리스트 (당일 3개 + 주간 2개 순서 유지)
DEFAULT_TASKS = [
    {
        "id": "fixed_1",
        "title": "최상위 수학 문제집 풀기",
        "type": "매일 당일 완료",
        "status": "미진행",
        "memo": "",
        "category": "고정",
    },
    {
        "id": "fixed_2",
        "title": "영어책 리딩",
        "type": "매일 당일 완료",
        "status": "미진행",
        "memo": "",
        "category": "고정",
    },
    {
        "id": "fixed_4",
        "title": "한글책 읽기",
        "type": "매일 당일 완료",
        "status": "미진행",
        "memo": "",
        "category": "고정",
    },
    {
        "id": "fixed_3",
        "title": "퍼플 학습",
        "type": "일주일 목표",
        "status": "미진행",
        "memo": "",
        "category": "고정",
    },
    {
        "id": "fixed_5",
        "title": "국어 독해 2개 단원",
        "type": "일주일 목표",
        "status": "미진행",
        "memo": "",
        "category": "고정",
    },
]


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


db_data = load_data()
today_str = datetime.date.today().strftime("%Y-%m-%d")


def initialize_date(target_date_str):
    if target_date_str not in db_data:
        if target_date_str == today_str:
            yesterday_str = (
                datetime.date.today() - datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d")
            tasks_to_add = []

            if yesterday_str in db_data:
                for t in db_data[yesterday_str]:
                    if t["type"] == "매일 당일 완료" and t["status"] != "완료":
                        tasks_to_add.append(
                            {
                                "id": f"{target_date_str}_{t['title']}",
                                "title": t["title"],
                                "type": t["type"],
                                "status": "미진행",
                                "memo": "",
                                "category": t.get("category", "수동"),
                            }
                        )

            base_tasks = []
            for t in DEFAULT_TASKS:
                base_tasks.append(
                    {
                        "id": f"{target_date_str}_{t['id']}",
                        "title": t["title"],
                        "type": t["type"],
                        "status": "미진행",
                        "memo": "",
                        "category": t["category"],
                    }
                )

            existing_titles = [bt["title"] for bt in base_tasks]
            for t in tasks_to_add:
                if t["title"] not in existing_titles:
                    base_tasks.append(t)
                    existing_titles.append(t["title"])

            db_data[target_date_str] = base_tasks
        else:
            base_tasks = []
            for t in DEFAULT_TASKS:
                base_tasks.append(
                    {
                        "id": f"{target_date_str}_{t['id']}",
                        "title": t["title"],
                        "type": t["type"],
                        "status": "미진행",
                        "memo": "",
                        "category": t["category"],
                    }
                )
            db_data[target_date_str] = base_tasks
        save_data(db_data)


# 세션 상태 초기화
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date.today()

# ==================== 사이드바 구성 ====================
st.sidebar.markdown("### 🦖 윤우의 대시보드")
st.sidebar.caption("오늘도 멋지게 미션을 완수해 볼까요?")

picked_date = st.sidebar.date_input(
    "📅 날짜 바로 선택", value=st.session_state.selected_date
)
st.session_state.selected_date = picked_date
st.sidebar.divider()

current_year = st.session_state.selected_date.year
current_month = st.session_state.selected_date.month

st.sidebar.markdown(f"#### 🗓️ {current_year}년 {current_month}월 달력")

cal = calendar.monthcalendar(current_year, current_month)
week_days = ["월", "화", "수", "목", "금", "토", "일"]

cols = st.sidebar.columns(7)
for idx, day_name in enumerate(week_days):
    cols[idx].markdown(
        f"<div style='text-align: center; font-size:11px; font-weight: 700; color: #475569;'>{day_name}</div>",
        unsafe_allow_html=True,
    )

for week in cal:
    cols = st.sidebar.columns(7)
    for idx, day in enumerate(week):
        if day == 0:
            cols[idx].write("")
        else:
            date_str = f"{current_year}-{current_month:02d}-{day:02d}"
            day_tasks = db_data.get(date_str, [])
            icon = ""
            if day_tasks:
                if all(t["status"] == "완료" for t in day_tasks):
                    icon = "⭐"
                elif any(t["status"] in ["진행중", "완료"] for t in day_tasks):
                    icon = "🔥"

            btn_text = f"{day}{icon}"
            if cols[idx].button(
                btn_text, key=f"cal_{date_str}", use_container_width=True
            ):
                st.session_state.selected_date = datetime.date(
                    current_year, current_month, day
                )
                st.rerun()

selected_date_str = st.session_state.selected_date.strftime("%Y-%m-%d")

# ==================== 메인 화면 구성 ====================
st.markdown(
    f"""
    <div class="dashboard-header">
        <h1>🌟 정윤우의 스마트 과제 대시보드</h1>
        <p>선택된 미션 날짜: <b>{selected_date_str}</b></p>
    </div>
""",
    unsafe_allow_html=True,
)

if selected_date_str == today_str:
    initialize_date(selected_date_str)

current_tasks = db_data.get(selected_date_str, [])

if not current_tasks:
    st.info(
        f"📅 **{selected_date_str}**에 저장된 미션 기록이 없습니다. (미래 계획된 일정이거나 기록이 없는 날입니다.)"
    )
else:
    # 당일 과제와 주간 목표 과제 분리
    daily_tasks = [t for t in current_tasks if t["type"] == "매일 당일 완료"]
    weekly_tasks = [t for t in current_tasks if t["type"] == "일주일 목표"]

    # 각각의 달성률 계산
    daily_total = len(daily_tasks)
    daily_completed = sum(1 for t in daily_tasks if t["status"] == "완료")
    daily_progress = (
        daily_completed / daily_total if daily_total > 0 else 0.0
    )

    weekly_total = len(weekly_tasks)
    weekly_completed = sum(1 for t in weekly_tasks if t["status"] == "완료")
    weekly_progress = (
        weekly_completed / weekly_total if weekly_total > 0 else 0.0
    )

    # 상단 요약 메트릭 배치
    st.markdown("### 📊 영역별 미션 달성 현황")
    m_col1, m_col2 = st.columns(2)

    with m_col1:
        st.markdown(
            f"**🔥 당일 완료 미션** ({daily_completed}/{daily_total} 완료)"
        )
        st.progress(daily_progress)

    with m_col2:
        st.markdown(
            f"**🗓️ 일주일 목표 미션** ({weekly_completed}/{weekly_total} 완료)"
        )
        st.progress(weekly_progress)

    st.divider()

    st.markdown(f"### 📋 {selected_date_str} 미션 보드")

    status_options = ["미진행", "진행중", "완료"]
    updated_tasks_dict = {t["id"]: t.copy() for t in current_tasks}
    deleted_task_ids = set()


    def render_task_group(group_title, task_list):
        if not task_list:
            return

        st.markdown(
            f"""
            <div class="group-section-box">
                <div class="group-title">{group_title}</div>
            """,
            unsafe_allow_html=True,
        )

        for task in task_list:
            t_id = task["id"]
            idx = current_tasks.index(task)

            with st.container():
                status_color = (
                    "#10B981"
                    if task["status"] == "완료"
                    else (
                        "#F59E0B" if task["status"] == "진행중" else "#64748B"
                    )
                )
                type_badge_color = (
                    "#3B82F6"
                    if task["type"] == "매일 당일 완료"
                    else "#8B5CF6"
                )

                st.markdown(
                    f"""
                    <div style="background-color: #F8FAFC; padding: 14px 18px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-size: 1.05rem; font-weight: 700; color: #1E293B;">
                                📘 {task['title']} 
                                <span style="font-size: 0.75rem; font-weight: bold; color: white; background-color: {type_badge_color}; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">{task['type']}</span>
                            </span>
                            <span style="font-size: 0.8rem; font-weight: 700; color: white; background-color: {status_color}; padding: 2px 8px; border-radius: 6px;">
                                {task['status']}
                            </span>
                        </div>
                        <div style="font-size: 0.9rem; color: #475569; background-color: #FFFFFF; padding: 6px 10px; border-radius: 6px; margin-top: 4px; border: 1px solid #E2E8F0;">
                            📝 <b>수행 내용:</b> {task['memo'] if task['memo'] else '작성된 내용이 없습니다.'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_a, col_b, col_c = st.columns([1.5, 3, 0.6])

                with col_a:
                    curr_status = task.get("status", "미진행")
                    s_idx = (
                        status_options.index(curr_status)
                        if curr_status in status_options
                        else 0
                    )
                    selected_status = st.selectbox(
                        "상태 변경",
                        status_options,
                        index=s_idx,
                        key=f"status_{selected_date_str}_{idx}",
                        label_visibility="collapsed",
                    )

                with col_b:
                    memo_input = st.text_input(
                        "진행 내용 입력",
                        value=task.get("memo", ""),
                        key=f"memo_{selected_date_str}_{idx}",
                        placeholder="예: p.15~18까지 풀었음!",
                        label_visibility="collapsed",
                    )

                with col_c:
                    if st.button(
                        "삭제",
                        key=f"del_{selected_date_str}_{idx}",
                        use_container_width=True,
                    ):
                        deleted_task_ids.add(t_id)

                updated_tasks_dict[t_id]["status"] = selected_status
                updated_tasks_dict[t_id]["memo"] = memo_input

        st.markdown("</div>", unsafe_allow_html=True)


    # 1. 상단: 당일 완료 미션 3개 그룹 박스
    render_task_group("🔥 매일 당일 완료 미션", daily_tasks)

    # 2. 하단: 일주일 목표 미션 2개 그룹 박스
    render_task_group("🗓️ 일주일 목표 미션", weekly_tasks)

    sorted_current_tasks = daily_tasks + weekly_tasks
    final_tasks = [
        t
        for t in sorted_current_tasks
        if t["id"] not in deleted_task_ids
        and t["id"] in updated_tasks_dict
    ]
    for idx, t in enumerate(final_tasks):
        final_tasks[idx] = updated_tasks_dict[t["id"]]

    st.write("")
    if st.button(
        "💾 변경된 공부 기록 저장하기", type="primary", use_container_width=True
    ):
        db_data[selected_date_str] = final_tasks
        save_data(db_data)
        st.balloons()
        st.success("선택하신 날짜의 미션 기록이 안전하게 저장되었습니다!")
        st.rerun()

st.write("")
with st.expander("➕ 새로운 과제 직접 추가하기"):
    with st.form("add_task_form"):
        new_title = st.text_input("추가할 과제 이름")
        new_type = st.selectbox(
            "과제 유형", ["매일 당일 완료", "일주일 목표"]
        )
        submit_btn = st.form_submit_button("과제 등록하기")

        if submit_btn:
            if new_title.strip() == "":
                st.warning("과제 이름을 입력해 주세요.")
            else:
                if selected_date_str not in db_data:
                    db_data[selected_date_str] = []
                new_task_item = {
                    "id": f"{selected_date_str}_{new_title}",
                    "title": new_title,
                    "type": new_type,
                    "status": "미진행",
                    "memo": "",
                    "category": "윤우 추가",
                }
                db_data[selected_date_str].append(new_task_item)
                save_data(db_data)
                st.success(
                    f"'{selected_date_str}' 날짜에 '{new_title}' 미션이 추가되었습니다!"
                )
                st.rerun()