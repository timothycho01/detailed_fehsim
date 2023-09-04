import streamlit as st
import pandas as pd
import fehsim
import json
from io import BytesIO

RARITY_OPTIONS = [
    'Any Rarity',
    'Any 5★ Unit or 4★ Special Rate Unit',
    'Any 5★ Unit',
    'Specific 5★ Focus Unit',
    'Specific 5★ Non-Focus Unit',
    'Any 4★ Unit or 4★ Special Rate Unit or 4★ SHSR Unit',
    'Any 4★ Unit',
    'Specific 4★ Focus Unit',
    'Specific 4★ Non-Focus Unit',
    'Any 4★ Special Rate Unit or 4★ SHSR Unit',
    'Specific 4★ Special Rate Unit',
    'Specific 4★ SHSR Unit'
]
COLOR_OPTIONS = [
    'Any Color',
    'Red',
    'Blue',
    'Green',
    'Colorless'
]
BANNER_OPTIONS = [
    '(3%/3%) Normal',
    '(4%/2%) Weekly Revival',
    '(4%/2%) Weekly Revival 4★ SHSR',
    '(5%/3%) Hero Fest',
    '(4%/2%) Double Special Heroes',
    '(8%/0%) Legendary / Mythic'
]
END_CRITERIA_OPTIONS = [
    'Any Goal Group Met',
    'All Goal Groups Met',
]
BANNER_RATES_MAPPING = {
    "(3%/3%) Normal": ['normal', 'normal_4'],
    "(4%/2%) Weekly Revival": ['weekly_revival'],
    "(4%/2%) Weekly Revival 4★ SHSR": ['weekly_revival_shsr'],
    "(5%/3%) Hero Fest": ['hero_fest'],
    "(4%/2%) Double Special Heroes": ['double_special', 'double_special_4'],
    "(8%/0%) Legendary / Mythic": ['legendary/mythic']
}

POOL_ORDER = [
    'focus_5',
    'non_focus_5',
    'focus_4',
    'special_4',
    'sh_special_4',
    'non_focus_4',
    'non_focus_3'
]

BANNER_RATES = [
    ['normal', 'focus_5', 0.03],
    ['normal', 'non_focus_5', 0.03],
    ['normal', 'special_4', 0.03],
    ['normal', 'non_focus_4', 0.55],
    ['normal', 'non_focus_3', 0.36],

    ['normal_4', 'focus_5', 0.03],
    ['normal_4', 'non_focus_5', 0.03],
    ['normal_4', 'focus_4', 0.03],
    ['normal_4', 'special_4', 0.03],
    ['normal_4', 'non_focus_4', 0.52],
    ['normal_4', 'non_focus_3', 0.36],

    ['weekly_revival', 'focus_5', 0.04],
    ['weekly_revival', 'non_focus_5', 0.02],
    ['weekly_revival', 'special_4', 0.03],
    ['weekly_revival', 'non_focus_4', 0.55],
    ['weekly_revival', 'non_focus_3', 0.36],

    ['weekly_revival_shsr', 'focus_5', 0.04],
    ['weekly_revival_shsr', 'non_focus_5', 0.02],
    ['weekly_revival_shsr', 'sh_special_4', 0.03],
    ['weekly_revival_shsr', 'special_4', 0.03],
    ['weekly_revival_shsr', 'non_focus_4', 0.55],
    ['weekly_revival_shsr', 'non_focus_3', 0.33],

    ['hero_fest', 'focus_5', 0.05],
    ['hero_fest', 'non_focus_5', 0.03],
    ['hero_fest', 'special_4', 0.03],
    ['hero_fest', 'non_focus_4', 0.55],
    ['hero_fest', 'non_focus_3', 0.34],

    ['double_special', 'focus_5', 0.06],
    ['double_special', 'special_4', 0.03],
    ['double_special', 'non_focus_4', 0.57],
    ['double_special', 'non_focus_3', 0.34],

    ['double_special_4', 'focus_5', 0.06],
    ['double_special_4', 'focus_4', 0.03],
    ['double_special_4', 'special_4', 0.03],
    ['double_special_4', 'non_focus_4', 0.54],
    ['double_special_4', 'non_focus_3', 0.34],

    ['legendary/mythic', 'focus_5', 0.08],
    ['legendary/mythic', 'special_4', 0.03],
    ['legendary/mythic', 'non_focus_4', 0.55],
    ['legendary/mythic', 'non_focus_3', 0.34],
]
BANNER_RATES_DF = pd.DataFrame(BANNER_RATES, columns=['banner_type', 'rarity_pool', 'rate'])
BANNER_RATES_DF['rate'] *= 100

