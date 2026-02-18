import re
import streamlit as st

st.set_page_config(page_title="Template nervo periférico", layout="wide")

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
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Template nervo periférico")
st.markdown(
    "<div style='font-size:27px; color:#666; margin-top:-0.5rem; margin-bottom:1rem;'>"
    "consulta inicial e de retorno"
    "</div>",
    unsafe_allow_html=True,
)

# =========================================================
# HELPERS (UI)
# =========================================================
def text_area_lines(label: str, lines: int, key: str, placeholder: str = ""):
    height_px = max(80, int(lines * 24 + 20))
    return st.text_area(label, key=key, height=height_px, placeholder=placeholder)

def inline_label_input(label_text: str, key: str, placeholder: str = ""):
    c_label, c_input, _fill = st.columns([3.2, 3.8, 10.0], vertical_alignment="center")
    with c_label:
        st.markdown(f'<div class="inline-label">{label_text}</div>', unsafe_allow_html=True)
    with c_input:
        return st.text_input("", key=key, placeholder=placeholder, label_visibility="collapsed")

def inline_label_display(label_text: str, value: str):
    c_label, c_box, _fill = st.columns([3.2, 3.0, 10.0], vertical_alignment="center")
    with c_label:
        st.markdown(f'<div class="inline-label">{label_text}</div>', unsafe_allow_html=True)
    with c_box:
        st.text_input("", value=value, disabled=True, label_visibility="collapsed")

def small_mrc_box(key: str):
    return st.text_input(
        "Valor (0–5)",
        key=key,
        placeholder="0-5",
        label_visibility="collapsed",
        max_chars=1,
    )

# =========================================================
# HELPERS (EXPORT/IMPORT)
# =========================================================
def _norm(text: str) -> str:
    return (text or "").replace("\r\n", "\n").replace("\r", "\n")

def _get(key: str, default: str = "") -> str:
    v = st.session_state.get(key, default)
    if v is None:
        return ""
    return str(v).strip()

def _bool_to_txt(v: bool) -> str:
    return "Sim" if v else "Não"

def _section(title: str, body: str) -> str:
    body = (body or "").strip()
    if not body:
        return ""
    return f"{title}\n{body}\n"

_SECTION_TITLES = [
    "IDENTIFICAÇÃO",
    "HISTÓRIA CLÍNICA",
    "ANTECEDENTES PATOLÓGICOS",
    "HISTÓRIA FAMILIAR",
    "MEDICAÇÕES MODIFICADORAS DE DOENÇA / IMUNOSSUPRESSORES",
    "EVOLUÇÃO CLÍNICA",
    "EXAME FÍSICO NEUROLÓGICO",
    "EXAMES COMPLEMENTARES",
    "IMPRESSÃO E DISCUSSÃO",
    "DIAGNÓSTICO / HIPÓTESE DIAGNÓSTICA",
    "CONDUTA",
]

def split_sections(text: str) -> dict[str, str]:
    text = _norm(text).strip()
    if not text:
        return {}
    patt = r"^(%s)\s*$" % "|".join(re.escape(t) for t in _SECTION_TITLES)
    matches = list(re.finditer(patt, text, flags=re.M))
    if not matches:
        return {}
    out: dict[str, str] = {}
    for i, m in enumerate(matches):
        title = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[title] = text[start:end].strip("\n").strip()
    return out

def _extract_line_value(body: str, prefix: str) -> str:
    body = _norm(body)
    for ln in body.split("\n"):
        if ln.strip().startswith(prefix):
            return ln.split(prefix, 1)[1].strip()
    return ""

def _extract_block(body: str, marker: str, end_markers: list[str]) -> str:
    body = _norm(body)
    esc_end = "|".join(re.escape(e) for e in end_markers) if end_markers else ""
    pattern = (
        re.escape(marker) + r"\n(.*?)(?=\n(?:" + esc_end + r")|\Z)"
        if esc_end
        else re.escape(marker) + r"\n(.*)\Z"
    )
    m = re.search(pattern, body, flags=re.S)
    return (m.group(1).strip() if m else "")

# =========================================================
# NIS (defs + helpers)
# =========================================================
NIS_MAX_WEAKNESS = 192
NIS_MAX_REFLEXES = 20
NIS_MAX_SENSATION = 32
NIS_MAX_TOTAL = 244

NIS_WEAKNESS_OPTIONS = [
    (0.00, "normal"),
    (1.00, "fraqueza 25%"),
    (2.00, "fraqueza 50%"),
    (3.00, "fraqueza 75%"),
    (3.25, "move apenas contra a gravidade"),
    (3.50, "move apenas com gravidade eliminada"),
    (3.75, "contração palpável/visível, sem movimento"),
    (4.00, "paralisia"),
]
NIS_WEAKNESS_VALUES = [v for v, _ in NIS_WEAKNESS_OPTIONS]
NIS_WEAKNESS_LABEL = {v: t for v, t in NIS_WEAKNESS_OPTIONS}

NIS_RS_OPTIONS = [
    (0, "normal"),
    (1, "diminuído"),
    (2, "ausente"),
]
NIS_RS_VALUES = [v for v, _ in NIS_RS_OPTIONS]
NIS_RS_LABEL = {v: t for v, t in NIS_RS_OPTIONS}

# Structure from the attached form
NIS_WEAKNESS_ITEMS = [
    ("Nervos cranianos", "III par (oculomotor)", "nis_cn_iii_r", "nis_cn_iii_l"),
    ("Nervos cranianos", "VI par (abducente)", "nis_cn_vi_r", "nis_cn_vi_l"),
    ("Nervos cranianos", "Fraqueza facial", "nis_cn_facial_r", "nis_cn_facial_l"),
    ("Nervos cranianos", "Fraqueza de palato", "nis_cn_palato_r", "nis_cn_palato_l"),
    ("Nervos cranianos", "Fraqueza de língua", "nis_cn_lingua_r", "nis_cn_lingua_l"),

    ("Fraqueza muscular", "Respiratório", "nis_mw_resp_r", "nis_mw_resp_l"),
    ("Fraqueza muscular", "Flexão cervical", "nis_mw_pescoco_r", "nis_mw_pescoco_l"),
    ("Fraqueza muscular", "Abdução do ombro", "nis_mw_ombro_r", "nis_mw_ombro_l"),
    ("Fraqueza muscular", "Flexão do cotovelo", "nis_mw_cotov_flex_r", "nis_mw_cotov_flex_l"),
    ("Fraqueza muscular", "Braquiorradial", "nis_mw_braq_r", "nis_mw_braq_l"),
    ("Fraqueza muscular", "Extensão do cotovelo", "nis_mw_cotov_ext_r", "nis_mw_cotov_ext_l"),
    ("Fraqueza muscular", "Flexão do punho", "nis_mw_punho_flex_r", "nis_mw_punho_flex_l"),
    ("Fraqueza muscular", "Extensão do punho", "nis_mw_punho_ext_r", "nis_mw_punho_ext_l"),
    ("Fraqueza muscular", "Flexão dos dedos", "nis_mw_dedos_flex_r", "nis_mw_dedos_flex_l"),
    ("Fraqueza muscular", "Abertura/abdução dos dedos", "nis_mw_dedos_abd_r", "nis_mw_dedos_abd_l"),
    ("Fraqueza muscular", "Abdução do polegar", "nis_mw_polegar_r", "nis_mw_polegar_l"),

    ("Membros inferiores", "Flexão do quadril", "nis_hip_flex_r", "nis_hip_flex_l"),
    ("Membros inferiores", "Extensão do quadril", "nis_hip_ext_r", "nis_hip_ext_l"),
    ("Membros inferiores", "Flexão do joelho", "nis_knee_flex_r", "nis_knee_flex_l"),
    ("Membros inferiores", "Extensão do joelho", "nis_knee_ext_r", "nis_knee_ext_l"),
    ("Membros inferiores", "Dorsiflexores do tornozelo", "nis_ankle_df_r", "nis_ankle_df_l"),
    ("Membros inferiores", "Flexores plantares do tornozelo", "nis_ankle_pf_r", "nis_ankle_pf_l"),
    ("Membros inferiores", "Extensor dos dedos do pé", "nis_toe_ext_r", "nis_toe_ext_l"),
    ("Membros inferiores", "Flexores dos dedos do pé", "nis_toe_flex_r", "nis_toe_flex_l"),
]

