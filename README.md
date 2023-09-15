# detailed_fehsim
Simulator for Nintendo’s top grossing mobile game with customizable pools, rates, and goals.

[Try it with the Streamlit GUI](https://huggingface.co/spaces/timothycho01/detailed_fehsim)

n = 10,000 runs

## Percentile cost to reach target goal of 11

![goal_percentile_cost](https://github.com/timothycho01/fehsim_stats/assets/104095972/124b5418-cd27-480c-a1b9-785da4fc84e5)

## Progress of every run

![lineages_of_runs](https://github.com/timothycho01/fehsim_stats/assets/104095972/391ece60-7eed-4f90-9a19-4e05ffcfb660)

## Session rates movement of every run

![lineages_of_session_rates](https://github.com/timothycho01/fehsim_stats/assets/104095972/7d77e82d-8508-48de-858a-48b918ea6a14)

## Frequency of session rates

![log_freq_session_rates](https://github.com/timothycho01/fehsim_stats/assets/104095972/008e03a6-46fe-4f8f-a5de-c2a4c398caf0)

## Distributions of total x summoned

![hist_goal_group_1](https://github.com/timothycho01/fehsim_stats/assets/104095972/5db2ae80-7006-4d23-bd2f-4ab8715092be)

![hist_focus_5](https://github.com/timothycho01/fehsim_stats/assets/104095972/8d73492b-5a51-4e53-9d49-a74ecd87c919)

![hist_non_focus_5](https://github.com/timothycho01/fehsim_stats/assets/104095972/5145a66f-24f7-4e13-b76d-0872422cf8ca)

![hist_special_4](https://github.com/timothycho01/fehsim_stats/assets/104095972/b3223edd-b856-4372-8107-23e2b97973e6)

![hist_non_focus_4](https://github.com/timothycho01/fehsim_stats/assets/104095972/33b71af1-a9c9-4173-aadd-66d9a6a23d7d)

![hist_non_focus_3](https://github.com/timothycho01/fehsim_stats/assets/104095972/33b8d230-a544-4a97-bbce-8f488078c98d)

## GUI Settings Used:

{"gui_settings": {"input_sparks": 0, "select_color_priority": ["Red", "Blue", "Green", "Colorless"], "select_goals_required": false, "input_summon_limit": false, "toggle_summon_limit": false, "toggle_goals_met": false, "toggle_orb_limit": true, "input_simulations": 10000, "select_banner_type": "(3%/3%) Normal", "input_tickets": 0, "flag_update_rates": false}, "simulator_settings": {"Pools": {"red": {"focus_5": 1, "focus_4": 0, "non_focus_5": 26, "special_4": 62, "sh_special_4": 22, "non_focus_4": 41, "non_focus_3": 41}, "blue": {"focus_5": 1, "focus_4": 0, "non_focus_5": 27, "special_4": 42, "sh_special_4": 28, "non_focus_4": 45, "non_focus_3": 45}, "green": {"focus_5": 1, "focus_4": 0, "non_focus_5": 19, "special_4": 36, "sh_special_4": 32, "non_focus_4": 37, "non_focus_3": 37}, "colorless": {"focus_5": 1, "focus_4": 0, "non_focus_5": 19, "special_4": 28, "sh_special_4": 27, "non_focus_4": 45, "non_focus_3": 45}}, "Goals": {"target_rarity": {"0": "Specific 5\u2605 Focus Unit"}, "target_color": {"0": "Red"}, "target_count": {"0": 11}, "goal_group": {"0": 1}}, "Banner Rates": {"rate": {"focus_5": 0.03, "non_focus_5": 0.03, "special_4": 0.03, "non_focus_4": 0.55, "non_focus_3": 0.36}}, "Goals Required": null, "Orb Limit": 3000, "Summon Limit": null, "Banner Type": "(3%/3%) Normal", "Simulations": 10000, "Tickets": 0, "Sparks": 0, "Focus Charges": false, "Color Priority": ["red", "blue", "green", "colorless"]}}