pool_to_alias = {
    'focus_5': '5★ Focus',
    'focus_4': '4★ Focus',
    'non_focus_5': '5★',
    'special_4': '4★ SR',
    'sh_special_4': '4★ SHSR',
    'non_focus_4': '4★',
    'non_focus_3': '3★',
}
alias_to_pool = {v: k for k, v in pool_to_alias.items()}
BANNER_RATES_DF['rarity_pool'] = BANNER_RATES_DF['rarity_pool'].map(pool_to_alias)


def core_settings(settings):
    st.subheader('Simulation Settings', anchor=False)

    st.write('End Criteria:')
    tt = 'End a run when goal conditions are met.'
    if st.toggle('Goals Met', help=tt, key='toggle_goals_met'):
        goals_required = st.selectbox(
            'GR',
            options=END_CRITERIA_OPTIONS,
            label_visibility='collapsed',
            key='select_goals_required'
        )
    else:
        goals_required = None

    tt = 'End a run when Orb Limit is reached or not enough orbs to summon.'
    if st.toggle('Orb Limit', help=tt, value=True, key='toggle_orb_limit'):
        orb_limit = st.number_input(
            'OL',
            value=3000,
            step=1,
            min_value=0,
            label_visibility='collapsed',
            key='input_orb_limit'
        )
    else:
        orb_limit = None

    tt = 'End a run when Summon Limit is reached.'
    if st.toggle('Summon Limit', help=tt, key='toggle_summon_limit'):
        summon_limit = st.number_input(
            'SL',
            value=15_000,
            step=1,
            min_value=0,
            label_visibility='collapsed',
            key='input_summon_limit'
        )
    else:
        summon_limit = None

    if not any([goals_required, orb_limit, summon_limit]):
        st.warning('Please select at least one End Criteria.')

    col1, col2 = st.columns([3, 2])

    with col2:
        st.write("")
        st.write("")
        focus_charges = st.checkbox('Enable Focus Charges?', key='toggle_focus_charges')
    with col1:
        tt = 'Highest Priority -> Lowest Priority'
        color_priority = st.multiselect(
            'Color Priority',
            COLOR_OPTIONS[1:],
            default=COLOR_OPTIONS[1:],
            help=tt,
            key='select_color_priority'
        )
    if len(color_priority) != 4:
        st.warning('Please sort all the colors.')

    col1, col2 = st.columns(2)

    with col1:
        tt = 'Select the banner rates to simulate. Will also determine which pools are used.'
        banner_type = st.selectbox(
            'Banner Type:',
            options=BANNER_OPTIONS,
            help=tt,
            key='select_banner_type',
        )
        tt = 'Number of simulations to run.'
        simulations = st.number_input(
            'Simulations',
            value=100,
            step=1,
            min_value=0,
            help=tt,
            key='input_simulations'
        )
        tt = 'Number of summoning sessions (i.e. circles) where the first summon is free.'

    with col2:
        tickets = st.number_input(
            'Tickets',
            value=0,
            step=1,
            min_value=0,
            help=tt,
            key='input_tickets'
        )
        tt = 'Guaranteed 5★ Focus Unit (i.e. spark) session after 40 summons.'
        sparks = st.number_input(
            'Sparks',
            value=0,
            step=1,
            min_value=0,
            help=tt,
            key='input_sparks'
        )

    summon_pools = settings['Pools']
    focus_5_pool_size = summon_pools.loc['focus_5'][1:].sum()
    if sparks > focus_5_pool_size:
        st.warning(f'Sparks exceeding the number of 5★ Focus Units.')

    updated_core_settings = {
        # End Criteria
        'Goals Required': goals_required,
        'Orb Limit': orb_limit,
        'Summon Limit': summon_limit,
        # Main Settings
        'Banner Type': banner_type,
        'Simulations': simulations,
        'Tickets': tickets,
        'Sparks': sparks,
        'Focus Charges': focus_charges,
        'Color Priority': color_priority,
    }

    return updated_core_settings


