# =========================================================
# GLOBAL STYLES
# =========================================================
st.markdown(
    """
    <style>
      section.main > div.block-container{
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
      }

      /* Make all subheader titles (st.subheader) red */
      h3 { color: #c00000 !important; }
      h3 strong { color: #c00000 !important; }

      /* Inline label look (used by inline_label_input) */
      .inline-label{
        font-size: 0.95rem;
        color: #333;
        padding-top: 0.35rem;
        white-space: nowrap;
        word-break: normal;
        overflow-wrap: normal;
      }

      /* ==========================
         GLOBAL VERTICAL SPACING TIGHTENER
         ========================== */

      div[data-testid="stMarkdown"] p,
      div[data-testid="stMarkdown"] h1,
      div[data-testid="stMarkdown"] h2,
      div[data-testid="stMarkdown"] h3,
      div[data-testid="stMarkdown"] h4,
      div[data-testid="stMarkdown"] h5,
      div[data-testid="stMarkdown"] h6 {
        margin-bottom: 0.15rem !important;
        margin-top: 0.15rem !important;
      }

      div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        margin-bottom: 0.35rem !important;
      }

      div[data-testid="stTextArea"],
      div[data-testid="stRadio"],
      div[data-testid="stCheckbox"],
      div[data-testid="stTextInput"],
      div[data-testid="stSelectbox"] {
        margin-top: -0.35rem !important;
      }

      label, .stTextArea label, .stRadio label, .stCheckbox label {
        margin-bottom: 0.15rem !important;
      }

      /* ==========================
         FIX: st.dialog layout (MRC todos os músculos)
         ========================== */

      /* tenta cobrir diferentes versões do Streamlit */
      div[role="dialog"], div[data-testid="stDialog"]{
        width: min(1100px, 96vw) !important;
      }

      /* dentro do dialog: não usar nowrap (evita label invadir os inputs) */
      div[role="dialog"] .inline-label,
      div[data-testid="stDialog"] .inline-label{
        white-space: normal !important;
        padding-top: 0.15rem !important;
      }

      /* dentro do dialog: desliga seus "tighteners" que podem colapsar spacing */
      div[role="dialog"] div[data-testid="stTextInput"],
      div[data-testid="stDialog"] div[data-testid="stTextInput"]{
        margin-top: 0rem !important;
      }

      div[role="dialog"] div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"],
      div[data-testid="stDialog"] div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]{
        margin-bottom: 0.55rem !important;
      }

      /* MRC-SS em vermelho no popup */
      .mrc-ss-red{
        color: #c00000 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# MRC-SS (calc helper) uses the 12 classic keys
# =========================================================
MRC_SS_KEYS = [
    "mrc_ombro_D", "mrc_ombro_E",
    "mrc_cotovelo_D", "mrc_cotovelo_E",
    "mrc_punho_D", "mrc_punho_E",
    "mrc_quadril_D", "mrc_quadril_E",
    "mrc_joelho_D", "mrc_joelho_E",
    "mrc_tornozelo_D", "mrc_tornozelo_E",
]
MRC_SS_KEYS_SET = set(MRC_SS_KEYS)

def compute_mrc_ss(mrc_keys_in: list[str]) -> tuple[bool, int | None]:
    values = []
    for k in mrc_keys_in:
        v = st.session_state.get(k, "")
        if v is None or str(v).strip() == "":
            return (False, None)
        try:
            iv = int(str(v).strip())
        except ValueError:
            return (False, None)
        if iv < 0 or iv > 5:
            return (False, None)
        values.append(iv)
    return (True, sum(values))

# =========================================================
# MRC FULL DIALOG (use temporary keys to avoid duplicates)
# =========================================================
dialog_decorator = getattr(st, "dialog", None)
if dialog_decorator is None:
    dialog_decorator = getattr(st, "experimental_dialog", None)

def _dlg_key(k: str) -> str:
    return f"dlg_{k}"

def _mrc_all_row_dialog(label_html: str, main_key_d: str, main_key_e: str):
    # SEM coluna filler: no dialog ela destrói a largura útil
    c0, c1, c2 = st.columns([6.0, 2.0, 2.0], vertical_alignment="center")

    with c0:
        st.markdown(f'<div class="inline-label">{label_html}</div>', unsafe_allow_html=True)

    with c1:
        st.text_input(
            "",
            key=_dlg_key(main_key_d),
            placeholder="0-5",
            label_visibility="collapsed",
            max_chars=1,
        )

    with c2:
        st.text_input(
            "",
            key=_dlg_key(main_key_e),
            placeholder="0-5",
            label_visibility="collapsed",
            max_chars=1,
        )

if dialog_decorator is not None:
    @dialog_decorator("MRC – todos os músculos")
    def mrc_all_dialog():
        st.markdown("**Membros superiores**")

        hh0, hh1, hh2 = st.columns([6.0, 2.0, 2.0], vertical_alignment="center")
        with hh0:
            st.markdown("**Grupo muscular**")
        with hh1:
            st.markdown("**Direito**")
        with hh2:
            st.markdown("**Esquerdo**")

        # ---- MMSS: MRC-SS em vermelho (por key) ----
        for lbl, kd, ke in MRC_ALL_ITEMS_UPPER:
            is_mrcss_row = (kd in MRC_SS_KEYS_SET) or (ke in MRC_SS_KEYS_SET)
            lbl_show = f'<span class="mrc-ss-red">{lbl}:</span>' if is_mrcss_row else f"{lbl}:"
            _mrc_all_row_dialog(lbl_show, kd, ke)

        st.markdown("---")
        st.markdown("**Membros inferiores**")

        # Header CONSISTENTE com as linhas (3 colunas, sem filler)
        hh0, hh1, hh2 = st.columns([6.0, 2.0, 2.0], vertical_alignment="center")
        with hh0:
            st.markdown("**Grupo muscular**")
        with hh1:
            st.markdown("**Direito**")
        with hh2:
            st.markdown("**Esquerdo**")

        # ---- MMII: MRC-SS em vermelho (por key) ----
        for lbl, kd, ke in MRC_ALL_ITEMS_LOWER:
            is_mrcss_row = (kd in MRC_SS_KEYS_SET) or (ke in MRC_SS_KEYS_SET)
            lbl_show = f'<span class="mrc-ss-red">{lbl}:</span>' if is_mrcss_row else f"{lbl}:"
            _mrc_all_row_dialog(lbl_show, kd, ke)

        # prévia do MRC-SS (usando as chaves temporárias do dialog)
        dlg_mrc_keys = [_dlg_key(k) for k in MRC_SS_KEYS]
        ok_mrc, tot_mrc = compute_mrc_ss(dlg_mrc_keys)

        st.markdown("---")
        if ok_mrc and tot_mrc is not None:
            st.success(f"MRC-SS (prévia): {tot_mrc}")
        else:
            st.info("MRC-SS será calculado ao salvar, se os 12 campos do MRC-SS estiverem preenchidos (0–5).")

        b1, b2, b3 = st.columns([1.4, 1.0, 1.2], vertical_alignment="center")
        with b1:
            if st.button("Salvar", type="primary", key="btn_mrc_all_save"):
                # copia do dialog -> main
                for k in MRC_ALL_KEYS:
                    st.session_state[k] = st.session_state.get(_dlg_key(k), "")

                ok2, tot2 = compute_mrc_ss(MRC_SS_KEYS)
                if ok2 and tot2 is not None:
                    st.session_state["mrc_ss_total"] = str(tot2)

                # limpa temporários
                for k in MRC_ALL_KEYS:
                    st.session_state.pop(_dlg_key(k), None)

                st.rerun()
        with b2:
            if st.button("Cancelar", key="btn_mrc_all_cancel"):
                for k in MRC_ALL_KEYS:
                    st.session_state.pop(_dlg_key(k), None)
                st.rerun()
        with b3:
            if st.button("Limpar todos (popup)", key="btn_mrc_all_clear"):
                for k in MRC_ALL_KEYS:
                    st.session_state[_dlg_key(k)] = ""
                st.rerun()

    def open_mrc_all_dialog():
        # preenche temporários com valores atuais
        for k in MRC_ALL_KEYS:
            st.session_state[_dlg_key(k)] = st.session_state.get(k, "")
        mrc_all_dialog()

else:
    def open_mrc_all_dialog():
        st.warning("Sua versão do Streamlit não suporta pop-up (st.dialog). Atualize para usar 'Todos os músculos'.")