NIS_REFLEX_ITEMS = [
    ("Reflexos", "Bíceps braquial", "nis_ref_biceps_r", "nis_ref_biceps_l"),
    ("Reflexos", "Tríceps braquial", "nis_ref_triceps_r", "nis_ref_triceps_l"),
    ("Reflexos", "Braquiorradial", "nis_ref_braq_r", "nis_ref_braq_l"),
    ("Reflexos", "Quadríceps (patelar)", "nis_ref_patellar_r", "nis_ref_patellar_l"),
    ("Reflexos", "Tríceps sural (Aquileu)", "nis_ref_achilles_r", "nis_ref_achilles_l"),
]

NIS_SENS_FINGER_ITEMS = [
    ("Sensibilidade – dedo indicador", "Pressão tátil", "nis_sf_touch_r", "nis_sf_touch_l"),
    ("Sensibilidade – dedo indicador", "Picada (dor)", "nis_sf_pin_r", "nis_sf_pin_l"),
    ("Sensibilidade – dedo indicador", "Vibração", "nis_sf_vib_r", "nis_sf_vib_l"),
    ("Sensibilidade – dedo indicador", "Posição articular", "nis_sf_jps_r", "nis_sf_jps_l"),
]

NIS_SENS_TOE_ITEMS = [
    ("Sensibilidade – hálux", "Pressão tátil", "nis_st_touch_r", "nis_st_touch_l"),
    ("Sensibilidade – hálux", "Picada (dor)", "nis_st_pin_r", "nis_st_pin_l"),
    ("Sensibilidade – hálux", "Vibração", "nis_st_vib_r", "nis_st_vib_l"),
    ("Sensibilidade – hálux", "Posição articular", "nis_st_jps_r", "nis_st_jps_l"),
]

NIS_KEYS_WEAKNESS = [k for _, _, kr, kl in NIS_WEAKNESS_ITEMS for k in (kr, kl)]
NIS_KEYS_REFLEXES = [k for _, _, kr, kl in NIS_REFLEX_ITEMS for k in (kr, kl)]
NIS_KEYS_SENSATION = [k for _, _, kr, kl in (NIS_SENS_FINGER_ITEMS + NIS_SENS_TOE_ITEMS) for k in (kr, kl)]
NIS_ALL_KEYS = NIS_KEYS_WEAKNESS + NIS_KEYS_REFLEXES + NIS_KEYS_SENSATION

def _fmt_score(x: float) -> str:
    s = f"{float(x):.2f}".rstrip("0").rstrip(".")
    return s if s else "0"

def init_nis_state():
    st.session_state.setdefault("nis_open", False)
    st.session_state.setdefault("nis_total", "")

    for k in NIS_KEYS_WEAKNESS:
        if k not in st.session_state or st.session_state[k] not in NIS_WEAKNESS_VALUES:
            st.session_state[k] = 0.00

    for k in (NIS_KEYS_REFLEXES + NIS_KEYS_SENSATION):
        if k not in st.session_state or st.session_state[k] not in NIS_RS_VALUES:
            st.session_state[k] = 0

def compute_nis_components() -> tuple[float, float, float, float]:
    w = sum(float(st.session_state.get(k, 0.0)) for k in NIS_KEYS_WEAKNESS)
    r = sum(float(st.session_state.get(k, 0.0)) for k in NIS_KEYS_REFLEXES)
    s = sum(float(st.session_state.get(k, 0.0)) for k in NIS_KEYS_SENSATION)
    return w, r, s, (w + r + s)

def nis_row(label: str, key_r: str, key_l: str, *, kind: str):
    c0, c1, c2, _fill = st.columns([3.2, 1.8, 1.8, 10.0], vertical_alignment="center")
    with c0:
        st.markdown(f'<div class="inline-label">{label}</div>', unsafe_allow_html=True)
    with c1:
        if kind == "weakness":
            st.selectbox(
                "",
                options=NIS_WEAKNESS_VALUES,
                key=key_r,
                format_func=lambda v: NIS_WEAKNESS_LABEL[v],
                label_visibility="collapsed",
            )
        else:
            st.selectbox(
                "",
                options=NIS_RS_VALUES,
                key=key_r,
                format_func=lambda v: NIS_RS_LABEL[v],
                label_visibility="collapsed",
            )
    with c2:
        if kind == "weakness":
            st.selectbox(
                "",
                options=NIS_WEAKNESS_VALUES,
                key=key_l,
                format_func=lambda v: NIS_WEAKNESS_LABEL[v],
                label_visibility="collapsed",
            )
        else:
            st.selectbox(
                "",
                options=NIS_RS_VALUES,
                key=key_l,
                format_func=lambda v: NIS_RS_LABEL[v],
                label_visibility="collapsed",
            )

# =========================================================
# MRC - FULL LIST (for dialog + export/import)
# =========================================================
MRC_ALL_ITEMS_UPPER = [
    ("Abdução do ombro", "mrc_ombro_D", "mrc_ombro_E"),  # used in MRC-SS
    ("Adução do ombro", "mrc_ombro_add_D", "mrc_ombro_add_E"),
    ("Flexores do cotovelo", "mrc_cotovelo_D", "mrc_cotovelo_E"),  # used in MRC-SS
    ("Extensores do cotovelo", "mrc_cotovelo_ext_D", "mrc_cotovelo_ext_E"),
    ("Extensores de punho", "mrc_punho_D", "mrc_punho_E"),  # used in MRC-SS
    ("Flexores de punho", "mrc_punho_flex_D", "mrc_punho_flex_E"),
    ("Extensores de dedos", "mrc_dedos_ext_D", "mrc_dedos_ext_E"),
    ("Flexores profundos dos dedos", "mrc_dedos_flexprof_D", "mrc_dedos_flexprof_E"),
    ("Abdução dos dedos", "mrc_dedos_abd_D", "mrc_dedos_abd_E"),
    ("Oponência do polegar", "mrc_polegar_op_D", "mrc_polegar_op_E"),
    ("Abdutor do dedo mínimo", "mrc_minimo_abd_D", "mrc_minimo_abd_E"),
]

MRC_ALL_ITEMS_LOWER = [
    ("Flexores de quadril", "mrc_quadril_D", "mrc_quadril_E"),  # used in MRC-SS
    ("Extensores do quadril", "mrc_quadril_ext_D", "mrc_quadril_ext_E"),
    ("Abdutores do quadril", "mrc_quadril_abd_D", "mrc_quadril_abd_E"),
    ("Adutores do quadril", "mrc_quadril_add_D", "mrc_quadril_add_E"),
    ("Flexores do joelho", "mrc_joelho_flex_D", "mrc_joelho_flex_E"),
    ("Extensores do joelho", "mrc_joelho_D", "mrc_joelho_E"),  # used in MRC-SS
    ("Dorsiflexão do pé", "mrc_tornozelo_D", "mrc_tornozelo_E"),  # used in MRC-SS
    ("Flexão do pé", "mrc_pe_flex_D", "mrc_pe_flex_E"),
    ("Eversores do pé", "mrc_pe_evers_D", "mrc_pe_evers_E"),
    ("Inversores do pé", "mrc_pe_invers_D", "mrc_pe_invers_E"),
    ("Extensores do hálux", "mrc_halux_ext_D", "mrc_halux_ext_E"),
    ("Flexores do hálux", "mrc_halux_flex_D", "mrc_halux_flex_E"),
]

MRC_ALL_ITEMS = MRC_ALL_ITEMS_UPPER + MRC_ALL_ITEMS_LOWER
MRC_ALL_KEYS = [k for _, kd, ke in MRC_ALL_ITEMS for k in (kd, ke)]

def init_mrc_all_state():
    for k in MRC_ALL_KEYS:
        st.session_state.setdefault(k, "")