def goal_settings(settings):
    st.subheader('Summoning Goals', anchor=False, help='Edit the table below to set your summoning goals')
    st.caption(f"{bo('Goals')} of the same {bo('Goal Group')} will contribute to a {bo('Shared Target Count')}.")
    st.caption(f"{bo('Shared Target Count')} will be the max {bo('Target Count')} within the {bo('Goal Group')}.")
    column_config = {
        "target_rarity": st.column_config.SelectboxColumn(
            "Rarity", options=RARITY_OPTIONS, required=True, width='large'
        ),
        "target_color": st.column_config.SelectboxColumn(
            "Color", options=COLOR_OPTIONS, required=True, width='small'
        ),
        "target_count": st.column_config.NumberColumn(
            "Target Count", min_value=1, step=1, required=True, width='small'
        ),
        "goal_group": st.column_config.NumberColumn(
            "Goal Group", min_value=1, step=1, required=True, width='small'
        ),
    }
    df = settings['Goals']
    return st.data_editor(
        df,
        num_rows='dynamic',
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        key='data_editor_goals'
    ), df


def pool_settings(settings):
    st.subheader('Summoning Pool', anchor=False, help='Edit the table below to set your summoning pools')
    column_config = {
        "red": st.column_config.NumberColumn("Red", min_value=0, step=1, required=True),
        "blue": st.column_config.NumberColumn("Blue", min_value=0, step=1, required=True),
        "green": st.column_config.NumberColumn("Green", min_value=0, step=1, required=True),
        "colorless": st.column_config.NumberColumn("Colorless", min_value=0, step=1, required=True),
        "rarity_pool": st.column_config.TextColumn("Rarity Pool", disabled=True),
    }
    df = settings['Pools']
    return st.data_editor(
        df,
        column_config=column_config,
        hide_index=True,
        key='data_editor_pools'
    ), df


def rate_settings(settings):
    st.subheader('Summoning Rates', anchor=False, help='Edit the table below to set your summoning rates')
    st.caption(f"Changes to {bo('4★ Focus pool')} or {bo('Banner Type')} will reset this table.")
    column_config = {
        "rarity_pool": st.column_config.SelectboxColumn(
            "Rarity Pool", disabled=True
        ),
        "rate": st.column_config.NumberColumn(
            "Rate (%)", min_value=0, step=0.01, max_value=100, required=True, format="%.2f"
        ),
    }
    summon_pools = settings['Pools']
    focus_4_pool_size = summon_pools.loc['focus_4'][1:].sum()
    if focus_4_pool_size > 0:
        mapped_banner_type = BANNER_RATES_MAPPING[settings['Banner Type']][-1]
        if len(BANNER_RATES_MAPPING[settings['Banner Type']]) == 1:
            st.warning(f'4★ Focus Units do not appear in this Banner Type.')
    else:
        mapped_banner_type = BANNER_RATES_MAPPING[settings['Banner Type']][0]

    if mapped_banner_type not in settings['Banner Rates']['banner_type'].values:
        df = BANNER_RATES_DF[BANNER_RATES_DF.banner_type == mapped_banner_type]
    else:
        df = settings['Banner Rates']

    return st.data_editor(
        df,
        column_config=column_config,
        hide_index=True,
        column_order=['rarity_pool', 'rate'],
        key='data_editor_rates'
    ), df


def goal_setting_example():
    with st.expander("Goal Group Examples"):
        st.caption("You want (11) copies of a Red unit present in both the 5★ Focus pool and 4★ Non-Focus pool.")
        st.caption("Goal Group 1 will be met once a shared total of (11) units are summoned.")
        ex_data = [
            ['Specific 5★ Focus Unit', 'Red', 11, 1],
            ['Specific 4★ Non-Focus Unit', 'Red', 11, 1]
        ]
        ex_df = pd.DataFrame(ex_data, columns=['Rarity', 'Color', 'Target Count', 'Goal Group'])
        st.dataframe(ex_df, hide_index=True)
        st.divider()
        st.caption("You want (8) units with a specific skill.")
        st.caption("(2) Blue units with this skill are present in the 5★ Non-Focus pool.")
        st.caption("(1) Green unit with this skill is present in the 4★ Non-Focus pool.")
        st.caption("Goal Group 2 will be met once a shared total of (8) units are summoned.")
        ex_data = [
            ['Specific 5★ Non-Focus  Unit', 'Blue', 8, 2],
            ['Specific 5★ Non-Focus  Unit', 'Blue', 8, 2],
            ['Specific 4★ Non-Focus Unit', 'Green', 8, 2],
        ]
        ex_df = pd.DataFrame(ex_data, columns=['Rarity', 'Color', 'Target Count', 'Goal Group'])
        st.dataframe(ex_df, hide_index=True)


def bo(text):  # streamlit bold orange markdown
    return f":orange[__{text}__]"


