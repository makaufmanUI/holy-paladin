"""
app.py
~~~~~~


"""
from source import (
    rprint,
    get_spell_cast_events,
    get_mana_change_events,
    get_healing_trance_events)
import json
import requests
import numpy as np
import streamlit as st
from modules.report import Report

def main(player, fight):
    soul_preserver_events = get_healing_trance_events(fight, player)
    num_procs = len([i for i,e in enumerate(soul_preserver_events) if e['type'] == 'applybuff'])
    num_wasted_procs = len([i for i,e in enumerate(soul_preserver_events) if e['type'] == 'refreshbuff'])

    spell_cast_events = get_spell_cast_events(fight, player)
    heal_events = [e for e in spell_cast_events if e['ability']['name'] in ['Holy Shock', 'Holy Light', 'Flash of Light']]

    soul_preserver_applied_events = [e for e in soul_preserver_events if e['type'] == 'applybuff']
    soul_preserver_removed_events = [e for e in soul_preserver_events if e['type'] == 'removebuff']

    casts_that_removed_soul_preserver_buff = []
    for i in range(len(soul_preserver_removed_events)):
        apply_event = soul_preserver_applied_events[i]
        remove_event = soul_preserver_removed_events[i]
        for i,heal_event in enumerate(heal_events):
            if apply_event['timestamp'] <= heal_event['timestamp'] <= remove_event['timestamp']:
                casts_that_removed_soul_preserver_buff.append(heal_event)
                heal_events = heal_events[i+1:]
                break

    spell_costs = {}
    spell_costs["Holy Shock"] = 790
    spell_costs["Holy Light"] = 1161
    spell_costs["Flash of Light"] = 307

    mana_saved = 0
    for spell in casts_that_removed_soul_preserver_buff:
        if spell['ability']['name'] in spell_costs:
            mana_saved += spell_costs[spell['ability']['name']]

    fight_length = fight.duration.seconds
    mana_per5_equivalent = (mana_saved / fight_length) * 5
    num_procs += num_wasted_procs
    return num_procs, num_wasted_procs, mana_saved, mana_per5_equivalent, spell_cast_events, soul_preserver_events, casts_that_removed_soul_preserver_buff


def get_talents(report, fight, player_name):
    url = f"https://classic.warcraftlogs.com/reports/summary/{report._code}/{fight.id}/0/99999999999/{report.get_player_by_name(player_name).report_id}/0/Any/0/-1.0.-1.-1/0"
    headers = {
        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google\"",
        "Accept": "*/*",
        "Referer": "https://classic.warcraftlogs.com/reports/nQxzWVwZfaKyJ9AH",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "\"Windows\""
    }
    response = requests.request("GET", url, headers=headers)
    text = response.text
    text = text.split('Talents: <span class="estimate">')[1].split('</span>')[0]
    text = text.strip().replace(' ','').strip('\n').replace('\n','')
    talents = text.split('/')
    talents = [int(t.strip().rstrip().replace(' ','')) for t in talents]
    return talents

def to_MMSS(seconds):
    return f"{int(seconds//60):01}:{int(seconds%60):02}"


def hide_footer():
    st.markdown(body=\
        """ <style>
        footer {visibility:hidden}
        </style> """, unsafe_allow_html=True
    )

def remove_all_href_links():
    """ Removes all the link things that appear next to markdown headers
        by adding "__web-inspector-hide-shortcut__" to the class attribute. """
    st.markdown(body=\
        """ <style>
        a {visibility:hidden}
        </style> """, unsafe_allow_html=True
    )

st.set_page_config(
    layout     = "centered",
    page_icon  = "🧙‍♂️",
    page_title = "Soul Preserver Info",
)
st.markdown(body=\
    """ <style>
    section.main > div {max-width:65rem}
    </style> """, unsafe_allow_html=True
)

if "report" not in st.session_state:
    st.session_state["report"] = None
if "report_code" not in st.session_state:
    st.session_state["report_code"] = ""
if "last_report_code" not in st.session_state:
    st.session_state["last_report_code"] = ""


hide_footer()
st.title("Soul Preserver / Healing Trance Info")
st.markdown("---")

resest_button = st.button(label=":red[Reset]")

if resest_button:
    st.session_state["report"] = None
    st.session_state["report_code"] = ""
    st.session_state["last_report_code"] = ""

with st.container():
    st.markdown("#### Search by Warcraft Logs link 𝑜𝑟 report code")
    report_code_input_column, search_button_column = st.columns([2,1])
    
    with report_code_input_column:
        report_code = st.text_input(label=" ", value="", label_visibility="collapsed", placeholder="https://classic.warcraftlogs.com/reports/...").strip().replace(' ','')
    with search_button_column:
        search_button = st.button(label=":blue[Search]", use_container_width=True)
        
    if search_button:
        if report_code != "":
            if '/' in report_code:
                report_code = report_code.split('/')[-1]
            st.session_state["report_code"] = report_code
        else:
            st.session_state["report_code"] = ""


st.markdown("---")
# st.markdown("## ")
remove_all_href_links()