# =========================================================
# RESET / IMPORT
# =========================================================
def _reset_form_state():
    keys_to_clear = [
        # Identificação
        "id_texto",
        # História clínica
        "idade_inicio_sintomas", "historia_clinica_texto",
        # Antecedentes / familiar
        "antecedentes_patologicos_texto", "historia_familiar_texto",
        "hf_esporadico", "hf_familiar",
        # Medicações
        "tratamento_atual_radio", "trat_em_uso_tempo", "trat_sem_tempo",
        "meds_atual_previo_texto", "outros_meds_texto", "paciente_transplantado",
        # Evolução
        "controle_atual_radio", "evo_estavel_tempo", "evo_descricao_texto", "evo_reabilitacao_texto",
        "incat_total", "pnd_total", "mrc_ss_total", "nis_total", "outras_escalas_seguimento",
        # INCAT panel internal
        "incat_open", "incat_ul", "incat_ll", "radio_incat_ul", "radio_incat_ll",
        # NIS panel internal
        "nis_open",
        # Exame físico
        "exame_fisico_neuro_texto", "deformidades_osteo_texto",
        # Exames complementares
        "exames_enmg", "exames_liquor", "exames_usg_nervos", "exames_biopsia", "exames_demais",
        # Impressão / dx / conduta
        "impressao_discussao", "radio_dx_categoria",
        "dx_genetica_choice", "dx_genetica_outro",
        "dx_imuno_choice", "dx_imuno_outro",
        "dx_outras_adquiridas",
        "dx_outros_diagnosticos",
        "conduta",
        # Export/import UI states
        "export_mode", "export_text", "import_text",
    ]

    for k in keys_to_clear + MRC_ALL_KEYS + NIS_ALL_KEYS:
        st.session_state.pop(k, None)

def _parse_keyvals_block(block: str) -> dict[str, str]:
    out: dict[str, str] = {}
    if not block:
        return out
    for ln in _norm(block).split("\n"):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        # allow "key: val" or "key = val"
        m = re.match(r"^([A-Za-z0-9_]+)\s*[:=]\s*(.+?)\s*$", ln)
        if not m:
            continue
        out[m.group(1)] = m.group(2).strip()
    return out

def _import_from_full_export(text: str) -> tuple[bool, str]:
    secs = split_sections(text)
    if not secs:
        return False, "Não foi possível identificar as seções. Confirme se o texto foi exportado por 'Exportar histórico completo'."

    _reset_form_state()
    init_mrc_all_state()
    init_nis_state()

    # -----------------------------
    # IDENTIFICAÇÃO
    # -----------------------------
    ident = secs.get("IDENTIFICAÇÃO", "")
    if ident:
        st.session_state["id_texto"] = _norm(ident).strip()

    # -----------------------------
    # HISTÓRIA CLÍNICA
    # -----------------------------
    hc = secs.get("HISTÓRIA CLÍNICA", "")
    if hc:
        hc_n = _norm(hc)
        idade = _extract_line_value(hc_n, "Idade ao início dos sintomas:")
        if idade:
            st.session_state["idade_inicio_sintomas"] = idade
            lines = [ln for ln in hc_n.split("\n") if not ln.strip().startswith("Idade ao início dos sintomas:")]
            st.session_state["historia_clinica_texto"] = "\n".join(lines).strip()
        else:
            st.session_state["historia_clinica_texto"] = hc_n.strip()

    ap = secs.get("ANTECEDENTES PATOLÓGICOS", "")
    if ap:
        st.session_state["antecedentes_patologicos_texto"] = _norm(ap).strip()

    hf = secs.get("HISTÓRIA FAMILIAR", "")
    if hf:
        t = _norm(hf).strip()
        padrao = _extract_line_value(t, "Padrão de herança:")
        if padrao:
            st.session_state["hf_esporadico"] = "Esporádico" in padrao
            st.session_state["hf_familiar"] = "Familiar" in padrao
            lines = [ln for ln in t.split("\n") if not ln.strip().startswith("Padrão de herança:")]
            st.session_state["historia_familiar_texto"] = "\n".join(lines).strip()
        else:
            st.session_state["historia_familiar_texto"] = t

    meds = secs.get("MEDICAÇÕES MODIFICADORAS DE DOENÇA / IMUNOSSUPRESSORES", "")
    if meds:
        t = _norm(meds)

        trat = _extract_line_value(t, "Tratamento atual:")
        if trat in ["em uso de tratamento medicamentoso", "sem tratamento medicamentoso"]:
            st.session_state["tratamento_atual_radio"] = trat

        tempo = _extract_line_value(t, "Há quanto tempo:")
        if tempo:
            if trat == "em uso de tratamento medicamentoso":
                st.session_state["trat_em_uso_tempo"] = tempo
            elif trat == "sem tratamento medicamentoso":
                st.session_state["trat_sem_tempo"] = tempo

        st.session_state["meds_atual_previo_texto"] = _extract_block(
            t,
            "Medicamentos de uso atual ou prévio:",
            ["Outros medicamentos:", "Paciente transplantado hepático:"],
        )
        st.session_state["outros_meds_texto"] = _extract_block(
            t,
            "Outros medicamentos:",
            ["Paciente transplantado hepático:"],
        )

        transp = _extract_line_value(t, "Paciente transplantado hepático:")
        if transp:
            st.session_state["paciente_transplantado"] = transp.strip().lower().startswith("sim")

    # -----------------------------
    # EVOLUÇÃO
    # -----------------------------
    evo = secs.get("EVOLUÇÃO CLÍNICA", "")
    if evo:
        t = _norm(evo)

        ctrl = _extract_line_value(t, "Controle atual:")
        if ctrl in ["estável ou melhorando", "piorando"]:
            st.session_state["controle_atual_radio"] = ctrl

        tempo = _extract_line_value(t, "Há quanto tempo:")
        if tempo:
            st.session_state["evo_estavel_tempo"] = tempo

        desc = _extract_block(
            t,
            "Descrição da evolução:",
            ["Reabilitação:", "NIS:", "NIS_ITENS:", "Escala INCAT:", "MRC-SS:", "Outras escalas e métricas:"],
        )
        if desc:
            st.session_state["evo_descricao_texto"] = desc

        reab = _extract_block(
            t,
            "Reabilitação:",
            ["NIS:", "NIS_ITENS:", "Escala INCAT:", "MRC-SS:", "Outras escalas e métricas:"],
        )
        if reab:
            st.session_state["evo_reabilitacao_texto"] = reab

        nis = _extract_line_value(t, "NIS:")
        if nis:
            st.session_state["nis_total"] = nis

        nis_items_block = _extract_block(
            t,
            "NIS_ITENS:",
            ["Escala INCAT:", "MRC-SS:", "Outras escalas e métricas:"],
        )
        kv = _parse_keyvals_block(nis_items_block)
        for k, v in kv.items():
            if k in NIS_KEYS_WEAKNESS:
                try:
                    fv = float(str(v).replace(",", "."))
                    if fv in NIS_WEAKNESS_VALUES:
                        st.session_state[k] = fv
                except ValueError:
                    pass
            elif k in (NIS_KEYS_REFLEXES + NIS_KEYS_SENSATION):
                try:
                    iv = int(str(v).strip())
                    if iv in NIS_RS_VALUES:
                        st.session_state[k] = iv
                except ValueError:
                    pass

        # If items exist but summary missing, rebuild summary
        if (not st.session_state.get("nis_total")) and kv:
            w, r, s, tot = compute_nis_components()
            st.session_state["nis_total"] = (
                f"Fraqueza ({_fmt_score(w)}/{NIS_MAX_WEAKNESS}) + "
                f"Reflexos ({_fmt_score(r)}/{NIS_MAX_REFLEXES}) + "
                f"Sensibilidade ({_fmt_score(s)}/{NIS_MAX_SENSATION}) = "
                f"Total ({_fmt_score(tot)}/{NIS_MAX_TOTAL})"
            )

        incat = _extract_line_value(t, "Escala INCAT:")
        if incat:
            st.session_state["incat_total"] = incat

        mrcss = _extract_line_value(t, "MRC-SS:")
        if mrcss:
            st.session_state["mrc_ss_total"] = mrcss

        outras = _extract_block(t, "Outras escalas e métricas:", [])
        if outras:
            st.session_state["outras_escalas_seguimento"] = outras

    # -----------------------------
    # EXAME FÍSICO
    # -----------------------------
    exf = secs.get("EXAME FÍSICO NEUROLÓGICO", "")
    if exf:
        t = _norm(exf).strip()

        deform = _extract_block(t, "Deformidades osteoesqueléticas e exame clínico geral:", [])
        if deform:
            st.session_state["deformidades_osteo_texto"] = deform

        mrc_block = _extract_block(t, "MRC:", ["Deformidades osteoesqueléticas e exame clínico geral:"])

        idx_mrc = t.find("MRC:\n")
        idx_def = t.find("Deformidades osteoesqueléticas e exame clínico geral:\n")
        candidates = [i for i in [idx_mrc, idx_def] if i != -1]
        split_idx = min(candidates) if candidates else None

        if split_idx is not None:
            neuro_txt = t[:split_idx].strip()
            if neuro_txt:
                st.session_state["exame_fisico_neuro_texto"] = neuro_txt
        else:
            if t:
                st.session_state["exame_fisico_neuro_texto"] = t

        if mrc_block:
            map_lbl = {lbl: (kd, ke) for (lbl, kd, ke) in MRC_ALL_ITEMS}
            for ln in mrc_block.split("\n"):
                ln = ln.strip()
                if not ln:
                    continue
                mm = re.match(r"^(.*?):\s*D\s*([0-5\-]?)\s*/\s*E\s*([0-5\-]?)\s*$", ln)
                if not mm:
                    continue
                lbl = mm.group(1).strip()
                vd = mm.group(2).strip().replace("-", "")
                ve = mm.group(3).strip().replace("-", "")
                if lbl in map_lbl:
                    kd, ke = map_lbl[lbl]
                    st.session_state[kd] = vd
                    st.session_state[ke] = ve

        # recompute MRC-SS if possible
        mrc_keys = [
            "mrc_ombro_D", "mrc_ombro_E",
            "mrc_cotovelo_D", "mrc_cotovelo_E",
            "mrc_punho_D", "mrc_punho_E",
            "mrc_quadril_D", "mrc_quadril_E",
            "mrc_joelho_D", "mrc_joelho_E",
            "mrc_tornozelo_D", "mrc_tornozelo_E",
        ]
        ok_mrc, tot_mrc = compute_mrc_ss(mrc_keys)
        if ok_mrc and tot_mrc is not None:
            st.session_state["mrc_ss_total"] = str(tot_mrc)

    # -----------------------------
    # EXAMES COMPLEMENTARES
    # -----------------------------
    exc = secs.get("EXAMES COMPLEMENTARES", "")
    if exc:
        t = _norm(exc).strip()
        for prefix, key in [
            ("ENMG:", "exames_enmg"),
            ("Líquor:", "exames_liquor"),
            ("USG nervos:", "exames_usg_nervos"),
            ("Biópsia:", "exames_biopsia"),
            ("Demais exames:", "exames_demais"),
        ]:
            val = _extract_line_value(t, prefix)
            if val:
                st.session_state[key] = val

    imp = secs.get("IMPRESSÃO E DISCUSSÃO", "")
    if imp:
        st.session_state["impressao_discussao"] = _norm(imp).strip()

    dx = secs.get("DIAGNÓSTICO / HIPÓTESE DIAGNÓSTICA", "")
    if dx:
        t = [ln.strip() for ln in _norm(dx).split("\n") if ln.strip()]
        if t:
            cat = t[0]
            if cat in [
                "Neuropatia genética",
                "Neuropatia imunomediada",
                "Outras neuropatias adquiridas (nutricional, endocrinológica, infecciosa, tóxica, etc.)",
                "Outros diagnósticos (neurônio motor, junção e músculo)",
                "Diagnóstico indefinido",
            ]:
                st.session_state["radio_dx_categoria"] = cat

            for ln in t[1:]:
                if ln.startswith("Gene:"):
                    st.session_state["dx_genetica_choice"] = "Outro"
                    st.session_state["dx_genetica_outro"] = ln.split("Gene:", 1)[1].strip()
                if ln.startswith("Subtipo:"):
                    st.session_state["dx_imuno_choice"] = "Outro"
                    st.session_state["dx_imuno_outro"] = ln.split("Subtipo:", 1)[1].strip()
                if ln.startswith("Especifique:"):
                    extra = ln.split("Especifique:", 1)[1].strip()
                    if cat == "Outras neuropatias adquiridas (nutricional, endocrinológica, infecciosa, tóxica, etc.)":
                        st.session_state["dx_outras_adquiridas"] = extra
                    if cat == "Outros diagnósticos (neurônio motor, junção e músculo)":
                        st.session_state["dx_outros_diagnosticos"] = extra

    cnd = secs.get("CONDUTA", "")
    if cnd:
        st.session_state["conduta"] = _norm(cnd).strip()

    return True, "Importação concluída. Campos ausentes no texto permaneceram em branco."