def user_to_sys(settings):
    sys_settings = {}

    for k, v in settings.items():
        if isinstance(v, pd.DataFrame):
            val = v.copy(deep=True)
        else:
            val = v
        sys_settings[k] = val

    sys_goals = sys_settings['Goals']
    sys_settings['Goals'] = sys_goals.to_dict()

    sys_pools = sys_settings['Pools']
    sys_pools = sys_pools.drop('rarity_pool', axis=1)
    sys_settings['Pools'] = sys_pools.to_dict()

    sys_rates = sys_settings['Banner Rates']
    sys_rates = sys_rates.drop('banner_type', axis=1)
    sys_rates['rarity_pool'] = sys_rates['rarity_pool'].map(alias_to_pool)
    sys_rates['rate'] = round(sys_rates['rate'] / 100, 4)
    sys_rates.index = sys_rates['rarity_pool']
    sys_rates = sys_rates.drop('rarity_pool', axis=1)
    sys_settings['Banner Rates'] = sys_rates.to_dict()

    sys_settings['Color Priority'] = [c.lower() for c in sys_settings['Color Priority']]

    return sys_settings


def sys_to_user(settings):
    user_settings = {}

    for k, v in settings.items():
        if isinstance(v, dict):
            val = pd.DataFrame(v)
        else:
            val = v
        user_settings[k] = val

    user_pools = user_settings['Pools']
    user_pools['rarity_pool'] = user_pools.index
    user_pools['rarity_pool'] = user_pools['rarity_pool'].map(pool_to_alias)
    col_order = ['rarity_pool', 'red', 'blue', 'green', 'colorless']
    user_settings['Pools'] = user_pools[col_order]

    user_rates = user_settings['Banner Rates']
    user_rates = user_rates.reset_index(names='rarity_pool')
    must_only_have = user_rates.rarity_pool.values
    df = BANNER_RATES_DF.copy(deep=True)
    df['rarity_pool'] = df['rarity_pool'].map(alias_to_pool)
    grouped_df = df.groupby('banner_type')['rarity_pool']
    filtered_banner_types = grouped_df.apply(lambda x: set(must_only_have) == set(x)).reset_index()
    filtered_banner_types = filtered_banner_types[filtered_banner_types['rarity_pool']]
    compatible_banners = df[df['banner_type'].isin(filtered_banner_types['banner_type'])]
    user_rates['banner_type'] = compatible_banners.banner_type.values[0]
    user_rates['rate'] = user_rates['rate'] * 100
    col_order = ['banner_type', 'rarity_pool', 'rate']
    sorting_order = {v: i for i, v in enumerate(POOL_ORDER)}
    user_rates['order'] = user_rates['rarity_pool'].map(sorting_order)
    user_rates = user_rates.sort_values(by='order').drop(columns='order').reset_index(drop=True)
    user_rates['rarity_pool'] = user_rates['rarity_pool'].map(pool_to_alias)

    user_settings['Banner Rates'] = user_rates[col_order]
    user_settings['Color Priority'] = [c.capitalize() for c in user_settings['Color Priority']]

    return user_settings


def debug_compare(setting_1, setting_2):
    comparison = {}
    for k, v in setting_1.items():
        if isinstance(v, pd.DataFrame):
            compare = v.equals(setting_2[k])
        else:
            compare = v == setting_2[k]
        comparison[k] = compare
    return comparison


