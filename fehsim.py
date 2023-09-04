import pandas as pd
import streamlit as st
from stqdm import stqdm
from tqdm import tqdm


class Simulator:
    def __init__(self, settings: dict, streamlit=False):
        self.streamlit = streamlit
        target_rarity_map = {
            'Any Rarity': [
                'sh_special_4', 'special_4', 'non_focus_3', 'focus_5', 'non_focus_4', 'non_focus_5', 'focus_4'
            ],
            'Any 5★ Unit or 4★ Special Rate Unit': [
                'sh_special_4', 'special_4', 'focus_5', 'non_focus_5'
            ],
            'Any 5★ Unit': [
                'focus_5', 'non_focus_5'
            ],
            'Specific 5★ Focus Unit': [
                'focus_5'
            ],
            'Specific 5★ Non-Focus Unit': [
                'non_focus_5'
            ],
            'Any 4★ Unit or 4★ Special Rate Unit or 4★ SHSR Unit': [
                'sh_special_4', 'special_4', 'non_focus_4', 'focus_4'
            ],
            'Any 4★ Unit': [
                'non_focus_4', 'focus_4'
            ],
            'Specific 4★ Focus Unit': [
                'focus_4'
            ],
            'Specific 4★ Non-Focus Unit': [
                'non_focus_4'
            ],
            'Any 4★ Special Rate Unit or 4★ SHSR Unit': [
                'sh_special_4', 'special_4'
            ],
            'Specific 4★ Special Rate Unit': [
                'special_4'
            ],
            'Specific 4★ SHSR Unit': [
                'sh_special_4'
            ],
        }
        target_color_map = {
            'Any Color': ['red', 'blue', 'green', 'colorless'],
            'Red': ['red'],
            'Blue': ['blue'],
            'Green': ['green'],
            'Colorless': ['colorless'],
        }
        banner_selection_map = {
            "(3%/3%) Normal": ['normal', 'normal_4'],
            "(4%/2%) Weekly Revival": ['weekly_revival'],
            "(4%/2%) Weekly Revival 4★ SHSR": ['weekly_revival_shsr'],
            "(5%/3%) Hero Fest": ['hero_fest'],
            "(4%/2%) Double Special Heroes": ['double_special', 'double_special_4'],
            "(8%/0%) Legendary / Mythic": ['legendary/mythic']
        }
        banner_rates = pd.DataFrame(
            [
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
            ],
            columns=['banner_type', 'rarity_pool', 'rate']
        )
        self.pools = settings.get('Pools')
        self.goals = settings.get('Goals')
        self.banner_rates = settings.get('Banner Rates')

        self.goals_required = settings.get('Goals Required')
        self.orb_limit = settings.get('Orb Limit')
        self.summon_limit = settings.get('Summon Limit')
        self.banner_type = settings.get('Banner Type', '(3%/3%) Normal')
        self.n_simulations = settings.get('Simulations', 1000)
        self.tickets = settings.get('Tickets', 0)
        self.sparks = settings.get('Sparks', 0)
        self.focus_charges_enabled = settings.get('Focus Charges', False)
        self.color_priority = settings.get('Color Priority', ['red', 'blue', 'green', 'colorless'])

        if not any([self.goals_required, self.orb_limit, self.summon_limit]):
            raise ValueError('No End Criteria (Goals Required, Orb Limit, Summon Limit) provided.')

        self.pools = pd.DataFrame(self.pools)
        self.goals = pd.DataFrame(self.goals)

        if self.banner_rates is None:
            if self.pools.loc['focus_4'].sum() > 0:
                mapped_banner_type = banner_selection_map[self.banner_type][-1]
            else:
                mapped_banner_type = banner_selection_map[self.banner_type][0]
            self.banner_rates = banner_rates[banner_rates['banner_type'] == mapped_banner_type]
        else:
            self.banner_rates = pd.DataFrame(self.banner_rates).reset_index()
            self.banner_rates.columns = ['rarity_pool', 'rate']

        bool_rate_5 = self.banner_rates.rarity_pool.str.contains('5')
        bool_rate_non_5 = ~bool_rate_5
        sum_rate_5 = self.banner_rates.loc[bool_rate_5, 'rate'].sum()
        sum_rate_non_5 = self.banner_rates.loc[bool_rate_non_5, 'rate'].sum()

        self.banner_rates['step'] = 0
        pre_calc_rates = [self.banner_rates]

        # feh calculates rate up (rate down for non 5 stars) from base, not from previous step!
        for i in range(1, 24):
            inc_rates_df = self.banner_rates.copy(deep=True)
            inc_rates_df.loc[bool_rate_5, 'rate'] *= 1 + (1 / sum_rate_5) * (0.005 * i)
            inc_rates_df.loc[bool_rate_non_5, 'rate'] *= 1 - (1 / sum_rate_non_5) * (0.005 * i)
            inc_rates_df['rate'] = round(inc_rates_df['rate'], 4)
            inc_rates_df['step'] = i
            pre_calc_rates.append(inc_rates_df)

        # max pity rate
        inc_rates_df = self.banner_rates.copy(deep=True)
        inc_rates_df.loc[bool_rate_5, 'rate'] /= sum_rate_5
        inc_rates_df.loc[bool_rate_non_5, 'rate'] = 0
        inc_rates_df['rate'] = round(inc_rates_df['rate'], 4)
        inc_rates_df['step'] = 24
        pre_calc_rates.append(inc_rates_df)

        self.banner_rates_pro_df = pd.concat(pre_calc_rates)
        self.pity_step = 0
        self.curr_banner_rates_df = self.banner_rates_pro_df[self.banner_rates_pro_df['step'] == self.pity_step]

        pools_to_use = [rp for rp in self.pools.index if rp in self.banner_rates.rarity_pool.values]
        self.pools = pd.DataFrame(self.pools.loc[pools_to_use])
        self.pools.reset_index(inplace=True, names='rarity_pool')
        unpivot_unit_pool = pd.melt(self.pools, id_vars=['rarity_pool'], var_name='color', value_name='size')

        unit_list = []
        for row in unpivot_unit_pool.itertuples():
            for _ in range(row.size):
                unit_list_row = [row.color, row.rarity_pool]
                unit_list.append(unit_list_row)
        units_df = pd.DataFrame(unit_list, columns=['color', 'rarity_pool'])

        # joining color priority col to df
        priority_df = pd.DataFrame(enumerate(self.color_priority, start=1), columns=['color_priority', 'color'])
        units_df = units_df.join(priority_df.set_index('color'), on='color', validate='m:1')

        # Goals Setup
        goals_df = self.goals.copy(deep=True)
        max_goal_group = goals_df.groupby('goal_group')['target_count'].max().reset_index()
        goals_df = goals_df.join(
            max_goal_group.set_index('goal_group'), on='goal_group', rsuffix='_max', validate='m:1'
        )
        goals_df['target_count'] = goals_df['target_count_max']
        goals_df = goals_df.drop('target_count_max', axis=1)
        goals_df['target_color'] = goals_df['target_color']
        goals_df['current_count'] = 0

        # Adding goal_row bool columns to unit_df
        reserved_unit_index = []

        for goal in goals_df.itertuples():
            accepted_pools = target_rarity_map[goal.target_rarity]
            accepted_colors = target_color_map[goal.target_color]
            gr_col_name = 'goal_row_' + str(goal.Index)
            goal_is_specific = 'specific' in goal.target_rarity.lower()

            if goal_is_specific:
                allowed_units = ~units_df.index.isin(reserved_unit_index)
            else:
                allowed_units = True

            units_df[gr_col_name] = units_df['rarity_pool'].isin(accepted_pools) & units_df['color'].isin(
                accepted_colors) & allowed_units

            if units_df[gr_col_name].any() and goal_is_specific:
                first_true_index = units_df.index[units_df[gr_col_name]].min()
                reserved_unit_index.append(first_true_index)
                units_df[gr_col_name] = units_df.index == first_true_index
            else:
                if self.streamlit:
                    st.warning(f'{gr_col_name} does not have any available units to target.')
                    st.warning('Target unit may already be reserved by previous goal.')
                else:
                    print(f'{gr_col_name} does not have any available units to target.')
                    print('Target unit may already be reserved by previous goal.')

        # Adding goal_group bool columns to unit_df
        goal_groups_dict = {}
        for group in set(goals_df['goal_group']):
            goals_in_group = ['goal_row_' + str(x) for x in list(goals_df[goals_df['goal_group'] == group].index)]
            goal_groups_dict['goal_group_' + str(group)] = goals_in_group

        for goal_group in goal_groups_dict:
            cols = goal_groups_dict[goal_group]
            units_df[goal_group] = units_df[cols].apply(lambda row: pd.Series(row).any(), axis=1)

        self.gg_cols = list(goal_groups_dict.keys())
        self.gg_cols.sort()
        slice_cols = [col for col in list(units_df.columns) if 'goal' not in col] + self.gg_cols
        units_df = units_df[slice_cols]

        self.base_summon_goals_df = goals_df.copy(deep=True)
        self.curr_summon_goals_df = self.base_summon_goals_df.copy(deep=True)
        self.banner_units_df = units_df.copy(deep=True)

        self.goal_cols = list(self.base_summon_goals_df.columns[5:])
        self.colors_to_target = list(set(self.curr_summon_goals_df.target_color))

        # small adjustments
        self.spark_thresholds = [_ * 40 for _ in range(1, self.sparks + 1)]
        self.sparks_redeemed = 0
        self.sparked_indexes = []

        self.active_focus_charges = 0
        self.apply_focus_charges = False

        # refs
        self.circle_df = None
        self.session_type = 'normal'
        self.summon_cost = 0
        self.n_stones_in_circle = 5

        # tracking
        self.total_orbs_spent = 0
        self.total_summons = 0
        self.session_count = 0
        self.summons_without_any_5 = 0
        self.halt_pity_increase = False
        self.end_criteria_met = False

        self.summon_log = []
        self.prev_summon_log_len = 0
        self.orbs_spent_log = []
        self.session_count_log = []
        self.session_type_log = []
        self.session_pity_step_log = []
        self.run_num_log = []

        self.simulation_log_df = None

        self.run_simulations()

    def reset_run(self):
        self.total_orbs_spent = 0
        self.total_summons = 0
        self.session_count = 0
        self.summons_without_any_5 = 0
        self.end_criteria_met = False

        self.curr_summon_goals_df = self.base_summon_goals_df.copy(deep=True)
        self.sparks_redeemed = 0
        self.sparked_indexes = []
        self.active_focus_charges = 0
        self.apply_focus_charges = False

    def run_simulations(self):

        if self.streamlit:
            progress_bar = stqdm(range(self.n_simulations))
        else:
            progress_bar = tqdm(range(self.n_simulations))

        for n in progress_bar:
            self.simulate_run()
            self.log_run(n + 1)
            self.reset_run()

        self.simulation_log_df = pd.DataFrame(self.summon_log)
        self.simulation_log_df.rename(columns={'Index': 'unit_id'}, inplace=True)
        self.simulation_log_df['unit_id'] += 1
        self.simulation_log_df['orbs_spent'] = self.orbs_spent_log
        self.simulation_log_df['session_count'] = self.session_count_log
        self.simulation_log_df['session_type'] = self.session_type_log
        self.simulation_log_df['session_pity_step'] = self.session_pity_step_log
        self.simulation_log_df['run_num'] = self.run_num_log

        message = f'{self.n_simulations} Simulations Completed'
        if self.streamlit:
            st.success(message)
        else:
            print(message)

    def simulate_run(self):

        while not self.end_criteria_met:
            self.setup_session()
            self.create_circle()
            self.filter_circle()
            self.summon_from_circle()

    def log_run(self, run_num):
        curr_log_len = len(self.summon_log) - self.prev_summon_log_len
        self.run_num_log = self.run_num_log + [run_num for _ in range(curr_log_len)]
        self.prev_summon_log_len = len(self.summon_log)

    def setup_session(self):
        self.session_type = 'normal'
        self.apply_focus_charges = False

        sparks_remain = self.sparks_redeemed != len(self.spark_thresholds)
        if sparks_remain and self.total_summons >= self.spark_thresholds[self.sparks_redeemed]:
            self.sparks_redeemed += 1
            self.session_type = 'spark'
            return

        if self.focus_charges_enabled and self.active_focus_charges >= 3:
            self.apply_focus_charges = True

        self.pity_step = int(self.summons_without_any_5 / 5)
        self.curr_banner_rates_df = self.banner_rates_pro_df[self.banner_rates_pro_df.step == self.pity_step].copy()

    def create_circle(self):
        circle = []
        if self.session_type == 'spark':
            bool_rarity = self.banner_units_df['rarity_pool'] == 'focus_5'
            spark_circle = self.banner_units_df.loc[bool_rarity]
            spark_circle = spark_circle[
                ~spark_circle.index.isin(self.sparked_indexes)]  # removes previously sparked units
            self.circle_df = spark_circle
            return

        for i in range(self.n_stones_in_circle):
            # draws unit rarities
            drawn_rarity = self.curr_banner_rates_df.sample(weights='rate')['rarity_pool'].iloc[0]
            if self.apply_focus_charges and drawn_rarity == 'non_focus_5':
                drawn_rarity = 'focus_5'
            units_in_rarity = self.banner_units_df[self.banner_units_df['rarity_pool'] == drawn_rarity]
            # draws unit from drawn rarities
            drawn_unit = units_in_rarity.sample()
            circle.append(drawn_unit)

        self.circle_df = pd.concat(circle)

    def filter_circle(self):

        if self.session_type == 'spark':
            circle = self.circle_df[self.circle_df[self.gg_cols].any(axis=1)].head(1)
        elif self.goals_required == 'Any Goal Met' or len(self.colors_to_target) == 1:
            self.colors_to_target = list(self.curr_summon_goals_df['target_color'].str.lower())
            circle = self.circle_df[self.circle_df['color'].isin(self.colors_to_target)].sort_values('color_priority')
        elif self.goals_required == 'All Goals Met':
            unmet_goals = self.curr_summon_goals_df['current_count'] < self.curr_summon_goals_df['target_count']
            self.colors_to_target = list(self.curr_summon_goals_df[unmet_goals]['target_color'].str.lower())
            circle = self.circle_df[self.circle_df['color'].isin(self.colors_to_target)].sort_values('color_priority')
        else:
            circle = self.circle_df

        if len(circle) != 0:
            self.circle_df = circle
        else:  # if nothing returns after filtering, filter for first stone
            self.circle_df = self.circle_df.sort_values('color_priority').head(1)

    def summon_from_circle(self):
        price_index = 0
        self.session_count += 1
        self.halt_pity_increase = False

        if self.session_count <= self.tickets + 1:
            prices = (0, 4, 4, 4, 3)
        else:
            prices = (5, 4, 4, 4, 3)

        for row in self.circle_df.itertuples(index=True):  # keep index as true
            if self.session_type == 'spark':
                self.sparked_indexes.append(row.Index)
                self.summon_cost = 0
            else:
                self.summon_cost = prices[price_index]
                self.eval_end_criteria_limits()
                if self.end_criteria_met:
                    break
                self.total_summons += 1

            self.orbs_spent_log.append(self.summon_cost)
            self.total_orbs_spent += self.summon_cost
            self.summon_log.append(row)
            self.session_count_log.append(self.session_count)
            self.session_type_log.append(self.session_type)
            self.session_pity_step_log.append(self.pity_step)

            self.update_flags(row)
            self.update_goals(row)
            self.eval_end_criteria_goals()

            if self.end_criteria_met:
                break
            price_index += 1

        if self.end_criteria_met:
            return

    def update_flags(self, row):
        if row.rarity_pool == 'focus_5':
            self.halt_pity_increase = True
            self.summons_without_any_5 = 0
            if self.active_focus_charges >= 3:
                self.active_focus_charges = 0
        elif row.rarity_pool == 'non_focus_5':
            self.summons_without_any_5 = max(0, self.summons_without_any_5 - 20)
            self.active_focus_charges += 1
        else:
            if not self.halt_pity_increase:
                self.summons_without_any_5 += 1

    def update_goals(self, row):  # takes named tuple from circle_df, updates summon goals based on goal group columns
        # noinspection PyProtectedMember
        row_dict = row._asdict()
        for gg in self.gg_cols:
            if row_dict[gg]:
                gg_num = gg.split('_')[-1]
                self.curr_summon_goals_df.loc[self.curr_summon_goals_df['goal_group'] == gg_num, 'current_count'] += 1

    def eval_end_criteria_goals(self):
        if self.goals_required is not None:
            met_goals = self.curr_summon_goals_df['current_count'] >= self.curr_summon_goals_df['target_count']
            if self.goals_required == 'Any Goal Group Met' and any(met_goals):
                self.end_criteria_met = True
            elif self.goals_required == 'All Goal Groups Met' and all(met_goals):
                self.end_criteria_met = True

    def eval_end_criteria_limits(self):
        if self.orb_limit != 0:
            if self.total_orbs_spent + self.summon_cost > self.orb_limit:
                self.end_criteria_met = True
        elif self.summon_limit != 0:
            if self.total_summons + 1 > self.summon_limit:
                self.end_criteria_met = True