# =========================================================
# IMPORT TRIGGER (runs before UI)
# =========================================================
if st.session_state.get("_do_import", False):
    st.session_state["_do_import"] = False
    ok, msg = _import_from_full_export(st.session_state.get("_import_raw", ""))
    st.session_state["_import_result"] = (ok, msg)
    st.rerun()

# =========================================================
# INIT STATES
# =========================================================
init_mrc_all_state()
init_nis_state()

# =========================================================
# MRC-SS (calc helper) uses the 12 classic keys
# =========================================================
mrc_keys = [
    "mrc_ombro_D", "mrc_ombro_E",
    "mrc_cotovelo_D", "mrc_cotovelo_E",
    "mrc_punho_D", "mrc_punho_E",
    "mrc_quadril_D", "mrc_quadril_E",
    "mrc_joelho_D", "mrc_joelho_E",
    "mrc_tornozelo_D", "mrc_tornozelo_E",
]

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
# IDENTIFICAÇÃO
# =========================================================
st.subheader("Identificação:")
_ = text_area_lines(label="", lines=1, key="id_texto", placeholder="")

# =========================================================
# 1) História clínica
# =========================================================
st.subheader("História clínica:")

_ = inline_label_input(
    "Idade ao início dos sintomas",
    key="idade_inicio_sintomas",
    placeholder="Ex.: 45",
)

_ = text_area_lines(
    label="",
    lines=10,
    key="historia_clinica_texto",
    placeholder="História da moléstia atual",
)

# =========================================================
# 2) Antecedentes Patológicos
# =========================================================
st.subheader("Antecedentes Patológicos")
_ = text_area_lines(
    label="",
    lines=4,
    key="antecedentes_patologicos_texto",
    placeholder="Comorbidades, vícios, exposições ocupacionais/ambientais, histórico de perda ponderal, etc.",
)

# =========================================================
# 3) História familiar
# =========================================================
st.subheader("História familiar")
_ = text_area_lines(
    label="",
    lines=4,
    key="historia_familiar_texto",
    placeholder="Familiares acometidos; estado de saúde de pais, irmãos e filhos; cidade de origem dos pais; consanguinidade; etc.",
)

c0, c1, c2, _hf_fill = st.columns([2.2, 1.4, 1.4, 10.0], vertical_alignment="center")
with c0:
    st.markdown('<div class="inline-label">Padrão de herança</div>', unsafe_allow_html=True)
with c1:
    esporadico = st.checkbox("Esporádico", key="hf_esporadico")
with c2:
    familiar = st.checkbox("Familiar", key="hf_familiar")

if esporadico and familiar:
    st.warning("Você marcou **Esporádico** e **Familiar** ao mesmo tempo. Se preferir, selecione apenas um.")

# =========================================================
# 4) Medicações
# =========================================================
st.subheader("Medicamentos")
st.markdown("**Tratamento atual:**")

tratamento_atual = st.radio(
    "",
    options=[
        "em uso de tratamento medicamentoso",
        "sem tratamento medicamentoso",
    ],
    index=None,
    key="tratamento_atual_radio",
)

if tratamento_atual == "em uso de tratamento medicamentoso":
    _ = inline_label_input("há quanto tempo", key="trat_em_uso_tempo", placeholder="Ex.: desde jan/2021")
elif tratamento_atual == "sem tratamento medicamentoso":
    _ = inline_label_input("há quanto tempo", key="trat_sem_tempo", placeholder="Ex.: desde jan/2021")

