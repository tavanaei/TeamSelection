import streamlit as st
import pandas as pd
import copy
import random
import os

df = pd.read_csv('Soccer Sunday.csv')
players = list(df['Player'])

def push_to_git():
    os.system('git add .')
    os.system('git commit -m "System push for player"')
    os.system('git push -u origin main')

class Team:
    def __init__(self, player_dict):
        player_list = list(player_dict.keys())
        self.table = df
        self.table = self.table[self.table['Player'].isin(player_list)].reset_index(drop=True)
        #print(len(self.table))
        if len(self.table) < 14:
            dummy = [["Ghoast",4,4,4,2,1] for i in range(14-len(self.table))]
            self.table = pd.concat([self.table, pd.DataFrame(dummy, columns=self.table.columns)], ignore_index=True)
        self.table = self.table.sample(frac=1).reset_index(drop=True)
        self.TeamA = []
        self.TeamB = []
        for i in range(len(self.table)):
            name = self.table.iloc[i]["Player"]
            for c in ["Goalie","Defense","Middle","Forward"]:
                self.table[c].iloc[i] = self.table[c].iloc[i]*player_dict[name]
    def select_goalie(self,A,B):
        self.table.sort_values(by=['Goalie'], inplace=True, ascending=False)
        A.append(self.table.iloc[0]['Player'])
        self.table.drop(self.table.index[0], inplace=True)
        B.append(self.table.iloc[0]['Player'])
        self.table.drop(self.table.index[0], inplace=True)
    def select_defender(self,A,B):
        self.table.sort_values(by=['Defense'], inplace=True, ascending=False)
        A.append(self.table.iloc[0]['Player'])
        self.table.drop(self.table.index[0], inplace=True)
        B.append(self.table.iloc[0]['Player'])
        self.table.drop(self.table.index[0], inplace=True)
    def select_midfielder(self,A,B):
        self.table.sort_values(by=['Middle'], inplace=True, ascending=False)
        A.append(self.table.iloc[0]['Player'])
        self.table.drop(self.table.index[0], inplace=True)
        B.append(self.table.iloc[0]['Player'])
        self.table.drop(self.table.index[0], inplace=True)
    def select_forward(self,A,B):
        self.table.sort_values(by=['Forward'], inplace=True, ascending=False)
        A.append(self.table.iloc[0]['Player'])
        v_a = self.table.iloc[0]['Forward']
        self.table.drop(self.table.index[0], inplace=True)
        B.append(self.table.iloc[0]['Player'])
        v_b = self.table.iloc[0]['Forward']
        self.table.drop(self.table.index[0], inplace=True)
        return v_a,v_b
    def select_rest(self,A,B):
        self.table['overall'] = self.table[['Goalie','Defense','Middle','Forward']].mean(axis=1)
        self.table.sort_values(by=['overall'], inplace=True, ascending=False)
        A.append(self.table.iloc[0]['Player'])
        self.table.drop(self.table.index[0], inplace=True)
        if len(self.table)>0:
            B.append(self.table.iloc[0]['Player'])
            self.table.drop(self.table.index[0], inplace=True)
    def make_teams(self):
        self.select_goalie(self.TeamA,self.TeamB)
        f_b,f_a = self.select_forward(self.TeamB,self.TeamA)
        self.select_midfielder(self.TeamA,self.TeamB)
        if f_b-f_a>1:
            self.select_defender(self.TeamA,self.TeamB)
        else:
            self.select_defender(self.TeamB,self.TeamA)
        x1,x2 = self.select_forward(self.TeamA,self.TeamB)
        self.select_midfielder(self.TeamB,self.TeamA)
        self.select_defender(self.TeamA,self.TeamB)
        while len(self.table)>0:
            self.select_rest(self.TeamB,self.TeamA)

