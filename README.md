# detailed_fehsim
Simulator for Nintendo’s top grossing mobile game with customizable pools, rates, and goals.

[Try it with the Streamlit GUI](https://huggingface.co/spaces/timothycho01/detailed_fehsim)

n = 10,000 runs

## Percentile cost to reach target goal of 11

![goal_percentile_cost](https://github.com/timothycho01/detailed_fehsim/assets/104095972/c08c11e7-b437-4c19-9ac7-67e99d8c4a42)

## Progress of every run

![lineages_of_runs](https://github.com/timothycho01/detailed_fehsim/assets/104095972/b35fb060-3975-4bc9-9bce-ba20e075c1fd)

## Session rates movement of every run

![lineages_of_session_rates](https://github.com/timothycho01/detailed_fehsim/assets/104095972/89039473-6539-4d14-9d37-59917e3fb7a0)

## Frequency of session rates

![log_freq_session_rates](https://github.com/timothycho01/detailed_fehsim/assets/104095972/ea05fa32-0b8e-4518-a9b9-38a8e1427668)

## Distributions of total x summoned

![hist_goal_group_1](https://github.com/timothycho01/detailed_fehsim/assets/104095972/dec02339-08e2-4790-afa5-b20c853c2731)
![hist_focus_5](https://github.com/timothycho01/detailed_fehsim/assets/104095972/8095e80e-3ee9-426f-88ac-5041b4ebe198)
![hist_non_focus_5](https://github.com/timothycho01/detailed_fehsim/assets/104095972/561d1b95-5f67-4be9-b6d2-6598fee8b7f0)
![hist_special_4](https://github.com/timothycho01/detailed_fehsim/assets/104095972/2a54d371-3cf1-4980-b63a-9edd2bdadbe1)
![hist_non_focus_4](https://github.com/timothycho01/detailed_fehsim/assets/104095972/91a42677-203d-49bc-aa97-c7390fbd4b5e)
![hist_non_focus_3](https://github.com/timothycho01/detailed_fehsim/assets/104095972/29cc7252-acdb-4403-803c-d8648dab884b)

## GUI Settings Used:

{"gui_settings": {"input_sparks": 0, "select_color_priority": ["Red", "Blue", "Green", "Colorless"], "select_goals_required": false, "input_summon_limit": false, "toggle_summon_limit": false, "toggle_goals_met": false, "toggle_orb_limit": true, "input_simulations": 10000, "select_banner_type": "(3%/3%) Normal", "input_tickets": 0, "flag_update_rates": false}, "simulator_settings": {"Pools": {"red": {"focus_5": 1, "focus_4": 0, "non_focus_5": 26, "special_4": 62, "sh_special_4": 22, "non_focus_4": 41, "non_focus_3": 41}, "blue": {"focus_5": 1, "focus_4": 0, "non_focus_5": 27, "special_4": 42, "sh_special_4": 28, "non_focus_4": 45, "non_focus_3": 45}, "green": {"focus_5": 1, "focus_4": 0, "non_focus_5": 19, "special_4": 36, "sh_special_4": 32, "non_focus_4": 37, "non_focus_3": 37}, "colorless": {"focus_5": 1, "focus_4": 0, "non_focus_5": 19, "special_4": 28, "sh_special_4": 27, "non_focus_4": 45, "non_focus_3": 45}}, "Goals": {"target_rarity": {"0": "Specific 5\u2605 Focus Unit"}, "target_color": {"0": "Red"}, "target_count": {"0": 11}, "goal_group": {"0": 1}}, "Banner Rates": {"rate": {"focus_5": 0.03, "non_focus_5": 0.03, "special_4": 0.03, "non_focus_4": 0.55, "non_focus_3": 0.36}}, "Goals Required": null, "Orb Limit": 3000, "Summon Limit": null, "Banner Type": "(3%/3%) Normal", "Simulations": 10000, "Tickets": 0, "Sparks": 0, "Focus Charges": false, "Color Priority": ["red", "blue", "green", "colorless"]}}