st.markdown("**Histórico de medicamentos modificadores de doença/imunossupressores**")
_ = text_area_lines(
    label="",
    lines=5,
    key="meds_atual_previo_texto",
    placeholder=(
        "Medicamento (uso atual ou prévio), data de início, data de término e motivo da suspensão.\n"
        "Ex.: Rituximabe 1g D1/D15, início 01/2024, suspensão 07/2024 por infecção"
    ),
)

st.markdown("**Outros medicamentos**")
_ = text_area_lines(label="", lines=5, key="outros_meds_texto", placeholder="")

st.checkbox("Paciente transplantado hepático", key="paciente_transplantado")

# =========================================================
# 5) Evolução clínica
# =========================================================
st.subheader("Evolução clínica")
st.markdown("**Controle atual:**")

controle_atual = st.radio(
    "",
    options=["estável ou melhorando", "piorando"],
    index=None,
    key="controle_atual_radio",
)

if controle_atual == "estável ou melhorando":
    _ = inline_label_input("há quanto tempo", key="evo_estavel_tempo", placeholder="Ex.: desde jan/2021")

st.markdown("**Descrição da evolução:**")
_ = text_area_lines(
    label="",
    lines=5,
    key="evo_descricao_texto",
    placeholder="Evolução dos sintomas motores, sensitivos e autonômicos. Adesão e efeitos colaterais dos medicamentos.",
)

st.markdown("**Reabilitação:**")
_ = text_area_lines(
    label="",
    lines=3,
    key="evo_reabilitacao_texto",
    placeholder="Fisioterapia e frequência. Outras modalidades de reabilitação.",
)

# =========================================================
# INCAT + PND + NIS + MRC-SS display
# =========================================================
def ll_to_pnd(ll_value: int) -> str:
    if ll_value == 0:
        return "PND I"
    if ll_value == 1:
        return "PND II"
    if ll_value == 2:
        return "PND IIIa"
    if ll_value in (3, 4):
        return "PND IIIb"
    return "PND IV"

st.session_state.setdefault("incat_open", False)
st.session_state.setdefault("incat_ul", 0)
st.session_state.setdefault("incat_ll", 0)
st.session_state.setdefault("incat_total", "")
st.session_state.setdefault("pnd_total", "")
st.session_state.setdefault("mrc_ss_total", "")

c_left, c_right = st.columns([2.2, 9.8], vertical_alignment="top")

with c_left:
    if st.button("Escala INCAT e PND", key="btn_open_incat"):
        st.session_state["incat_open"] = True

    if st.button("Escala NIS", key="btn_open_nis"):
        st.session_state["nis_open"] = True

with c_right:
    st.text_input(
        "Escala INCAT (MMSS + MMII)",
        value=st.session_state.get("incat_total") or "Calculada automaticamente",
        disabled=True,
    )
    st.text_input(
        "Escala PND",
        value=st.session_state.get("pnd_total") or "Calculada automaticamente",
        disabled=True,
    )

    nis_placeholder = (
        f"Calculada automaticamente (Fraqueza máx {NIS_MAX_WEAKNESS}; "
        f"Reflexos máx {NIS_MAX_REFLEXES}; Sensibilidade máx {NIS_MAX_SENSATION}; "
        f"Total máx {NIS_MAX_TOTAL})"
    )
    nis_display_value = (
        str(st.session_state.get("nis_total", "")).strip()
        if str(st.session_state.get("nis_total", "")).strip() != ""
        else nis_placeholder
    )
    st.text_input("Escala NIS", value=nis_display_value, disabled=True)

    mrc_display_value = (
        str(st.session_state.get("mrc_ss_total", "")).strip()
        if str(st.session_state.get("mrc_ss_total", "")).strip() != ""
        else "Calculada automaticamente, conforme exame físico"
    )
    st.text_input("Escala MRC-SS", value=mrc_display_value, disabled=True)

# --------------------------
# INCAT PANEL
# --------------------------
if st.session_state["incat_open"]:
    st.markdown("#### Escala INCAT")

    st.markdown("**Membros Superiores**")
    ul_options = {
        0: "0 – Sem problemas nos membros superiores.",
        1: (
            "1 – Sintomas em um ou ambos os braços, sem afetar a capacidade de realizar nenhuma das seguintes funções:\n"
            "• fechar todos os zíperes e botões\n"
            "• lavar ou pentear o cabelo\n"
            "• usar faca e garfo juntos\n"
            "• manusear moedas pequenas"
        ),
        2: "2 – Sintomas em um ou ambos os braços, afetando, mas não impedindo, nenhuma das funções acima.",
        3: "3 – Sintomas em um ou ambos os braços, impedindo uma ou duas das funções listadas acima.",
        4: "4 – Sintomas em um ou ambos os braços, impedindo três ou todas as funções listadas acima, mas ainda com alguns movimentos propositais possíveis.",
        5: "5 – Incapacidade de usar qualquer braço para qualquer movimento com finalidade.",
    }

    st.session_state["incat_ul"] = st.radio(
        "",
        options=list(ul_options.keys()),
        format_func=lambda k: ul_options[k],
        index=list(ul_options.keys()).index(st.session_state.get("incat_ul", 0)),
        key="radio_incat_ul",
    )

    st.markdown("---")
    st.markdown("**Marcha (Membros Inferiores)**")
    ll_options = {
        0: "0 – Marcha não afetada.",
        1: "1 – Marcha afetada, mas caminha independentemente em ambientes externos.",
        2: "2 – Geralmente necessita apoio unilateral (bengala, muleta simples ou apoio de um braço) para caminhar em ambientes externos.",
        3: "3 – Geralmente necessita apoio bilateral (duas bengalas, muletas, andador ou apoio de dois braços) para caminhar em ambientes externos.",
        4: "4 – Geralmente usa cadeira de rodas para se locomover em ambientes externos, mas consegue ficar em pé e andar alguns passos com ajuda.",
        5: "5 – Restrito à cadeira de rodas, incapaz de ficar em pé ou andar, ou apenas alguns passos mesmo com ajuda.",
    }

    st.session_state["incat_ll"] = st.radio(
        "",
        options=list(ll_options.keys()),
        format_func=lambda k: ll_options[k],
        index=list(ll_options.keys()).index(st.session_state.get("incat_ll", 0)),
        key="radio_incat_ll",
    )

    ul = int(st.session_state["incat_ul"])
    ll = int(st.session_state["incat_ll"])
    total = ul + ll
    pnd = ll_to_pnd(ll)

    st.markdown(f"**MMSS ({ul}) + MMII ({ll}) = {total}**")
    st.markdown(f"**PND: {pnd}**")

    b1, b2, _bfill = st.columns([1.4, 1.0, 10.0])
    with b1:
        if st.button("Salvar INCAT/PND", key="btn_save_incat", type="primary"):
            st.session_state["incat_total"] = f"MMSS ({ul}) + MMII ({ll}) = {total}"
            st.session_state["pnd_total"] = pnd
            st.session_state["incat_open"] = False
            st.rerun()
    with b2:
        if st.button("Cancelar", key="btn_cancel_incat"):
            st.session_state["incat_open"] = False
            st.rerun()

