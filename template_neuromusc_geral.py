pip install streamlit-js-eval
import streamlit as st
import json
import time
from streamlit_js_eval import streamlit_js_eval

# =========================================================
# CONFIG + GLOBAL STYLES (same structure as reference model)
# =========================================================
st.set_page_config(page_title="Template neuromuscular geral", layout="wide")

st.markdown(
    """
    <style>
      section.main > div.block-container{
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Template neuromuscular geral")

st.markdown(
    "<div style='font-size:27px; color:#666; margin-top:-0.5rem; margin-bottom:1rem;'>"
    "consulta inicial e de retorno"
    "</div>",
    unsafe_allow_html=True,
)

# Subheaders in medical red
st.markdown(
    """
    <style>
      h3 { color: #c00000 !important; }
      h3 strong { color: #c00000 !important; }

      /* inline label look */
      .inline-label{
        font-size: 0.95rem;
        color: #333;
        padding-top: 0.35rem;

        /* prevent ugly mid-word breaks */
        white-space: nowrap;
        word-break: normal;
        overflow-wrap: normal;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# Tighten vertical spacing
st.markdown(
    """
    <style>
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
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HELPERS (same philosophy)
# =========================
def text_area_lines(label: str, lines: int, key: str, placeholder: str = ""):
    height_px = max(80, int(lines * 24 + 20))
    return st.text_area(label, key=key, height=height_px, placeholder=placeholder)

def inline_label_input(label_html: str, key: str, placeholder: str = ""):
    c_label, c_input, _fill = st.columns([3.2, 4.2, 10.0], vertical_alignment="center")
    with c_label:
        st.markdown(f'<div class="inline-label">{label_html}</div>', unsafe_allow_html=True)
    with c_input:
        return st.text_input("", key=key, placeholder=placeholder, label_visibility="collapsed")

def inline_label_display(label_text: str, value: str, help_text: str | None = None):
    c_label, c_box, _fill = st.columns([3.2, 6.0, 10.0], vertical_alignment="center")
    with c_label:
        st.markdown(f'<div class="inline-label">{label_text}</div>', unsafe_allow_html=True)
    with c_box:
        st.text_input("", value=value, disabled=True, label_visibility="collapsed", help=help_text)

def small_mrc_box(key: str, placeholder: str = "0-5"):
    return st.text_input(
        "Valor (0–5)",
        key=key,
        placeholder=placeholder,
        label_visibility="collapsed",
        max_chars=1,
    )

def _get(key: str, default: str = "") -> str:
    v = st.session_state.get(key, default)
    if v is None:
        return ""
    return str(v).strip()

def _section(title: str, body: str) -> str:
    body = (body or "").strip()
    if not body:
        return ""
    return f"{title}\n{body}\n"

def _bool_to_txt(v: bool) -> str:
    return "Sim" if v else "Não"

def inline_label_input_dnpm(label_text: str, key: str, placeholder: str = ""):
    # Wider label column so words don't wrap/break
    c_label, c_input = st.columns([5.2, 2.8], vertical_alignment="center")
    with c_label:
        st.markdown(f'<div class="inline-label">{label_text}</div>', unsafe_allow_html=True)
    with c_input:
        return st.text_input("", key=key, placeholder=placeholder, label_visibility="collapsed")

# =========================
# SESSION STATE INIT
# =========================
# Force panel
if "forca_open" not in st.session_state:
    st.session_state["forca_open"] = False
if "forca_resumo" not in st.session_state:
    st.session_state["forca_resumo"] = ""  # auto-generated summary text

# Functional panel
if "func_open" not in st.session_state:
    st.session_state["func_open"] = False
if "func_resumo" not in st.session_state:
    st.session_state["func_resumo"] = ""

# Export mode
if "export_mode" not in st.session_state:
    st.session_state["export_mode"] = None  # "evolucao" | "completo" | None
if "export_text" not in st.session_state:
    st.session_state["export_text"] = ""

# =========================================================
# 1) ANAMNESE
# =========================================================
st.subheader("Anamnese")

st.markdown("**Identificação:**")
_ = text_area_lines(
    label="",
    lines=1,
    key="Id",
    placeholder="",)
    
c_label, c_input, _fill = st.columns([3.2, 7.0, 10.0], vertical_alignment="center")
with c_label:
    st.markdown('<div class="inline-label"><strong>Idade de início</strong></div>', unsafe_allow_html=True)
with c_input:
    st.text_input("", key="idade_inicio", placeholder="Ex.: 12 anos / 2021 / infância", label_visibility="collapsed")


st.markdown("**História da doença atual:**")
_ = text_area_lines(
    label="",
    lines=10,
    key="hda",
    placeholder="",
)

# =========================================================
# 2) ANTECEDENTES
# =========================================================
st.subheader("Antecedentes")

st.markdown("**Antecedentes pessoais:**")
_ = text_area_lines(
    label="",
    lines=6,
    key="antecedentes_pessoais",
    placeholder=(
        "Descrever cardiopatias, distúrbios do sono, catarata, neoplasias, distúrbios respiratórios, "
        "endocrinopatias, exposição ocupacional, diabetes, hipertensão, etilismo, cirurgias prévias, etc."
    ),
)

st.markdown("**História familiar:**")
_ = text_area_lines(
    label="",
    lines=4,
    key="antecedentes_familiares",
    placeholder=(
        "Familiares acometidos / estado de saúde de pais, irmãos e filhos / cidade de origem dos pais / consanguinidade / etc."
    ),
)

st.markdown("**Medicações em uso:**")
_ = text_area_lines(
    label="",
    lines=6,
    key="meds_em_uso",
    placeholder="",
)

st.markdown("**Medicações de uso prévio e motivo da suspensão:**")
_ = text_area_lines(
    label="",
    lines=1,
    key="meds_previas",
    placeholder="",
)

# =========================================================
# 3) DESENVOLVIMENTO NEUROPSICOMOTOR
# =========================================================
st.subheader("Desenvolvimento neuropsicomotor")

dnpm = st.radio(
    "",
    options=["Normal", "Não sabe informar", "Atraso desenvolvimento"],
    index=None,
    key="dnpm_radio",
)

if dnpm == "Atraso desenvolvimento":
    st.markdown("**Idade de obtenção dos marcos motores e cognitivos:**")

    # Two-column grid for compactness
    colA, colB = st.columns(2, vertical_alignment="top")

    with colA:
        inline_label_input_dnpm("Sustento cefálico", key="dnpm_sustento_cefalico", placeholder="Ex.: 4 meses")
        inline_label_input_dnpm("Engatinhar", key="dnpm_engatinhar", placeholder="Ex.: 10 meses")
        inline_label_input_dnpm("Andar sem apoio", key="dnpm_andar_sem_apoio", placeholder="Ex.: 18 meses")
        inline_label_input_dnpm("Formar frases", key="dnpm_formar_frases", placeholder="Ex.: 3 anos")
        inline_label_input_dnpm("Sentar (meses)", key="dnpm_sentar_meses", placeholder="Ex.: 8")

    with colB:
        inline_label_input_dnpm("Ficar de pé (anos)", key="dnpm_ficar_de_pe_anos", placeholder="Ex.: 2")
        inline_label_input_dnpm("Andar com apoio (anos)", key="dnpm_andar_com_apoio_anos", placeholder="Ex.: 2")
        inline_label_input_dnpm("Primeiras palavras (anos)", key="dnpm_primeiras_palavras_anos", placeholder="Ex.: 2")
        inline_label_input_dnpm("Controle esfincteriano (meses)", key="dnpm_controle_esfincteriano_meses", placeholder="Ex.: 30")

# =========================================================
# 4) EVOLUÇÃO (panel)
# =========================================================

st.subheader("Evolução clínica")
st.markdown("**Descrição da evolução:**")
_ = text_area_lines(
    label="",
    lines=5,
    key="evolucao",
    placeholder="",
)

# =========================================================
# 8) AVALIAÇÃO FUNCIONAL (panel summary)
# =========================================================
st.markdown("**Avaliação funcional**")

cL, cR = st.columns([2.2, 9.8], vertical_alignment="top")
with cL:
    if st.button("Avaliação funcional", key="btn_open_func"):
        st.session_state["func_open"] = True
with cR:
    disp = st.session_state.get("func_resumo", "").strip()
    if not disp:
        disp = "Gerado automaticamente ao preencher a avaliação funcional"
    st.text_area(
    "Avaliação funcional (resumo)",
    value=disp,
    height=120,   # ~4–5 lines
    disabled=True,
)

def build_func_summary() -> str:
    parts = []

    # -------------------------
    # 1) Limitações motoras
    # -------------------------
    modo = _get("func_modo")
    if modo == "Sem limitações":
        parts.append("Sem limitações motoras atuais.")
    elif modo == "Com limitações":
        mi = []
        ms = []

        mi_map = [
            ("Anda com apoio unilateral", "mi_apoio_unilateral"),
            ("Anda com apoio bilateral", "mi_apoio_bilateral"),
            ("Fica de pé mas não troca passos", "mi_pe_sem_passos"),
            ("Não fica de pé sem suporte", "mi_nao_fica_pe"),
            ("Não faz transferências sem ajuda", "mi_nao_transfere"),
            ("Não senta sem suporte", "mi_nao_senta"),
            ("Não levanta do chão sem ajuda", "mi_nao_levanta_chao"),
        ]
        ms_map = [
            ("Não eleva os braços acima da cabeça", "ms_nao_acima_cabeca"),
            ("Não eleva os braços acima dos ombros", "ms_nao_acima_ombros"),
            ("Não faz flexão dos antebraços", "ms_nao_flex_antebraco"),
        ]

        for lbl, k in mi_map:
            if st.session_state.get(k):
                mi.append(lbl)
        for lbl, k in ms_map:
            if st.session_state.get(k):
                ms.append(lbl)

        lim_parts = []
        if mi:
            lim_parts.append("MMII: " + "; ".join(mi))
        if ms:
            lim_parts.append("MMSS: " + "; ".join(ms))
        if lim_parts:
            parts.append("Limitações: " + " | ".join(lim_parts))
        else:
            parts.append("Limitações: Com limitações (não detalhadas).")

    # If modo is not chosen, don't add anything (keeps summary optional)

    # -------------------------
    # 2) Órteses / cadeira (optional)
    # -------------------------
    ort = []
    for lbl, k in [
        ("Não usa", "ortese_nao_usa"),
        ("Órteses MMII", "ortese_mi"),
        ("Cadeira de rodas", "cadeira_rodas"),
        ("Órteses MMSS", "ortese_ms"),
        ("Colete ortopédico", "colete_ortopedico"),
    ]:
        if st.session_state.get(k):
            ort.append(lbl)

    ort_outros = _get("ortese_outros")
    if ort_outros:
        ort.append(f"Outros: {ort_outros}")

    if ort:
        parts.append("Órteses/Cadeira de rodas: " + "; ".join(ort))

    # -------------------------
    # 3) Ventilação (optional)
    # -------------------------
    vent_line = _get("vent_radio")
    vent_info = _get("vent_info_adicional")
    if vent_line or vent_info:
        vent_txt = vent_line if vent_line else ""
        if vent_info:
            vent_txt += (" — " if vent_txt else "") + vent_info
        parts.append("Ventilação: " + vent_txt)

    return "\n".join([p for p in parts if p.strip()]).strip()


if st.session_state["func_open"]:
    st.markdown("#### Limitações motoras atuais")

    modo = st.radio(
        "",
        options=["Sem limitações", "Com limitações"],
        index=None,
        key="func_modo",
    )

    if modo == "Com limitações":
        st.markdown("**Membros inferiores**")
        st.checkbox("Anda com apoio unilateral", key="mi_apoio_unilateral")
        st.checkbox("Anda com apoio bilateral", key="mi_apoio_bilateral")
        st.checkbox("Fica de pé mas não troca passos", key="mi_pe_sem_passos")
        st.checkbox("Não fica de pé sem suporte", key="mi_nao_fica_pe")
        st.checkbox("Não faz transferências sem ajuda (cadeira para cama, por exemplo)", key="mi_nao_transfere")
        st.checkbox("Não senta sem suporte", key="mi_nao_senta")
        st.checkbox("Não levanta do chão sem ajuda", key="mi_nao_levanta_chao")

        st.markdown("---")
        st.markdown("**Membros superiores**")
        st.checkbox("Não eleva os braços acima da cabeça", key="ms_nao_acima_cabeca")
        st.checkbox("Não eleva os braços acima dos ombros", key="ms_nao_acima_ombros")
        st.checkbox("Não faz flexão dos antebraços", key="ms_nao_flex_antebraco")

    st.markdown("---")
    st.markdown("### Uso de órteses e/ou cadeira de rodas")

    st.checkbox("Não usa", key="ortese_nao_usa")
    st.checkbox("Usa órteses para membros inferiores", key="ortese_mi")
    st.checkbox("Usa cadeira de rodas", key="cadeira_rodas")
    st.checkbox("Usa órteses para membros superiores", key="ortese_ms")
    st.checkbox("Usa colete ortopédico", key="colete_ortopedico")
    _ = inline_label_input("Outros", key="ortese_outros", placeholder="Especifique")

    st.markdown("---")
    st.markdown("### Uso de suporte ventilatório")

    vent_options = [
        "Sem indicação",
        "Tem indicação de BiPAP, mas não faz uso",
        "BiPAP – uso noturno",
        "BiPAP – uso diurno e noturno",
        "Traqueostomia",
        "Ventilação invasiva permanente",
    ]
    st.radio("", options=vent_options, index=None, key="vent_radio")

    _ = text_area_lines(
        label="",
        lines=3,
        key="vent_info_adicional",
        placeholder="Informações adicionais (tempo diário de ventilação, equipamento, parâmetros).",
    )

    
    b1, b2, _bf = st.columns([1.6, 1.2, 10.0], vertical_alignment="center")
    with b1:
        if st.button("Salvar limitações", key="btn_save_func", type="primary"):
            st.session_state["func_resumo"] = build_func_summary()
            st.session_state["func_open"] = False
            st.rerun()
    with b2:
        if st.button("Minimizar menu de seleção", key="btn_cancel_func"):
            st.session_state["func_open"] = False
            st.rerun()

# =========================================================
# 9) SEGUIMENTO MULTIDISCIPLINAR
# =========================================================
st.markdown("**Seguimento multidisciplinar**")

def freq_row(label: str, check_key: str, freq_key: str):
    c0, c1, c2, _f = st.columns([3.2, 1.6, 2.2, 10.0], vertical_alignment="center")
    with c0:
        st.markdown(f'<div class="inline-label">{label}</div>', unsafe_allow_html=True)
    with c1:
        checked = st.checkbox("Sim", key=check_key)
    with c2:
        st.text_input(
            "",
            key=freq_key,
            placeholder="vezes/semana",
            label_visibility="collapsed",
            disabled=not checked,
        )

freq_row("Fisioterapia motora", "fisio_motora_chk", "fisio_motora_freq")
freq_row("Fisioterapia respiratória", "fisio_resp_chk", "fisio_resp_freq")
freq_row("Ambú / máscara facial", "ambu_chk", "ambu_freq")
freq_row("Fonoterapia", "fono_chk", "fono_freq")
freq_row("Terapia ocupacional", "to_chk", "to_freq")
freq_row("Psicoterapia", "psico_chk", "psico_freq")

st.markdown("**Outras terapias e informações:**")
_ = text_area_lines("", 3, "outras_terapias", placeholder="")

# =========================================================
# 4) NEUROLÓGICO GERAL + EXAME DE FORÇA (panel)
# =========================================================
st.subheader("Exame físico")

st.markdown("**Exame neurológico geral**")

_ = text_area_lines(
    label="",
    lines=5,
    key="neuro_geral",
    placeholder=(
        "Descrever cognição, força, reflexos osteotendinosos, reflexos patológicos (cutâneo plantar, axiais da face), "
        "tônus, sensibilidade, coordenação, marcha, nervos cranianos"
    ),
)

# --- aligned area: button left, summary right (like INCAT/PND area) ---
c_left, c_right = st.columns([2.2, 9.8], vertical_alignment="top")

with c_left:
    if st.button("Exame de força", key="btn_open_forca"):
        st.session_state["forca_open"] = True

with c_right:
    display_forca = st.session_state.get("forca_resumo", "").strip()
    if not display_forca:
        display_forca = "Gerado automaticamente ao preencher o exame de força"
    st.text_area(
        "Força motora (resumo)",
        value=display_forca,
        height=120,   # ~4–5 lines
        disabled=True,
    )


# --------------------------
# FORCE PANEL
# --------------------------
def _force_row_bilateral(label: str, key_d: str, key_e: str):
    c0, c1, c2, _fill = st.columns([3.2, 1.4, 1.4, 10.0], vertical_alignment="center")
    with c0:
        st.markdown(f'<div class="inline-label">{label}</div>', unsafe_allow_html=True)
    with c1:
        small_mrc_box(key_d)
    with c2:
        small_mrc_box(key_e)

def _force_row_single(label: str, key: str, placeholder: str = "0-5"):
    c0, c1, _fill = st.columns([3.2, 3.0, 10.0], vertical_alignment="center")
    with c0:
        st.markdown(f'<div class="inline-label">{label}</div>', unsafe_allow_html=True)
    with c1:
        st.text_input("", key=key, placeholder=placeholder, label_visibility="collapsed", max_chars=1)


def build_forca_summary() -> str:
    """
    Summarize only filled items.
    """
    lines: list[str] = []

    def add_single(lbl: str, k: str):
        v = _get(k)
        if v != "":
            lines.append(f"{lbl}: {v}")

    def add_bilat(lbl: str, kd: str, ke: str):
        vd = _get(kd)
        ve = _get(ke)
        if vd != "" or ve != "":
            lines.append(f"{lbl}: D {vd or '-'} / E {ve or '-'}")

    # Axial
    axial = []
    v_ext_tronco = _get("mrc_ext_tronco")
    if v_ext_tronco:
        axial.append(f"Extensores do tronco {v_ext_tronco}")
    v_flex_pescoco = _get("mrc_flex_pescoco")
    if v_flex_pescoco:
        axial.append(f"Flexores do pescoço {v_flex_pescoco}")
    v_flex_tronco = _get("mrc_flex_tronco")
    if v_flex_tronco:
        axial.append(f"Flexores do tronco {v_flex_tronco}")
    


    if axial:
        lines.append("Axiais: " + " | ".join(axial))

    # Upper
    add_bilat("Abdução do ombro", "mrc_abd_ombro_D", "mrc_abd_ombro_E")
    add_bilat("Adução do ombro", "mrc_add_ombro_D", "mrc_add_ombro_E")
    add_bilat("Flexores do cotovelo", "mrc_flex_cotovelo_D", "mrc_flex_cotovelo_E")
    add_bilat("Extensores do cotovelo", "mrc_ext_cotovelo_D", "mrc_ext_cotovelo_E")
    add_bilat("Extensores de punho", "mrc_ext_punho_D", "mrc_ext_punho_E")
    add_bilat("Flexores de punho", "mrc_flex_punho_D", "mrc_flex_punho_E")
    add_bilat("Extensores de dedos", "mrc_ext_dedos_D", "mrc_ext_dedos_E")
    add_bilat("Flexores profundos dos dedos", "mrc_fpd_D", "mrc_fpd_E")
    add_bilat("Abdução dos dedos", "mrc_abd_dedos_D", "mrc_abd_dedos_E")
    add_bilat("Oponência do polegar", "mrc_op_polegar_D", "mrc_op_polegar_E")
    add_bilat("Oponência do dedo mínimo", "mrc_op_minimo_D", "mrc_op_minimo_E")

    # Lower
    add_bilat("Flexores de quadril", "mrc_flex_quadril_D", "mrc_flex_quadril_E")
    add_bilat("Extensores do quadril", "mrc_ext_quadril_D", "mrc_ext_quadril_E")
    add_bilat("Abdutores do quadril", "mrc_abd_quadril_D", "mrc_abd_quadril_E")
    add_bilat("Adutores do quadril", "mrc_add_quadril_D", "mrc_add_quadril_E")
    add_bilat("Flexores do joelho", "mrc_flex_joelho_D", "mrc_flex_joelho_E")
    add_bilat("Extensores do joelho", "mrc_ext_joelho_D", "mrc_ext_joelho_E")
    add_bilat("Dorsiflexão do pé", "mrc_df_pe_D", "mrc_df_pe_E")
    add_bilat("Flexão do pé", "mrc_pf_pe_D", "mrc_pf_pe_E")
    add_bilat("Eversores do pé", "mrc_ev_pe_D", "mrc_ev_pe_E")
    add_bilat("Inversores do pé", "mrc_inv_pe_D", "mrc_inv_pe_E")
    add_bilat("Extensores do hálux", "mrc_ext_halux_D", "mrc_ext_halux_E")
    add_bilat("Flexores do hálux", "mrc_flex_halux_D", "mrc_flex_halux_E")

    if not lines:
        return ""
    return "Força motora (MRC): " + " | ".join(lines)

if st.session_state["forca_open"]:
    st.markdown("#### Força motora (escala MRC)")

    st.markdown("**Músculos axiais:**")
    _force_row_single("Extensores do tronco", "mrc_ext_tronco", placeholder="0-5")
    _force_row_single("Flexores do pescoço", "mrc_flex_pescoco", placeholder="0-5")
    _force_row_single("Flexores do tronco", "mrc_flex_tronco", placeholder="0-5")

    st.markdown("---")
    st.markdown("**Músculos dos membros superiores:**")
    # header
    h0, h1, h2, _hf = st.columns([3.2, 1.4, 1.4, 10.0], vertical_alignment="center")
    with h0:
        st.markdown("**Grupo muscular**")
    with h1:
        st.markdown("**Direito**")
    with h2:
        st.markdown("**Esquerdo**")

    _force_row_bilateral("Abdução do ombro", "mrc_abd_ombro_D", "mrc_abd_ombro_E")
    _force_row_bilateral("Adução do ombro", "mrc_add_ombro_D", "mrc_add_ombro_E")
    _force_row_bilateral("Flexores do cotovelo", "mrc_flex_cotovelo_D", "mrc_flex_cotovelo_E")
    _force_row_bilateral("Extensores do cotovelo", "mrc_ext_cotovelo_D", "mrc_ext_cotovelo_E")
    _force_row_bilateral("Extensores de punho", "mrc_ext_punho_D", "mrc_ext_punho_E")
    _force_row_bilateral("Flexores de punho", "mrc_flex_punho_D", "mrc_flex_punho_E")
    _force_row_bilateral("Extensores de dedos", "mrc_ext_dedos_D", "mrc_ext_dedos_E")
    _force_row_bilateral("Flexores profundos dos dedos", "mrc_fpd_D", "mrc_fpd_E")
    _force_row_bilateral("Abdução dos dedos", "mrc_abd_dedos_D", "mrc_abd_dedos_E")
    _force_row_bilateral("Oponência do polegar", "mrc_op_polegar_D", "mrc_op_polegar_E")
    _force_row_bilateral("Oponência do dedo mínimo", "mrc_op_minimo_D", "mrc_op_minimo_E")

    st.markdown("---")
    st.markdown("**Músculos dos membros inferiores:**")
    # header
    h0, h1, h2, _hf = st.columns([3.2, 1.4, 1.4, 10.0], vertical_alignment="center")
    with h0:
        st.markdown("**Grupo muscular**")
    with h1:
        st.markdown("**Direito**")
    with h2:
        st.markdown("**Esquerdo**")

    _force_row_bilateral("Flexores de quadril", "mrc_flex_quadril_D", "mrc_flex_quadril_E")
    _force_row_bilateral("Extensores do quadril", "mrc_ext_quadril_D", "mrc_ext_quadril_E")
    _force_row_bilateral("Abdutores do quadril", "mrc_abd_quadril_D", "mrc_abd_quadril_E")
    _force_row_bilateral("Adutores do quadril", "mrc_add_quadril_D", "mrc_add_quadril_E")
    _force_row_bilateral("Flexores do joelho", "mrc_flex_joelho_D", "mrc_flex_joelho_E")
    _force_row_bilateral("Extensores do joelho", "mrc_ext_joelho_D", "mrc_ext_joelho_E")
    _force_row_bilateral("Dorsiflexão do pé", "mrc_df_pe_D", "mrc_df_pe_E")
    _force_row_bilateral("Flexão do pé", "mrc_pf_pe_D", "mrc_pf_pe_E")
    _force_row_bilateral("Eversores do pé", "mrc_ev_pe_D", "mrc_ev_pe_E")
    _force_row_bilateral("Inversores do pé", "mrc_inv_pe_D", "mrc_inv_pe_E")
    _force_row_bilateral("Extensores do hálux", "mrc_ext_halux_D", "mrc_ext_halux_E")
    _force_row_bilateral("Flexores do hálux", "mrc_flex_halux_D", "mrc_flex_halux_E")

    b1, b2, _bfill = st.columns([1.6, 1.2, 10.0], vertical_alignment="center")
    with b1:
        if st.button("Salvar exame de força", key="btn_save_forca", type="primary"):
            st.session_state["forca_resumo"] = build_forca_summary()
            st.session_state["forca_open"] = False
            st.rerun()
    with b2:
        if st.button("Minimizar menu de seleção", key="btn_cancel_forca"):
            st.session_state["forca_open"] = False
            st.rerun()

st.divider()

# =========================================================
# 5) EXAME NEUROMUSCULAR ESPECÍFICO
# =========================================================
st.markdown("**Exame neuromuscular específico**")

_ = text_area_lines(
    label="",
    lines=4,
    key="exame_neuromuscular_especifico",
    placeholder=(
        "Testes de fatigabilidade para miastenia, Simpson, Cogan, sinal da cortina, língua tri-sulcada, "
        "facilitação do reflexo pós-esforço, lentificação do reflexo pupilar.\n"
        "Fasciculações, mioquimias, rippling.\n"
        "Miotonia (língua, membros, percussão)."
    ),
)

# =========================================================
# 6) PELE / EXAME CLÍNICO GERAL
# =========================================================
st.markdown("**Alterações de pele e exame clínico geral**")

_ = text_area_lines(
    label="",
    lines=3,
    key="pele_clinico_geral",
    placeholder="Alterações da pele (quelóide, hiperqueratose folicular), cardíaco, respiratório, abdominal, etc.",
)

# =========================================================
# 7) OSTEOESQUELÉTICAS / DISMORFISMOS
# =========================================================
st.markdown("**Alterações osteoesqueléticas e dismorfismos**")

_ = text_area_lines(
    label="",
    lines=3,
    key="osteo_dismorfismos",
    placeholder=(
        "Deformidades de coluna, retrações articulares, deformidades torácicas, deformidade de quadril, "
        "escápula alada, hiperextensibilidade distal, palato em ogiva, maloclusão dentária."
    ),
)

# =========================================================
# 12) EXAMES COMPLEMENTARES
# =========================================================
st.subheader("Exames complementares")

_ = inline_label_input("CPK", key="ex_cpk", placeholder="Ex.: 350 U/L (data)")
st.markdown("**Eletroneuromiografia**")
_ = text_area_lines("", 3, "ex_enmg", placeholder="")

_ = inline_label_input("Decremento / Jitter na EMG", key="ex_decremento_jitter", placeholder="")
_ = inline_label_input("Anti-receptor de acetilcolina", key="ex_achr", placeholder="")
_ = inline_label_input("Outros anticorpos de junção", key="ex_outros_juncao", placeholder="")

_ = inline_label_input("Anticorpos para miosites", key="ex_miosites", placeholder="")
st.markdown("**RM muscular**")
_ = text_area_lines("", 3, "ex_rm_muscular", placeholder="")
st.markdown("**Biópsia muscular**")
_ = text_area_lines("", 3, "ex_biopsia_muscular", placeholder="")

st.markdown("**Cardiorrespiratórios**")
_ = text_area_lines("", 2, "ex_eco", placeholder="ECO (data e achados)")
_ = text_area_lines("", 2, "ex_holter", placeholder="Holter (data e achados)")
_ = text_area_lines("", 2, "ex_espirometria", placeholder="Espirometria (data e achados)")
_ = text_area_lines("", 2, "ex_polissonografia", placeholder="Polissonografia (data e achados)")

st.markdown("**Outros exames**")
_ = text_area_lines("", 3, "ex_outros", placeholder="")

# =========================================================
# 14) TESTE GENÉTICO
# =========================================================
st.subheader("Teste genético")

tg = st.radio("", options=["Não realizado", "Teste genético realizado"], index=None, key="tg_radio")

genes_options = [
    "Teste negativo",
    "ACTA1","ANO5","CAPN3","CHRNE","CLCN1","CPT2","D4Z4","DES","DMD","DMPK","DOK7","DUX4","DYSF",
    "FKRP","GAA","GJB1","GNE","LAMA2","LMNA","MFN2","MPZ","MTM1","NEB","PYGM","RAPSN","RYR1",
    "SMN1","TPM3","TTN","TTR","POMT1","POMT2","POMGNT1","COL6A1","COL6A2","COL6A3",
    "SGCA","SGCB","SGCD","SGCG",
]

if tg == "Teste genético realizado":
    st.markdown("**Resultado / gene (pesquise digitando):**")
    gene_sel = st.selectbox("Gene / Resultado", options=genes_options, index=0, key="tg_gene_sel")

    st.markdown("**Detalhes do exame:**")
    _ = inline_label_input("Exame genético realizado", key="tg_exame_nome", placeholder="Ex.: Painel miopatias / Exoma / MLPA / etc.")
    _ = inline_label_input("Data", key="tg_data", placeholder="Ex.: 10/2024")
    _ = inline_label_input("Local do exame", key="tg_local", placeholder="Ex.: Fleury / Einstein / laboratório X")

# =========================================================
# 13) DIAGNÓSTICO TOPOGRÁFICO
# =========================================================
st.subheader("Diagnóstico topográfico")

topo_options = [
    "Central",
    "Ponta anterior",
    "Gânglio da raiz dorsal",
    "Raiz",
    "Polirradiculoneuropatia",
    "Polineuropatia",
    "Mononeuropatia",
    "Múltiplos nervos",
    "Junção neuromuscular",
    "Músculo esquelético",
    "Funcional",
    "Outro",
]
topo = st.selectbox("Selecione", options=topo_options, index=0, key="dx_topografico")

if topo == "Outro":
    _ = inline_label_input("Especifique", key="dx_topografico_outro", placeholder="")

# =========================================================
# 15) DIAGNÓSTICO NOSOLÓGICO
# =========================================================
st.subheader("Diagnóstico nosológico")

dx_noso_options = [
    "Atrofia muscular espinhal tipo 1 (SMN1) (G12.0)",
    "Atrofia muscular espinhal tipo 2 (SMN1) (G12.1)",
    "Atrofia muscular espinhal tipo 3 (SMN1) (G12.1)",
    "Atrofia muscular espinhal tipo 4 (SMN1) (G12.1)",
    "Atrofia espinhal muscular não 5q (G12.1)",
    "Doenças do neurônio motor (outras formas) (G12.2)",
    "Esclerose lateral amiotrófica (G12.2)",
    "Polineuropatia tóxico/metabólica/diabetes (G62–G63)",
    "Neuropatias sensitivo-motoras hereditárias (CMT) (G60.0)",
    "Polirradiculoneurite inflamatória aguda ou crônica (G61)",
    "CIAP (Chronic idiopathic axonal polyneuropathy) (G61)",
    "Radiculopatias / plexopatias (M54.1)",
    "Mononeuropatia isolada ou múltipla (vasculítica, hansênica e outras) (G56, G67)",
    "Miastenia congênita (G70.2)",
    "Miastenia gravis (G70.0)",
    "Outras formas de distúrbios da junção (G70)",
    "Miopatia congênita nemalínica (G71.2)",
    "Miopatia congênita cores (G71.2)",
    "Miopatia congênita centronuclear (G71.2)",
    "Miopatia congênita miotubular / portadoras sintomáticas MTM (G71.2)",
    "Miopatia congênita – desproporção congênita fibras (G71.2)",
    "Miopatia congênita não classificada (G71.2)",
    "Distrofia muscular congênita – Merosina (G71.2)",
    "Distrofia muscular congênita – Colágeno 6 (G71.2)",
    "Distrofia muscular congênita – Alfa-distroglicana (G71.2)",
    "Distrofia muscular congênita – outras formas e não classificadas (G71.2)",
    "Distrofia muscular de Duchenne (G71.0)",
    "Distrofia muscular de Becker (G71.0)",
    "Distrofinopatia – mulher portadora (G71.0)",
    "Distrofia muscular de cinturas (G71.0)",
    "Distrofia de Emery-Dreifuss (G71.0)",
    "Distrofia fascioescapuloumeral (G71.0)",
    "Distrofia miotônica de Steinert (G71.0)",
    "Miotonia congênita / paramiotonia / Síndrome hiperexcitabilidade (G72)",
    "Paralisia periódica (G72)",
    "Miosite com corpos de inclusão (IBM) (M60)",
    "Miopatia miofibrilar (G72)",
    "Miopatia distal (G72)",
    "Miopatia vacuolar (G72)",
    "Miopatia associada ao HIV (G72)",
    "Miopatia de causa sistêmica (G72)",
    "Miosites outras (M60)",
    "Glicogenose (Pompe, McArdle, outros) (G72)",
    "Lipidose (G72)",
    "Mitocondrial (G71.3)",
    "Miopatia inespecífica (G72.9)",
    "Miopatia inflamatória (polimiosite/necrotizante/dermatomiosite) (M33, M33.2)",
    "Não esclarecido",
    "Quadro funcional",
    "Central",
    "Outros",
]

dx_noso = st.selectbox(
    "Selecione (pesquise digitando)",
    options=dx_noso_options,
    index=0,
    key="dx_noso_sel",
)

if dx_noso == "Outros":
    _ = inline_label_input("Especifique", key="dx_noso_outros", placeholder="")

# =========================================================
# 16) IMPRESSÃO / CONDUTA
# =========================================================
st.subheader("Impressão")
_ = text_area_lines("", 4, "impressao", placeholder="")

st.subheader("Conduta")
_ = text_area_lines("", 4, "conduta", placeholder="")

# =========================================================
# EXPORT (updated: order + structure aligned to current UI)
# =========================================================
def _safe_call(fn, fallback: str = "") -> str:
    try:
        v = fn()
        return (v or "").strip()
    except Exception:
        return fallback

def build_export_text(include_all: bool) -> str:
    parts: list[str] = []

    # -----------------------------
    # 1) ANAMNESE / ANTECEDENTES / DNPM (only in full export)
    # -----------------------------
    if include_all:
        # Anamnese
        anam_lines = []
        if _get("Id"):
            anam_lines.append("# Identificação:\n" + _get("Id"))
        if _get("idade_inicio"):
            anam_lines.append("Idade de início: " + _get("idade_inicio"))
        if _get("hda"):
            anam_lines.append("# HMA:\n" + _get("hda"))
        parts.append(_section("ANAMNESE", "\n\n".join([x for x in anam_lines if x.strip()])))

        # Antecedentes
        ant_lines = []
        if _get("antecedentes_pessoais"):
            ant_lines.append("# Antecedentes pessoais:\n" + _get("antecedentes_pessoais"))
        if _get("antecedentes_familiares"):
            ant_lines.append("# História familiar:\n" + _get("antecedentes_familiares"))
        if _get("meds_em_uso"):
            ant_lines.append("# Medicações em uso:\n" + _get("meds_em_uso"))
        if _get("meds_previas"):
            ant_lines.append("Medicações prévias / motivo da suspensão:\n" + _get("meds_previas"))
        parts.append(_section("ANTECEDENTES", "\n\n".join([x for x in ant_lines if x.strip()])))

        # DNPM
        dnpm_radio = _get("dnpm_radio")
        dnpm_block = f"Status: {dnpm_radio}" if dnpm_radio else ""
        if dnpm_radio == "Atraso desenvolvimento":
            milestones = []
            for lbl, k in [
                ("Sustento cefálico", "dnpm_sustento_cefalico"),
                ("Engatinhar", "dnpm_engatinhar"),
                ("Andar sem apoio", "dnpm_andar_sem_apoio"),
                ("Formar frases", "dnpm_formar_frases"),
                ("Sentar (meses)", "dnpm_sentar_meses"),
                ("Ficar de pé (anos)", "dnpm_ficar_de_pe_anos"),
                ("Andar com apoio (anos)", "dnpm_andar_com_apoio_anos"),
                ("Primeiras palavras (anos)", "dnpm_primeiras_palavras_anos"),
                ("Controle esfincteriano (meses)", "dnpm_controle_esfincteriano_meses"),
            ]:
                v = _get(k)
                if v:
                    milestones.append(f"{lbl}: {v}")
            if milestones:
                dnpm_block = (dnpm_block + "\n" if dnpm_block else "") + "Marcos:\n" + "\n".join(milestones)
        parts.append(_section("DESENVOLVIMENTO NEUROPSICOMOTOR", dnpm_block))

    # -----------------------------
    # 2) EVOLUÇÃO CLÍNICA (always)
    # -----------------------------
    parts.append(_section("EVOLUÇÃO CLÍNICA", _get("evolucao")))

    # -----------------------------
    # 3) AVALIAÇÃO FUNCIONAL (always)
    # - Prefer saved func_resumo, otherwise compute from current selections
    # -----------------------------
    func_block = _get("func_resumo")
    if not func_block:
        func_block = _safe_call(build_func_summary, "")
    parts.append(_section(">> Avaliação funcional:", func_block))

    # -----------------------------
    # 4) SEGUIMENTO MULTIDISCIPLINAR (always)
    # -----------------------------
    multi_lines = []

    def add_freq(name: str, chk: str, freq: str):
        if st.session_state.get(chk):
            f = _get(freq)
            multi_lines.append(f"{name}: {f + 'x/sem' if f else '(freq. não informada)'}")

    add_freq("Fisioterapia motora", "fisio_motora_chk", "fisio_motora_freq")
    add_freq("Fisioterapia respiratória", "fisio_resp_chk", "fisio_resp_freq")
    add_freq("Ambú / máscara facial", "ambu_chk", "ambu_freq")
    add_freq("Fonoterapia", "fono_chk", "fono_freq")
    add_freq("Terapia ocupacional", "to_chk", "to_freq")
    add_freq("Psicoterapia", "psico_chk", "psico_freq")

    outras = _get("outras_terapias")
    if outras:
        multi_lines.append("Outras:\n" + outras)

    parts.append(_section(">> Seguimento multidisciplinar", "\n".join([x for x in multi_lines if x.strip()])))

    # -----------------------------
    # 5) EXAME FÍSICO (major group in export)
    # -----------------------------
    exf_lines = []

    neuro_geral = _get("neuro_geral")
    if neuro_geral:
        exf_lines.append("# Exame Neurológico:\n" + neuro_geral)

    # força: prefer saved summary, else compute from current fields
    forca = _get("forca_resumo")
    if not forca:
        forca = _safe_call(build_forca_summary, "")
    if forca:
        exf_lines.append("" + forca)

    nm = _get("exame_neuromuscular_especifico")
    if nm:
        exf_lines.append("Exame neuromuscular específico:\n" + nm)

    pele = _get("pele_clinico_geral")
    if pele:
        exf_lines.append("Alterações de pele e exame clínico geral:\n" + pele)

    osteo = _get("osteo_dismorfismos")
    if osteo:
        exf_lines.append("Alterações osteoesqueléticas e dismorfismos:\n" + osteo)

    parts.append(_section("EXAME FÍSICO", "\n\n".join([x for x in exf_lines if x.strip()])))

    # -----------------------------
    # 6) EXAMES COMPLEMENTARES
    # -----------------------------
    ex_lines = []
    if _get("ex_cpk"):
        ex_lines.append(f"CPK: {_get('ex_cpk')}")
    if _get("ex_enmg"):
        ex_lines.append("Eletroneuromiografia:\n" + _get("ex_enmg"))
    if _get("ex_decremento_jitter"):
        ex_lines.append(f"Decremento / Jitter na EMG: {_get('ex_decremento_jitter')}")
    if _get("ex_achr"):
        ex_lines.append(f"Anti-receptor de acetilcolina: {_get('ex_achr')}")
    if _get("ex_outros_juncao"):
        ex_lines.append(f"Outros anticorpos de junção: {_get('ex_outros_juncao')}")
    if _get("ex_miosites"):
        ex_lines.append(f"Anticorpos para miosites: {_get('ex_miosites')}")
    if _get("ex_rm_muscular"):
        ex_lines.append("RM muscular:\n" + _get("ex_rm_muscular"))
    if _get("ex_biopsia_muscular"):
        ex_lines.append("Biópsia muscular:\n" + _get("ex_biopsia_muscular"))

    for lbl, k in [
        ("ECO", "ex_eco"),
        ("Holter", "ex_holter"),
        ("Espirometria", "ex_espirometria"),
        ("Polissonografia", "ex_polissonografia"),
        ("Outros exames", "ex_outros"),
    ]:
        if _get(k):
            ex_lines.append(f"{lbl}:\n{_get(k)}")

    parts.append(_section("EXAMES COMPLEMENTARES", "\n\n".join([x for x in ex_lines if x.strip()])))

    # -----------------------------
    # 7) TESTE GENÉTICO (separate section, mirrors UI)
    # -----------------------------
    tg_radio = _get("tg_radio")
    tg_lines = []
    if tg_radio:
        tg_lines.append(tg_radio)
        if tg_radio == "Teste genético realizado":
            if _get("tg_gene_sel"):
                tg_lines.append("Gene/resultado: " + _get("tg_gene_sel"))
            det = []
            if _get("tg_exame_nome"):
                det.append("Exame: " + _get("tg_exame_nome"))
            if _get("tg_data"):
                det.append("Data: " + _get("tg_data"))
            if _get("tg_local"):
                det.append("Local: " + _get("tg_local"))
            if det:
                tg_lines.append("Detalhes: " + " | ".join(det))
    parts.append(_section(">> Teste genético", "\n".join([x for x in tg_lines if x.strip()])))

    # -----------------------------
    # 8) DIAGNÓSTICO (topográfico + nosológico)
    # -----------------------------
    dx_lines = []

    topo_txt = _get("dx_topografico")
    if topo_txt:
        if topo_txt == "Outro":
            topo_txt = _get("dx_topografico_outro") or "Outro (não especificado)"
        dx_lines.append(f"Topográfico: {topo_txt}")

    noso = _get("dx_noso_sel")
    if noso:
        if noso == "Outros":
            noso = _get("dx_noso_outros") or "Outros (não especificado)"
        dx_lines.append(f"Nosológico: {noso}")

    parts.append(_section("DIAGNÓSTICO", "\n".join([x for x in dx_lines if x.strip()])))

    # -----------------------------
    # 9) IMPRESSÃO + CONDUTA
    # -----------------------------
    parts.append(_section("IMPRESSÃO", _get("impressao")))
    parts.append(_section("CONDUTA", _get("conduta")))

    cleaned = [p for p in parts if p.strip()]
    return "\n".join(cleaned).strip() + "\n"


# --- UI export ---
st.divider()
st.subheader("Exportar texto acima")

st.markdown(
    "<div style='background:#f5f5f5; padding:8px; border-radius:6px; font-size:14px;'>"
    "Funções a seguir disponíveis exclusivamente para fase de testes do template"
    "</div>",
    unsafe_allow_html=True,
)

c_exp1, c_exp2, c_exp3 = st.columns([1.2, 1.8, 1.2], vertical_alignment="center")
with c_exp1:
    if st.button("Exportar evolução", key="btn_export_evolucao"):
        st.session_state["export_mode"] = "evolucao"
with c_exp2:
    if st.button("Exportar histórico completo", key="btn_export_completo"):
        st.session_state["export_mode"] = "completo"
with c_exp3:
    if st.button("Trocar modalidade de exportação", key="btn_clear_export"):
        st.session_state["export_mode"] = None
        st.session_state["export_text"] = ""
        st.rerun()

mode = st.session_state.get("export_mode")
if mode == "evolucao":
    st.session_state["export_text"] = build_export_text(include_all=False)
elif mode == "completo":
    st.session_state["export_text"] = build_export_text(include_all=True)
else:
    st.session_state["export_text"] = ""

export_text = st.session_state.get("export_text", "")
if export_text:
    st.text_area(
        "Texto para copiar (Ctrl+A, Ctrl+C)",
        value=export_text,
        height=380,
        key="export_text_area",
    )
    st.download_button(
        "Baixar .txt",
        data=export_text.encode("utf-8"),
        file_name="template_neuromuscular_geral_export.txt",
        mime="text/plain",
        key="download_txt_export",
    )
