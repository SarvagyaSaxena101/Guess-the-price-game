import streamlit as st
from game_manager import manager

st.set_page_config(page_title="Guess The Price", layout="wide")

def main():
    st.title("ðŸŽ® Guess The Price — Multiplayer ðŸŽ®")

    if 'player_name' not in st.session_state:
        st.session_state.player_name = ""
    if 'room_code' not in st.session_state:
        st.session_state.room_code = ""

    with st.sidebar:
        st.header("ðŸš€ Join or Create Room")
        name = st.text_input("Your name", value=st.session_state.player_name)
        st.session_state.player_name = name

        room_code = st.text_input("Room code (6 chars) to join", value=st.session_state.room_code)
        st.session_state.room_code = room_code.upper()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create Room"):
                code = manager.create_room(name)
                st.session_state.room_code = code
        with col2:
            if st.button("Join Room"):
                try:
                    manager.join_room(st.session_state.room_code, name)
                except Exception as e:
                    st.error(str(e))

        if st.session_state.room_code:
            with st.expander("Room Controls", expanded=True):
                room = manager.get_room(st.session_state.room_code)
                if room is None:
                    st.info("Room not found yet.")
                else:
                    st.write(f"**Room:** {room['code']}")
                    st.write(f"**Host:** {room['host']}")
                    st.write(f"**Players ({len(room['players'])}):**")
                    for p, info in room['players'].items():
                        st.write(f"- {p} — {info['score']} pts")

                    if room['host'] == name:
                        if room['state'] == 'lobby':
                            if st.button("Start Round (host)"):
                                manager.start_round(room['code'])
                        else:
                            cur_price = None
                            if room.get('current_round') and room['current_round'].get('item'):
                                cur_price = room['current_round']['item'].get('price')
                            if cur_price is None:
                                st.warning("Round price is not set.")
                                price_input = st.number_input("Set true price (host)", min_value=0.0, step=0.01, format="%.2f")
                                if st.button("Set price & End Round"):
                                    try:
                                        manager.set_round_price(room['code'], float(price_input))
                                        manager.end_round(room['code'])
                                    except Exception as e:
                                        st.error(str(e))
                            else:
                                if st.button("End Round (host)"):
                                    try:
                                        manager.end_round(room['code'])
                                    except Exception as e:
                                        st.error(str(e))

    if not st.session_state.room_code:
        st.info("Create or join a room to play.")
        return

    room = manager.get_room(st.session_state.room_code)
    if room is None:
        st.error("Room not found. Check code and try again.")
        return

    st.header(f"Room {room['code']}")
    st.subheader(f"State: {room['state']}")

    if st.session_state.player_name not in room['players']:
        st.warning("You're not in the player list for this room. Click Join Room in the sidebar.")
    
    if room['state'] == 'lobby':
        st.write("Waiting for host to start the next round.")
        st.markdown("### Scoreboard")
        scores = sorted(room['players'].items(), key=lambda kv: -kv[1]['score'])
        for name, info in scores:
            st.write(f"**{name}** — {info['score']} pts")

    elif room['state'] == 'in_round':
        rnd = room['current_round']
        st.markdown(f"### Round {rnd['round_no']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if 'item' in rnd and rnd['item']:
                st.image(rnd['item']['image_url'], width=400)
                st.write(f"**{rnd['item']['title']}**")

        with col2:
            if st.session_state.player_name in rnd.get('guesses', {}):
                st.info("You already submitted a guess for this round.")
            else:
                guess = st.number_input("Your price guess", min_value=0.0, step=0.5, format="%.2f")
                if st.button("Submit Guess"):
                    try:
                        manager.submit_guess(room['code'], st.session_state.player_name, float(guess))
                        st.success("Guess submitted.")
                    except Exception as e:
                        st.error(str(e))

            st.markdown("### Round guesses")
            guesses = rnd.get('guesses', {})
            for p, g in guesses.items():
                st.write(f"{p}: {g}")

            if room['host'] == st.session_state.player_name:
                st.info("You are the host. You can end the round from the sidebar.")

    st.markdown("---")
    st.markdown("### Recent rounds")
    for r in reversed(room['rounds'][-5:]):
        st.write(f"Round {r['round_no']} — Item: {r['item']['title']} — Price: {r['item']['price']}")
        st.write("Winners:")
        for w in r.get('winners', []):
            st.write(f"- {w['name']}: guess={w['guess']} diff={w['diff']} pts={w['pts']}")

if __name__ == '__main__':
    main()