# --------------------------
# NIS PANEL
# --------------------------
if st.session_state.get("nis_open", False):
    st.markdown("#### Escala NIS")

    h0, h1, h2, _hf = st.columns([3.2, 1.8, 1.8, 10.0], vertical_alignment="center")
    with h0:
        st.markdown("**Item**")
    with h1:
        st.markdown("**Direito**")
    with h2:
        st.markdown("**Esquerdo**")

    def render_group(title: str, items: list[tuple[str, str, str, str]], kind: str):
        st.markdown(f"**{title}**")
        for _grp, lbl, kr, kl in items:
            nis_row(lbl, kr, kl, kind=kind)
        st.markdown("---")

    render_group("Nervos cranianos (fraqueza)", [x for x in NIS_WEAKNESS_ITEMS if x[0] == "Nervos cranianos"], kind="weakness")
    render_group("Fraqueza muscular", [x for x in NIS_WEAKNESS_ITEMS if x[0] == "Fraqueza muscular"], kind="weakness")
    render_group("Membros inferiores", [x for x in NIS_WEAKNESS_ITEMS if x[0] == "Membros inferiores"], kind="weakness")

    st.markdown("**Reflexos**")
    for _grp, lbl, kr, kl in NIS_REFLEX_ITEMS:
        nis_row(lbl, kr, kl, kind="rs")
    st.markdown("---")

    st.markdown("**Sensibilidade – dedo indicador**")
    for _grp, lbl, kr, kl in NIS_SENS_FINGER_ITEMS:
        nis_row(lbl, kr, kl, kind="rs")
    st.markdown("---")

    st.markdown("**Sensibilidade – hálux**")
    for _grp, lbl, kr, kl in NIS_SENS_TOE_ITEMS:
        nis_row(lbl, kr, kl, kind="rs")
    st.markdown("---")

    w, r, s, t = compute_nis_components()
    st.markdown(
        f"**Prévia:** Fraqueza **{_fmt_score(w)}/{NIS_MAX_WEAKNESS}** · "
        f"Reflexos **{_fmt_score(r)}/{NIS_MAX_REFLEXES}** · "
        f"Sensibilidade **{_fmt_score(s)}/{NIS_MAX_SENSATION}** · "
        f"Total **{_fmt_score(t)}/{NIS_MAX_TOTAL}**"
    )

    b1, b2, b3, _bfill = st.columns([1.4, 1.0, 1.2, 10.0], vertical_alignment="center")
    with b1:
        if st.button("Salvar NIS", key="btn_save_nis", type="primary"):
            w, r, s, t = compute_nis_components()
            st.session_state["nis_total"] = (
                f"Fraqueza ({_fmt_score(w)}/{NIS_MAX_WEAKNESS}) + "
                f"Reflexos ({_fmt_score(r)}/{NIS_MAX_REFLEXES}) + "
                f"Sensibilidade ({_fmt_score(s)}/{NIS_MAX_SENSATION}) = "
                f"Total ({_fmt_score(t)}/{NIS_MAX_TOTAL})"
            )
            st.session_state["nis_open"] = False
            st.rerun()
    with b2:
        if st.button("Cancelar", key="btn_cancel_nis"):
            st.session_state["nis_open"] = False
            st.rerun()
    with b3:
        if st.button("Limpar NIS", key="btn_clear_nis"):
            for k in NIS_KEYS_WEAKNESS:
                st.session_state[k] = 0.00
            for k in (NIS_KEYS_REFLEXES + NIS_KEYS_SENSATION):
                st.session_state[k] = 0
            st.session_state["nis_total"] = ""
            st.rerun()

st.markdown("**Outras escalas e métricas de seguimento**")
_ = text_area_lines(
    "",
    5,
    "outras_escalas_seguimento",
    placeholder="NIS, dinamometria, tempo de marcha, TUG, RODS, Norfolk, COMPASS-31, etc.",
)

# =========================================================
# 6) Exame físico neurológico
# =========================================================
st.subheader("Exame físico neurológico")

_ = text_area_lines(
    "",
    5,
    "exame_fisico_neuro_texto",
    placeholder="Força, tônus, reflexo, equilíbrio, sensibilidade, nervos cranianos, alterações autonômicas, cognição",
)

st.markdown("**MRC:**")

h0, h1, h2, _hf = st.columns([3.2, 1.4, 1.4, 10.0], vertical_alignment="center")
with h0:
    st.markdown("**Grupo muscular**")
with h1:
    st.markdown("**Direito**")
with h2:
    st.markdown("**Esquerdo**")

def mrc_row(label: str, key_d: str, key_e: str):
    c0, c1, c2, _fill = st.columns([3.2, 1.4, 1.4, 10.0], vertical_alignment="center")
    with c0:
        st.markdown(f'<div class="inline-label">{label}</div>', unsafe_allow_html=True)
    with c1:
        small_mrc_box(key_d)
    with c2:
        small_mrc_box(key_e)

# Keep current muscle groups in main page (same keys)
mrc_row("Abdução do ombro:", "mrc_ombro_D", "mrc_ombro_E")
mrc_row("Flexão do cotovelo:", "mrc_cotovelo_D", "mrc_cotovelo_E")
mrc_row("Extensão do punho:", "mrc_punho_D", "mrc_punho_E")
mrc_row("Flexão do quadril:", "mrc_quadril_D", "mrc_quadril_E")
mrc_row("Extensão do joelho:", "mrc_joelho_D", "mrc_joelho_E")
mrc_row("Dorsiflexão do tornozelo:", "mrc_tornozelo_D", "mrc_tornozelo_E")

complete, total = compute_mrc_ss(mrc_keys)

# =========================================================
# MRC FULL DIALOG (FIX: use temporary keys to avoid duplicates)
# =========================================================
dialog_decorator = getattr(st, "dialog", None) or getattr(st, "experimental_dialog")

def _dlg_key(k: str) -> str:
    return f"dlg_{k}"

def _mrc_all_row_dialog(label: str, main_key_d: str, main_key_e: str):
    """Row inside dialog using dlg_* keys (avoids duplicate keys with main page)."""
    c0, c1, c2, _fill = st.columns([3.2, 1.4, 1.4, 10.0], vertical_alignment="center")
    with c0:
        st.markdown(f'<div class="inline-label">{label}</div>', unsafe_allow_html=True)
    with c1:
        st.text_input(
            "Valor (0–5)",
            key=_dlg_key(main_key_d),
            placeholder="0-5",
            label_visibility="collapsed",
            max_chars=1,
        )
    with c2:
        st.text_input(
            "Valor (0–5)",
            key=_dlg_key(main_key_e),
            placeholder="0-5",
            label_visibility="collapsed",
            max_chars=1,
        )

@dialog_decorator("MRC – todos os músculos")
def mrc_all_dialog():
    st.markdown("**Membros superiores**")

    hh0, hh1, hh2, _ = st.columns([3.2, 1.4, 1.4, 10.0], vertical_alignment="center")
    with hh0:
        st.markdown("**Grupo muscular**")
    with hh1:
        st.markdown("**Direito**")
    with hh2:
        st.markdown("**Esquerdo**")

    for lbl, kd, ke in MRC_ALL_ITEMS_UPPER:
        _mrc_all_row_dialog(lbl + ":", kd, ke)

    st.markdown("---")
    st.markdown("**Membros inferiores**")

    hh0, hh1, hh2, _ = st.columns([3.2, 1.4, 1.4, 10.0], vertical_alignment="center")
    with hh0:
        st.markdown("**Grupo muscular**")
    with hh1:
        st.markdown("**Direito**")
    with hh2:
        st.markdown("**Esquerdo**")

    for lbl, kd, ke in MRC_ALL_ITEMS_LOWER:
        _mrc_all_row_dialog(lbl + ":", kd, ke)

    # Preview MRC-SS computed from dlg_* keys
    dlg_mrc_keys = [_dlg_key(k) for k in mrc_keys]  # mrc_keys = 12 classic keys used for MRC-SS
    ok_mrc, tot_mrc = compute_mrc_ss(dlg_mrc_keys)

    st.markdown("---")
    if ok_mrc and tot_mrc is not None:
        st.success(f"MRC-SS (prévia): {tot_mrc}")
    else:
        st.info("MRC-SS será calculado ao salvar, se os 12 campos do MRC-SS estiverem preenchidos (0–5).")

    b1, b2, b3 = st.columns([1.4, 1.0, 1.2], vertical_alignment="center")
    with b1:
        if st.button("Salvar", type="primary", key="btn_mrc_all_save"):
            # Copy dlg_* -> main keys
            for k in MRC_ALL_KEYS:
                st.session_state[k] = st.session_state.get(_dlg_key(k), "")

            ok2, tot2 = compute_mrc_ss(mrc_keys)
            if ok2 and tot2 is not None:
                st.session_state["mrc_ss_total"] = str(tot2)
            else:
                # keep as is (or clear) if incomplete
                st.session_state["mrc_ss_total"] = st.session_state.get("mrc_ss_total", "")

            # optional: clear dialog state
            for k in MRC_ALL_KEYS:
                st.session_state.pop(_dlg_key(k), None)

            st.rerun()
    with b2:
        if st.button("Cancelar", key="btn_mrc_all_cancel"):
            # optional: clear dialog state
            for k in MRC_ALL_KEYS:
                st.session_state.pop(_dlg_key(k), None)
            st.rerun()
    with b3:
        if st.button("Limpar todos (popup)", key="btn_mrc_all_clear"):
            # clear only dialog fields
            for k in MRC_ALL_KEYS:
                st.session_state[_dlg_key(k)] = ""
            st.rerun()

