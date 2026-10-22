import streamlit as st
import pandas as pd


class Players:
    def __init__(self, names=None, max_score=100):
        self.max_score = max_score
        names = names or []
        self.players = {name.strip(): [] for name in names if name.strip()}

    def add_score(self, scores: dict):
        """Adds points for active players and returns a round summary."""
        round_summary = {}
        for name, history in self.players.items():
            current_total = sum(history)

            # Check if player is already eliminated
            if current_total >= self.max_score:
                round_summary[name] = "Eliminated"
                continue

            # Add points if provided
            points = scores.get(name, 0)
            if points is not None:
                history.append(points)
                new_total = sum(history)
                if new_total >= self.max_score:
                    round_summary[name] = f"Eliminated ({new_total})"
                else:
                    round_summary[name] = points
            else:
                round_summary[name] = 0

        return round_summary

    def active_players(self):
        """Returns names of players still under max_score."""
        return [
            name
            for name, history in self.players.items()
            if sum(history) < self.max_score
        ]

    def is_game_over(self):
        """Game ends if 1 or 0 players remain."""
        return len(self.active_players()) <= 1


# --- Streamlit UI Setup ---
st.set_page_config(page_title="Score Tracker", page_icon="🎯", layout="wide")
st.title("🎯 Elimination Score Tracker")

# Initialize session state
if "game" not in st.session_state:
    st.session_state.game = None
if "round_num" not in st.session_state:
    st.session_state.round_num = 1


# --- Sidebar: Game Setup ---
with st.sidebar:
    st.header("Game Settings")
    max_score = st.number_input(
        "Elimination Score Threshold", min_value=10, max_value=1000, value=100, step=10
    )
    names_input = st.text_area(
        "Enter Player Names (one per line)",
        value="Alice\nBob\nCharlie\nDiana",
        height=140,
    )

    if st.button("Start / Reset Game", type="primary"):
        player_list = [n.strip() for n in names_input.splitlines() if n.strip()]
        if len(player_list) < 2:
            st.error("Please enter at least 2 player names.")
        else:
            st.session_state.game = Players(names=player_list, max_score=max_score)
            st.session_state.round_num = 1
            st.rerun()


# --- Main Area ---
game: Players = st.session_state.game

if not game:
    st.info("👈 Enter players and click **Start / Reset Game** in the sidebar to begin.")
else:
    active = game.active_players()

    # Check for game completion
    if len(active) == 1:
        st.balloons()
        st.success(f"🏆 **Winner: {active[0]}!** All other players have been eliminated.")
    elif len(active) == 0:
        st.warning("⚠️ All players were eliminated in the same round!")

    # 1. Score Entry Form for Active Players
    if not game.is_game_over():
        st.subheader(f"Enter Scores — Round {st.session_state.round_num}")
        with st.form("round_scores_form"):
            input_cols = st.columns(min(len(active), 4))
            round_inputs = {}

            for idx, player in enumerate(active):
                col = input_cols[idx % len(input_cols)]
                with col:
                    round_inputs[player] = st.number_input(
                        f"{player}'s points",
                        min_value=0,
                        max_value=game.max_score,
                        value=0,
                        step=1,
                        key=f"score_{player}_{st.session_state.round_num}",
                    )

            submitted = st.form_submit_button("Submit Round Scores", type="primary")
            if submitted:
                game.add_score(round_inputs)
                st.session_state.round_num += 1
                st.rerun()

    # 2. Leaderboard & Status
    st.subheader("Leaderboard & Status")
    table_data = []
    for name, history in game.players.items():
        total = sum(history)
        status = "🟢 Active" if total < game.max_score else "❌ Eliminated"
        table_data.append(
            {
                "Player": name,
                "Total Score": total,
                "Rounds Played": len(history),
                "Status": status,
                "Score History": ", ".join(map(str, history)) if history else "-",
            }
        )

    df = pd.DataFrame(table_data)
    df = df.sort_values(by=["Status", "Total Score"], ascending=[True, True])
    st.dataframe(df, use_container_width=True, hide_index=True)