if st.session_state["report_code"] != "":
    if st.session_state["report_code"] != st.session_state["last_report_code"]:
        st.session_state["report"] = None
        st.session_state["last_report_code"] = st.session_state["report_code"]
    
    if st.session_state["report"] is None:
        with st.spinner(text=" Loading report..."):
            st.session_state["report"] = Report(st.session_state["report_code"])

    with st.container():
        fights = list(set([f.boss_name for f in st.session_state["report"].fights if f.kill]))
        fights = sorted(fights, key=lambda name: st.session_state["report"].get_fight_by_boss_name(name).duration)
        players = [p.name for p in st.session_state["report"].players if p.class_ == "Paladin"]

        fights_ = [st.session_state["report"].get_fight_by_boss_name(f) for f in fights]

        players2 = {}
        for p in players:
            for f in fights_:
                talents = get_talents(st.session_state["report"], f, p)
                if max(talents) == talents[0]:  # most points in holy
                    if p not in players2:
                        players2[p] = []
                    players2[p].append(f.boss_name + ' (' + to_MMSS(f.duration.seconds) + ')')

        fight_name_select_column, player_name_select_column, submit_button_column = st.columns([1,1,1])

        with fight_name_select_column:
            st.markdown("#### Fight")
            fight_name_options = [f.boss_name + ' (' + to_MMSS(f.duration.seconds) + ')' for f in fights_]
            fight_name = st.selectbox(label=" ", options=fight_name_options, index=0, label_visibility="collapsed")
            fight_name = fight_name.split(' (')[0]  # type: ignore
        
        with player_name_select_column:
            st.markdown("#### Player")
            player_name_options = []
            for name, bosses in players2.items():
                for boss in bosses:
                    if fight_name in boss:
                        player_name_options.append(name)
            player_name = st.selectbox(label=" ", options=player_name_options, index=0, label_visibility="collapsed")
            # player_name = st.selectbox(label=" ", options=players, index=0, label_visibility="collapsed")

        


        with submit_button_column:
            st.markdown("#### ")
            st.markdown("#### ")
            submit_button = st.button(label=":green[Submit]", use_container_width=True)

        st.markdown("---")

        if submit_button:
            player = st.session_state["report"].get_player_by_name(player_name)
            fight = st.session_state["report"].get_fight_by_boss_name(fight_name)
            
            with st.spinner(text=" Getting events..."):
                num_procs, num_wasted_procs, mana_saved, mana_per5_equivalent, spell_cast_events, soul_preserver_events, casts_that_removed_soul_preserver_buff = main(player, fight)

            st.markdown("#### ")
            
            # st.markdown(f"### :blue[Number of procs] ⎯ **{num_procs:,.0f}**")
            # st.markdown(f"### :blue[Number of procs wasted] ⎯ **{num_wasted_procs:,.0f}**")
            # st.markdown("#### ")
            # st.markdown(f"### :violet[Number of casts] ⎯ **{len(spell_cast_events):,.0f}**")
            # st.markdown(f"### :violet[Percent that triggered proc] ⎯ **{num_procs/len(spell_cast_events)*100:.2f}%**")
            # st.markdown("#### ")
            # c1,c2 = st.columns([1,1])
            # with c1:
            #     st.markdown(f"### :orange[Approx. mana saved] ⎯ **{mana_saved:,.0f}**")
            # with c2:
            #     st.markdown(f"### :orange[Equivalent to] **{mana_per5_equivalent:,.0f}** :orange[MP5]")
            

            c1,c2 = st.columns([1,1])
            with c1:
                if num_procs == 1:
                    st.markdown(f"### **{num_procs:,.0f}** :blue[Healing Trance proc]")
                else:
                    st.markdown(f"### **{num_procs:,.0f}** :blue[Healing Trance procs]")
            with c2:
                if num_wasted_procs == 1:
                    st.markdown(f"### **{num_wasted_procs:,.0f}** :blue[of which was wasted]")
                else:
                    st.markdown(f"### **{num_wasted_procs:,.0f}** :blue[of which were wasted]")
            
            # st.markdown("#### ")

            c3,c4 = st.columns([1,1])
            with c3:
                st.markdown(f"### **{len(spell_cast_events):,.0f}** :violet[total spells cast]")
            with c4:
                st.markdown(f"### **{num_procs/len(spell_cast_events)*100:.2f}%** :violet[of which triggered Healing Trance]")

            # st.markdown("#### ")
            
            c5,c6 = st.columns([1,1])
            with c5:
                st.markdown(f"### **{mana_saved:,.0f}** :orange[total mana saved]")
            with c6:
                st.markdown(f"### :orange[Equivalent to] **{mana_per5_equivalent:,.0f}** :orange[mana per five]")


            # st.markdown("#### ")
            # display the casts_that_removed_soul_preserver_buff table after removing the "time" key
            # casts_that_removed_soul_preserver_buff_ = []
            # for d in casts_that_removed_soul_preserver_buff:
            #     d_ = d.copy()
            #     del d_["time"]
            #     del d_["timestamp_relative"]
            #     casts_that_removed_soul_preserver_buff_.append(d_)

            # import pandas as pd
            # st.table(pd.DataFrame(casts_that_removed_soul_preserver_buff_).set_index("timestamp").sort_index(ascending=False))

            # st.write(get_talents(st.session_state["report"], fight, player_name))

            remove_all_href_links()
        


        












# if __name__ == "__main__":
#     pass