# =========================================================
# Button "Todos os músculos" (sync main -> dialog keys, then open dialog)
# =========================================================
def open_mrc_all_dialog():
    # sync current main values into dialog inputs
    for k in MRC_ALL_KEYS:
        st.session_state[_dlg_key(k)] = st.session_state.get(k, "")
    mrc_all_dialog()

# --- In your existing buttons row, replace the previous open call with this:
# with bcalc3:
#     if st.button("Todos os músculos", key="btn_open_mrc_all"):
#         open_mrc_all_dialog()


# =========================================================
# Exames complementares
# =========================================================
st.subheader("Exames complementares")
st.markdown("**ENMG**")
_ = text_area_lines("", 3, "exames_enmg", placeholder="")
st.markdown("**Líquor**")
_ = text_area_lines("", 3, "exames_liquor", placeholder="")
st.markdown("**USG nervos**")
_ = text_area_lines("", 3, "exames_usg_nervos", placeholder="")
st.markdown("**Biópsia**")
_ = text_area_lines("", 3, "exames_biopsia", placeholder="")
st.markdown("**Demais exames**")
_ = text_area_lines(
    "",
    3,
    "exames_demais",
    placeholder="Data e descrição dos demais exames relevantes (laboratoriais, RM, teste genético)",
)

# =========================================================
# Impressão e discussão
# =========================================================
st.subheader("Impressão e discussão:")
_ = text_area_lines(
    "",
    4,
    "impressao_discussao",
    placeholder="Impressão diagnóstica.\nControle atual da doença (estável, progredindo), baseado em quais métricas",
)

# =========================================================
# Diagnóstico/Hipótese diagnóstica
# =========================================================
st.subheader("Diagnóstico/Hipótese diagnóstica:")

dx_options = [
    "Neuropatia genética",
    "Neuropatia imunomediada",
    "Outras neuropatias adquiridas (nutricional, endocrinológica, infecciosa, tóxica, etc.)",
    "Outros diagnósticos (neurônio motor, junção e músculo)",
    "Diagnóstico indefinido",
]
dx_categoria = st.radio("", options=dx_options, key="radio_dx_categoria")

if dx_categoria == "Neuropatia genética":
    with st.expander("Detalhar (Neuropatia genética)", expanded=True):
        gen_options = ["TTR", "PPOX", "HMBS", "CPOX", "PMP22", "MPZ", "GJB1", "MFN2", "Outro"]
        dx_genetica_choice = st.radio("Gene:", options=gen_options, key="dx_genetica_choice")
        if dx_genetica_choice == "Outro":
            st.text_input("Especifique:", key="dx_genetica_outro", placeholder="Ex.: GDAP1, TTR, etc.")

if dx_categoria == "Neuropatia imunomediada":
    with st.expander("Detalhar (Neuropatia imunomediada)", expanded=True):
        imuno_options = ["CIDP", "Vasculite", "Ganglionopatia", "Guillain-Barré", "Neuropatia motora multifocal", "Outro"]
        dx_imuno_choice = st.radio("Especifique:", options=imuno_options, key="dx_imuno_choice")
        if dx_imuno_choice == "Outro":
            st.text_input("Especifique", key="dx_imuno_outro", placeholder="Ex.: anti-MAG, AMAN/AMSAN, paraneoplásica, etc.")

if dx_categoria == "Outras neuropatias adquiridas (nutricional, endocrinológica, infecciosa, tóxica, etc.)":
    st.text_input(
        "Especifique:",
        key="dx_outras_adquiridas",
        placeholder="Ex.: neuropatia alcoólica / hipotireoidismo / B12 / HIV / quimioterapia / etc.",
    )

if dx_categoria == "Outros diagnósticos (neurônio motor, junção e músculo)":
    st.text_input(
        "Especifique:",
        key="dx_outros_diagnosticos",
        placeholder="Ex.: ELA / Miastenia / Miopatia / Doença do neurônio motor / etc.",
    )

summary = dx_categoria
if dx_categoria == "Neuropatia genética":
    choice = st.session_state.get("dx_genetica_choice", "")
    if choice == "Outro":
        extra = st.session_state.get("dx_genetica_outro", "").strip()
        summary += f" | Gene: {extra}" if extra else " | Gene: outro (não especificado)"
    elif choice:
        summary += f" | Gene: {choice}"

if dx_categoria == "Neuropatia imunomediada":
    choice = st.session_state.get("dx_imuno_choice", "")
    if choice == "Outro":
        extra = st.session_state.get("dx_imuno_outro", "").strip()
        summary += f" | Subtipo: {extra}" if extra else " | Subtipo: outro (não especificado)"
    elif choice:
        summary += f" | Subtipo: {choice}"

if dx_categoria == "Outras neuropatias adquiridas (nutricional, endocrinológica, infecciosa, tóxica, etc.)":
    extra = st.session_state.get("dx_outras_adquiridas", "").strip()
    if extra:
        summary += f" | Especifique: {extra}"

if dx_categoria == "Outros diagnósticos (neurônio motor, junção e músculo)":
    extra = st.session_state.get("dx_outros_diagnosticos", "").strip()
    if extra:
        summary += f" | Especifique: {extra}"

st.caption(summary)

# =========================================================
# Conduta
# =========================================================
st.subheader("Conduta:")
_ = text_area_lines("", 4, "conduta", placeholder="")

# =========================================================
# EXPORT
# =========================================================
def _has_any_nis_data() -> bool:
    # any non-zero / non-default suggests the scale was actually filled
    for k in NIS_KEYS_WEAKNESS:
        if float(st.session_state.get(k, 0.0)) != 0.0:
            return True
    for k in (NIS_KEYS_REFLEXES + NIS_KEYS_SENSATION):
        if int(st.session_state.get(k, 0)) != 0:
            return True
    return False