def settings_app():
    st.set_page_config(layout="centered")
    css = '''
    <style>
        section.main > div {max-width:55rem}
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)
    st.subheader("FEH Detailed Summoning Simulator", anchor=False)

    # initialize session state
    if 'user_settings' not in st.session_state:
        default_goals = [['Specific 5★ Focus Unit', 'Red', 11, 1]]
        default_pools = {
            'focus_5': ['5★ Focus', 1, 1, 1, 1],
            'focus_4': ['4★ Focus', 0, 0, 0, 0],
            'non_focus_5': ['5★', 26, 27, 19, 19],
            'special_4': ['4★ SR', 62, 42, 36, 28],
            'sh_special_4': ['4★ SHSR', 22, 28, 32, 27],
            'non_focus_4': ['4★', 41, 45, 37, 45],
            'non_focus_3': ['3★', 41, 45, 37, 45],
        }
        pool_cols = ['rarity_pool', 'red', 'blue', 'green', 'colorless']
        goal_cols = ['target_rarity', 'target_color', 'target_count', 'goal_group']
        mapped_banner_type = BANNER_RATES_MAPPING[BANNER_OPTIONS[0]][0]
        default_settings = {
            # Dataframes
            'Pools': pd.DataFrame.from_dict(default_pools, orient='index', columns=pool_cols),
            'Goals': pd.DataFrame(default_goals, columns=goal_cols),
            'Banner Rates': BANNER_RATES_DF[BANNER_RATES_DF.banner_type == mapped_banner_type].copy(deep=True),
            # End Criteria
            'Goals Required': 'All Goal Groups Met',
            'Orb Limit': 3000,
            'Summon Limit': None,
            # Main Settings
            'Banner Type': BANNER_OPTIONS[0],
            'Simulations': 100,
            'Tickets': 0,
            'Sparks': 0,
            'Focus Charges': False,
            'Color Priority': ['Red', 'Blue', 'Green', 'Colorless'],
        }
        st.session_state.user_settings = default_settings

    # upload settings from json
    uploaded_file = st.file_uploader("Upload gui_simulator_settings.json file", type=['json'])
    if uploaded_file is not None:
        if st.button("Submit", use_container_width=True):
            data = json.load(uploaded_file)
            if 'gui_settings' not in data or 'simulator_settings' not in data:
                st.error("Invalid gui_simulator_settings.json file")
            else:
                st.session_state.user_settings = sys_to_user(data['simulator_settings'])
                for k, v in data['gui_settings'].items():
                    st.session_state[k] = v

    st.divider()

    current_settings = st.session_state.user_settings
    prev_banner_type = current_settings['Banner Type']

    updated_data = core_settings(current_settings)
    for k, v in updated_data.items():
        st.session_state.user_settings[k] = v

    if prev_banner_type != current_settings['Banner Type']:
        st.session_state.flag_update_rates = True
    else:
        st.session_state.flag_update_rates = False

    current_settings = st.session_state.user_settings
    new_goals, prev_goals = goal_settings(current_settings)

    goal_setting_example()

    if st.button("Update Summoning Goals", use_container_width=True):
        st.session_state.user_settings['Goals'] = new_goals
        st.experimental_rerun()

    if not prev_goals.equals(new_goals):
        st.warning("Unsaved changes")

    sub_col1, sub_col2 = st.columns([1, 1])

    with sub_col1:
        current_settings = st.session_state.user_settings
        new_pools, prev_pools = pool_settings(current_settings)

        if st.button("Update Summoning Pools", use_container_width=True):
            st.session_state.user_settings['Pools'] = new_pools
            st.experimental_rerun()

        if not prev_pools.equals(new_pools):
            st.warning("Unsaved changes")

    with sub_col2:
        current_settings = st.session_state.user_settings
        new_rates, prev_rates = rate_settings(current_settings)

        if st.button("Update Summoning Rates", use_container_width=True) or st.session_state.flag_update_rates:
            st.session_state.user_settings['Banner Rates'] = new_rates
            st.session_state.flag_update_rates = False
            st.experimental_rerun()

        if not prev_rates.equals(new_rates):
            st.warning("Unsaved changes")

        sum_rates = sum(new_rates['rate'])
        if sum_rates != 100:
            st.warning(f"Rates should sum to 100% | Currently: {sum_rates:.2f}%")

    st.divider()
    widget_keys = [
        'input_sparks',
        'select_color_priority',
        'select_goals_required',
        'input_summon_limit',
        'toggle_summon_limit',
        'toggle_goals_met',
        'toggle_orb_limit',
        'input_simulations',
        'select_banner_type',
        'input_tickets',
        'flag_update_rates'
    ]
    gui_settings = {k: st.session_state.get(k, False) for k in widget_keys}
    st.session_state.sys_settings = user_to_sys(st.session_state.user_settings)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.download_button(
            label=":blue[Download GUI + Simulator Settings]",
            data=json.dumps({'gui_settings': gui_settings, 'simulator_settings': st.session_state.sys_settings}),
            file_name="gui_simulator_settings.json",
            use_container_width=True,
            help='Settings compatible with the GUI and the simulator.'
        )

    with col2:
        st.download_button(
            label=":blue[Download Simulator Settings]",
            data=json.dumps(st.session_state.sys_settings),
            file_name="simulator_settings.json",
            use_container_width=True,
            help='Settings compatible with the simulator.'
        )

    if st.button(':orange[Run Simulation]', use_container_width=True):
        results = fehsim.Simulator(st.session_state.sys_settings, streamlit=True).simulation_log_df
        st.session_state.simulation_log_df = results
        buffer = BytesIO()
        results.to_parquet(buffer, index=False)
        st.download_button(
            label=":orange[Download Simulation Data]",
            data=buffer,
            file_name='data.parquet',
            use_container_width=True
        )


if __name__ == "__main__":
    settings_app()