def select_teams(player_list):
    myteam = Team(player_list)
    myteam.make_teams()
    if len(myteam.TeamA) < len(myteam.TeamB):
        myteam.TeamA.append(" ")
    elif len(myteam.TeamB) < len(myteam.TeamA):
        myteam.TeamB.append(" ")
    cols = ["White-Jersey Team","Black-Jersey Team"]
    random.shuffle(cols)
    return "Captains: "+myteam.TeamA[2]+ "  --  "+ myteam.TeamB[2],pd.DataFrame({cols[0]: myteam.TeamA, cols[1]: myteam.TeamB})

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        width: 300px !important;  # Set the desired width here
        margin-right: 50px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

selection_tab,player_tab = st.tabs(["Team Selection","Player Update"])
with selection_tab:
    st.title("Sunday Soccer Team Selection")
    teams = None
    with st.sidebar:
        st.header("Players")
        for player in players:
            col1,col2 = st.columns([15,6])
            with col1:
                checkbox_key = f"checkbox_{player}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = False
                checked = st.checkbox(player,key=checkbox_key)
            with col2:
                if checked:
                    slider_key = f"slider_{player}"
                    st.radio("Strength",[10,8,5],
                            horizontal=True,key=slider_key)

        #selected_options = st.multiselect(
        #    "Select attending players:",
        #    players
        #)
        selected_options = {
            key.replace("slider_",""): float(value)/10.0 for key,value in st.session_state.items() if key.startswith("slider_")
        }
        if st.button("Run"):
            caps,teams = select_teams(selected_options)

    if teams is not None:
        st.write("### Players: {}".format(len(selected_options)))
        st.write("*{}*".format(caps))
        st.write("-----")
        st.table(teams)

with player_tab:
    st.write("### Update Player")
    selected_player = st.selectbox("Select the player?",players,index=None)
    if selected_player:
        row = df[df['Player']==selected_player]
        ind = row.index
        goal = st.radio("Goalie",[-2,-1,0,1,2],index=2,horizontal=True,key="rb_g")
        back = st.radio("Defense",[-2,-1,0,1,2],index=2,horizontal=True,key="rb_b")
        mid = st.radio("Middle",[-2,-1,0,1,2],index=2,horizontal=True,key="rb_m")
        forw = st.radio("Forward",[-2,-1,0,1,2],index=2,horizontal=True,key="rb_f")
        
        if st.button("Update"):
            df['Goalie'].loc[ind] = df['Goalie'].loc[ind]+goal
            df['Defense'].loc[ind] = df['Defense'].loc[ind]+back
            df['Middle'].loc[ind] = df['Middle'].loc[ind]+mid
            df['Forward'].loc[ind] = df['Forward'].loc[ind]+forw
            df.to_csv('Soccer Sunday.csv',index=False)

            st.write('The player "{}"" is updated'.format(row.Player.item()))

            push_to_git()

    st.write("-----")

    st.write("### Add New Player")
    selected_new = st.selectbox("Select a player with similar seed?",players,index=None)
    if selected_new:
        row = df[df['Player']==selected_new]
        st.write("**How different is the new player?**")
        new_name = st.text_input("Name")
        goal2 = st.radio("Goalie",[-2,-1,0,1,2],index=2,horizontal=True)
        back2 = st.radio("Defense",[-2,-1,0,1,2],index=2,horizontal=True)
        mid2 = st.radio("Middle",[-2,-1,0,1,2],index=2,horizontal=True)
        forw2 = st.radio("Forward",[-2,-1,0,1,2],index=2,horizontal=True)
        
        if st.button("Add Player"):
            new_player = [new_name,row.Defense.item()+back2,row.Middle.item()+mid2,row.Forward.item()+forw2,row.Goalie.item()+goal2,0]
            df = pd.concat([df,pd.DataFrame([new_player],columns=["Player","Defense","Middle","Forward","Goalie","Present"])])
            df.to_csv('Soccer Sunday.csv',index=False)
            st.write('The player "{}"" is Added'.format(new_name))

            push_to_git()
            print('Push to Git')

    