def build_export_text(include_all: bool) -> str:
    parts = []

    if include_all:
        parts.append(_section("IDENTIFICAÇÃO", _get("id_texto")))

        parts.append(_section(
            "HISTÓRIA CLÍNICA",
            f"Idade ao início dos sintomas: {_get('idade_inicio_sintomas')}\n{_get('historia_clinica_texto')}"
        ))
        parts.append(_section("ANTECEDENTES PATOLÓGICOS", _get("antecedentes_patologicos_texto")))

        hf_txt = _get("historia_familiar_texto")
        padrao = []
        if st.session_state.get("hf_esporadico"):
            padrao.append("Esporádico")
        if st.session_state.get("hf_familiar"):
            padrao.append("Familiar")
        padrao_txt = ", ".join(padrao) if padrao else ""
        if padrao_txt:
            hf_txt = (hf_txt + "\n" if hf_txt else "") + f"Padrão de herança: {padrao_txt}"
        parts.append(_section("HISTÓRIA FAMILIAR", hf_txt))

    # Medicações
    trat = _get("tratamento_atual_radio")
    trat_line = f"Tratamento atual: {trat}" if trat else ""
    tempo = ""
    if trat == "em uso de tratamento medicamentoso":
        tempo = _get("trat_em_uso_tempo")
    elif trat == "sem tratamento medicamentoso":
        tempo = _get("trat_sem_tempo")
    if tempo:
        trat_line = (trat_line + "\n" if trat_line else "") + f"Há quanto tempo: {tempo}"

    meds_block = "\n".join([x for x in [
        trat_line,
        "Medicamentos de uso atual ou prévio:\n" + _get("meds_atual_previo_texto") if _get("meds_atual_previo_texto") else "",
        "Outros medicamentos:\n" + _get("outros_meds_texto") if _get("outros_meds_texto") else "",
        "Paciente transplantado hepático: " + _bool_to_txt(bool(st.session_state.get("paciente_transplantado")))
        if "paciente_transplantado" in st.session_state else "",
    ] if x.strip()])
    parts.append(_section("MEDICAÇÕES MODIFICADORAS DE DOENÇA / IMUNOSSUPRESSORES", meds_block))

    # Evolução
    controle = _get("controle_atual_radio")
    evo_lines = []
    if controle:
        evo_lines.append(f"Controle atual: {controle}")
    if controle == "estável ou melhorando":
        t = _get("evo_estavel_tempo")
        if t:
            evo_lines.append(f"Há quanto tempo: {t}")

    desc = _get("evo_descricao_texto")
    if desc:
        evo_lines.append("Descrição da evolução:\n" + desc)

    reab = _get("evo_reabilitacao_texto")
    if reab:
        evo_lines.append("Reabilitação:\n" + reab)

    # NIS summary (recompute if necessary)
    nis_any = _has_any_nis_data()
    nis_sum = _get("nis_total")
    if nis_any and not nis_sum:
        w, r, s, tot = compute_nis_components()
        nis_sum = (
            f"Fraqueza ({_fmt_score(w)}/{NIS_MAX_WEAKNESS}) + "
            f"Reflexos ({_fmt_score(r)}/{NIS_MAX_REFLEXES}) + "
            f"Sensibilidade ({_fmt_score(s)}/{NIS_MAX_SENSATION}) = "
            f"Total ({_fmt_score(tot)}/{NIS_MAX_TOTAL})"
        )

    if nis_sum:
        evo_lines.append(f"NIS: {nis_sum}")

    # ✅ Save individual values for full reimport later
    if nis_any:
        evo_lines.append("NIS_ITENS:")
        for k in NIS_KEYS_WEAKNESS:
            evo_lines.append(f"{k}: {_fmt_score(float(st.session_state.get(k, 0.0)))}")
        for k in NIS_KEYS_REFLEXES:
            evo_lines.append(f"{k}: {int(st.session_state.get(k, 0))}")
        for k in NIS_KEYS_SENSATION:
            evo_lines.append(f"{k}: {int(st.session_state.get(k, 0))}")

    incat = _get("incat_total")
    if incat:
        evo_lines.append(f"Escala INCAT: {incat}")

    mrc_ss = _get("mrc_ss_total")
    if mrc_ss:
        evo_lines.append(f"MRC-SS: {mrc_ss}")

    outras = _get("outras_escalas_seguimento")
    if outras:
        evo_lines.append("Outras escalas e métricas:\n" + outras)

    parts.append(_section("EVOLUÇÃO CLÍNICA", "\n".join(evo_lines)))

    # Exame físico
    exame_neuro = _get("exame_fisico_neuro_texto")

    # ✅ Export FULL MRC (all muscles) so it can be fully reimported
    mrc_lines = []
    for label, kd, ke in MRC_ALL_ITEMS:
        vd = _get(kd) or "-"
        ve = _get(ke) or "-"
        mrc_lines.append(f"{label}: D {vd} / E {ve}")
    mrc_block = "MRC:\n" + "\n".join(mrc_lines)

    deform = _get("deformidades_osteo_texto")

    exame_block_parts = []
    if exame_neuro:
        exame_block_parts.append(exame_neuro)
    if mrc_block:
        exame_block_parts.append(mrc_block)
    if deform:
        exame_block_parts.append("Deformidades osteoesqueléticas e exame clínico geral:\n" + deform)

    parts.append(_section("EXAME FÍSICO NEUROLÓGICO", "\n\n".join(exame_block_parts)))

    # Exames complementares
    exames_lines = []
    if _get("exames_enmg"):
        exames_lines.append("ENMG: " + _get("exames_enmg"))
    if _get("exames_liquor"):
        exames_lines.append("Líquor: " + _get("exames_liquor"))
    if _get("exames_usg_nervos"):
        exames_lines.append("USG nervos: " + _get("exames_usg_nervos"))
    if _get("exames_biopsia"):
        exames_lines.append("Biópsia: " + _get("exames_biopsia"))
    if _get("exames_demais"):
        exames_lines.append("Demais exames: " + _get("exames_demais"))
    parts.append(_section("EXAMES COMPLEMENTARES", "\n".join(exames_lines)))

    parts.append(_section("IMPRESSÃO E DISCUSSÃO", _get("impressao_discussao")))

    # Diagnóstico
    dx = _get("radio_dx_categoria")
    dx_lines = []
    if dx:
        dx_lines.append(dx)

    if dx == "Neuropatia genética":
        gene = _get("dx_genetica_choice")
        if gene == "Outro":
            gene = _get("dx_genetica_outro") or "Outro (não especificado)"
        if gene:
            dx_lines.append(f"Gene: {gene}")

    if dx == "Neuropatia imunomediada":
        sub = _get("dx_imuno_choice")
        if sub == "Outro":
            sub = _get("dx_imuno_outro") or "Outro (não especificado)"
        if sub:
            dx_lines.append(f"Subtipo: {sub}")

    if dx == "Outras neuropatias adquiridas (nutricional, endocrinológica, infecciosa, tóxica, etc.)":
        extra = _get("dx_outras_adquiridas")
        if extra:
            dx_lines.append(f"Especifique: {extra}")

    if dx == "Outros diagnósticos (neurônio motor, junção e músculo)":
        extra = _get("dx_outros_diagnosticos")
        if extra:
            dx_lines.append(f"Especifique: {extra}")

    parts.append(_section("DIAGNÓSTICO / HIPÓTESE DIAGNÓSTICA", "\n".join(dx_lines)))
    parts.append(_section("CONDUTA", _get("conduta")))

    cleaned = [p for p in parts if p.strip()]
    return "\n".join(cleaned).strip() + "\n"

# =========================================================
# SEÇÃO: EXPORTAR / IMPORTAR (TESTES)
# =========================================================
st.divider()
st.subheader("Exportar texto acima")

st.markdown(
    "<div style='background:#f5f5f5; padding:8px; border-radius:6px; font-size:14px;'>"
    "Funções a seguir disponíveis exclusivamente para fase de testes do template"
    "</div>",
    unsafe_allow_html=True,
)

if "export_mode" not in st.session_state:
    st.session_state["export_mode"] = None  # "evolucao" | "completo" | None

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
    export_text = build_export_text(include_all=False)
    st.session_state["export_text"] = export_text
elif mode == "completo":
    export_text = build_export_text(include_all=True)
    st.session_state["export_text"] = export_text
else:
    export_text = ""

if export_text:
    st.text_area(
        "Texto para copiar (Ctrl+A, Ctrl+C)",
        value=export_text,
        height=320,
        key="export_text_area",
    )
    st.download_button(
        "Baixar .txt",
        data=export_text.encode("utf-8"),
        file_name="template_nervo_export.txt",
        mime="text/plain",
        key="download_txt_export",
    )

# =========================================================
# IMPORTAR PARA O FORMULÁRIO
# =========================================================
st.markdown("---")
st.subheader("Importar para o formulário")

st.markdown(
    "<div style='background:#f5f5f5; padding:8px; border-radius:6px; font-size:14px;'>"
    "A importação funciona apenas para texto no formato exato gerado por <strong>Exportar histórico completo</strong>."
    "</div>",
    unsafe_allow_html=True,
)

st.text_area(
    "Cole aqui o texto exportado por 'Exportar histórico completo'",
    key="import_text",
    height=160,
    placeholder="Cole aqui o texto exportado por 'Exportar histórico completo'",
)

c_i1, c_i2, _ = st.columns([1.8, 1.4, 10.0], vertical_alignment="center")

def _request_import():
    st.session_state["_import_raw"] = st.session_state.get("import_text", "")
    st.session_state["_do_import"] = True

with c_i1:
    st.button(
        "Importar para o formulário",
        key="btn_import",
        on_click=_request_import,
        type="primary",
    )

with c_i2:
    def clear_import():
        st.session_state["import_text"] = ""
    st.button("Limpar texto colado", key="btn_clear_import", on_click=clear_import)

res = st.session_state.get("_import_result")
if res:
    ok, msg = res
    if ok:
        st.success(msg)
    else:
        st.error(msg)
    st.session_state.pop("_import_result", None)
