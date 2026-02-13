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
    esc_end = "|".join(re.escape(e) for e in end_markers)
    pattern = re.escape(marker) + r"\n(.*?)(?=\n(?:" + esc_end + r")|\Z)"
    m = re.search(pattern, body, flags=re.S)
    return (m.group(1).strip() if m else "")

def _reset_form_state():
    keys_to_clear = [
        # História clínica
        "idade_inicio_sintomas", "historia_clinica_texto",
        # Antecedentes / familiar
        "antecedentes_patologicos_texto", "historia_familiar_texto",
        "hf_esporadico", "hf_familiar",
        # Medicações
        "tratamento_atual_radio", "trat_em_uso_tempo", "trat_sem_tempo",
        "meds_atual_previo_texto", "outros_meds_texto", "paciente_transplantado",
        # Evolução
        "controle_atual_radio", "evo_estavel_tempo", "evo_descricao_texto",
        "incat_total", "pnd_total", "mrc_ss_total", "outras_escalas_seguimento",
        # INCAT panel internal
        "incat_open", "incat_ul", "incat_ll", "radio_incat_ul", "radio_incat_ll",
        # Exame físico
        "exame_fisico_neuro_texto", "deformidades_osteo_texto",
        # Exames complementares
        "exames_enmg", "exames_liquor", "exames_usg_nervos", "exames_biopsia", "exames_demais",
        # Impressão / dx / conduta
        "impressao_discussao", "radio_dx_categoria",
        "dx_genetica_choice", "dx_genetica_outro",
        "dx_imuno_choice", "dx_imuno_outro",
        "conduta",
        # Export/import UI states
        "export_mode", "export_text", "import_text",
    ]

    mrc_keys_local = [
        "mrc_ombro_D", "mrc_ombro_E",
        "mrc_cotovelo_D", "mrc_cotovelo_E",
        "mrc_punho_D", "mrc_punho_E",
        "mrc_quadril_D", "mrc_quadril_E",
        "mrc_joelho_D", "mrc_joelho_E",
        "mrc_tornozelo_D", "mrc_tornozelo_E",
    ]

    for k in keys_to_clear + mrc_keys_local:
        st.session_state.pop(k, None)

def _import_from_full_export(text: str) -> tuple[bool, str]:
    """
    Importa um texto colado cuja formatação esteja no padrão do
    'Exportar histórico completo'. Campos ausentes -> ficam em branco.
    """
    secs = split_sections(text)
    if not secs:
        return False, "Não foi possível identificar as seções. Confirme se o texto foi exportado por 'Exportar histórico completo'."

    _reset_form_state()

    # -----------------------------
    # HISTÓRIA CLÍNICA
    # -----------------------------
    hc = secs.get("HISTÓRIA CLÍNICA", "")
    if hc:
        hc_n = _norm(hc)
        # primeira linha: "Idade ao início dos sintomas: X"
        idade = _extract_line_value(hc_n, "Idade ao início dos sintomas:")
        if idade:
            st.session_state["idade_inicio_sintomas"] = idade
            # remove a linha do corpo
            lines = [ln for ln in hc_n.split("\n") if not ln.strip().startswith("Idade ao início dos sintomas:")]
            st.session_state["historia_clinica_texto"] = "\n".join(lines).strip()
        else:
            st.session_state["historia_clinica_texto"] = hc_n.strip()

    # -----------------------------
    # ANTECEDENTES PATOLÓGICOS
    # -----------------------------
    ap = secs.get("ANTECEDENTES PATOLÓGICOS", "")
    if ap:
        st.session_state["antecedentes_patologicos_texto"] = _norm(ap).strip()

    # -----------------------------
    # HISTÓRIA FAMILIAR
    # -----------------------------
    hf = secs.get("HISTÓRIA FAMILIAR", "")
    if hf:
        t = _norm(hf).strip()
        padrao = _extract_line_value(t, "Padrão de herança:")
        if padrao:
            st.session_state["hf_esporadico"] = "Esporádico" in padrao
            st.session_state["hf_familiar"] = "Familiar" in padrao
            # remove linha do padrão do texto
            lines = [ln for ln in t.split("\n") if not ln.strip().startswith("Padrão de herança:")]
            st.session_state["historia_familiar_texto"] = "\n".join(lines).strip()
        else:
            st.session_state["historia_familiar_texto"] = t

    # -----------------------------
    # MEDICAÇÕES
    # -----------------------------
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

        # Blocos (com ou sem conteúdo)
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
    # EVOLUÇÃO CLÍNICA
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

        # descrição e outras escalas como blocos
        desc = _extract_block(
            t,
            "Descrição da evolução:",
            ["Escala INCAT:", "MRC-SS:", "Outras escalas e métricas:"],
        )
        if desc:
            st.session_state["evo_descricao_texto"] = desc

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
    # EXAME FÍSICO NEUROLÓGICO
    # -----------------------------
    exf = secs.get("EXAME FÍSICO NEUROLÓGICO", "")
    if exf:
        t = _norm(exf).strip()

        # Deformidades (se existir)
        deform = _extract_block(t, "Deformidades osteoesqueléticas e exame clínico geral:", [])
        if deform:
            st.session_state["deformidades_osteo_texto"] = deform

        # MRC block
        mrc_block = _extract_block(t, "MRC:", ["Deformidades osteoesqueléticas e exame clínico geral:"])
        # Texto neurológico = tudo antes de "MRC:" (ou antes de deformidades, se não houver MRC)
        split_idx = None
        idx_mrc = t.find("MRC:\n")
        idx_def = t.find("Deformidades osteoesqueléticas e exame clínico geral:\n")

        candidates = [i for i in [idx_mrc, idx_def] if i != -1]
        if candidates:
            split_idx = min(candidates)

        if split_idx is not None:
            neuro_txt = t[:split_idx].strip()
            if neuro_txt:
                st.session_state["exame_fisico_neuro_texto"] = neuro_txt
        else:
            # sem marcadores
            if t:
                st.session_state["exame_fisico_neuro_texto"] = t

        # Parse MRC lines -> preenche os campos
        if mrc_block:
            map_lbl = {
                "Abdução do ombro": ("mrc_ombro_D", "mrc_ombro_E"),
                "Flexão do cotovelo": ("mrc_cotovelo_D", "mrc_cotovelo_E"),
                "Extensão do punho": ("mrc_punho_D", "mrc_punho_E"),
                "Flexão do quadril": ("mrc_quadril_D", "mrc_quadril_E"),
                "Extensão do joelho": ("mrc_joelho_D", "mrc_joelho_E"),
                "Dorsiflexão do tornozelo": ("mrc_tornozelo_D", "mrc_tornozelo_E"),
            }
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

    # -----------------------------
    # EXAMES COMPLEMENTARES
    # -----------------------------
    exc = secs.get("EXAMES COMPLEMENTARES", "")
    if exc:
        t = _norm(exc).strip()
        # Linhas "ENMG: ..." etc
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

    # -----------------------------
    # IMPRESSÃO
    # -----------------------------
    imp = secs.get("IMPRESSÃO E DISCUSSÃO", "")
    if imp:
        st.session_state["impressao_discussao"] = _norm(imp).strip()

    # -----------------------------
    # DIAGNÓSTICO
    # -----------------------------
    dx = secs.get("DIAGNÓSTICO / HIPÓTESE DIAGNÓSTICA", "")
    if dx:
        t = [ln.strip() for ln in _norm(dx).split("\n") if ln.strip()]
        if t:
            cat = t[0]
            # precisa existir nas opções do radio
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

    # -----------------------------
    # CONDUTA
    # -----------------------------
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
# MRC-SS (calc helper)
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
    """
    Returns (is_complete_and_valid, total_or_None)
    Valid only if ALL fields are filled with integers 0–5.
    """
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
# 4) Medicações modificadoras de doença/Imunossupressores
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
    _ = inline_label_input(
        "há quanto tempo",
        key="trat_em_uso_tempo",
        placeholder="Ex.: desde jan/2021",
    )
elif tratamento_atual == "sem tratamento medicamentoso":
    _ = inline_label_input(
        "há quanto tempo",
        key="trat_sem_tempo",
        placeholder="Ex.: desde jan/2021",
    )

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
_ = text_area_lines(
    label="",
    lines=5,
    key="outros_meds_texto",
    placeholder="",
)

st.checkbox("Paciente transplantado hepático", key="paciente_transplantado")

# =========================================================
# 5) Evolução clínica
# =========================================================
st.subheader("Evolução clínica")
st.markdown("**Controle atual:**")

controle_atual = st.radio(
    "",
    options=[
        "estável ou melhorando",
        "piorando",
    ],
    index=None,
    key="controle_atual_radio",
)

if controle_atual == "estável ou melhorando":
    _ = inline_label_input(
        "há quanto tempo",
        key="evo_estavel_tempo",
        placeholder="Ex.: desde jan/2021",
    )

st.markdown("**Descrição da evolução:**")
_ = text_area_lines(
    label="",
    lines=5,
    key="evo_descricao_texto",
    placeholder="",
)

# =========================================================
# INCAT + PND + MRC-SS display
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

# state init
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

    mrc_display_value = (
        str(st.session_state.get("mrc_ss_total", "")).strip()
        if str(st.session_state.get("mrc_ss_total", "")).strip() != ""
        else "Calculada automaticamente, conforme exame físico"
    )
    st.text_input(
        "Escala MRC-SS",
        value=mrc_display_value,
        disabled=True,
    )

# Panel INCAT/PND
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

    if st.session_state["incat_ul"] not in ul_options:
        st.session_state["incat_ul"] = 0

    st.session_state["incat_ul"] = st.radio(
        "",
        options=list(ul_options.keys()),
        format_func=lambda k: ul_options[k],
        index=list(ul_options.keys()).index(st.session_state["incat_ul"]),
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

    if st.session_state["incat_ll"] not in ll_options:
        st.session_state["incat_ll"] = 0

    st.session_state["incat_ll"] = st.radio(
        "",
        options=list(ll_options.keys()),
        format_func=lambda k: ll_options[k],
        index=list(ll_options.keys()).index(st.session_state["incat_ll"]),
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

st.markdown("**Outras escalas e métricas de seguimento**")
_ = text_area_lines(
    label="",
    lines=5,
    key="outras_escalas_seguimento",
    placeholder="NIS, dinamometria, tempo de marcha, TUG, etc.",
)

# =========================================================
# 6) Exame físico neurológico
# =========================================================
st.subheader("Exame físico neurológico")

_ = text_area_lines(
    label="",
    lines=5,
    key="exame_fisico_neuro_texto",
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

mrc_row("Abdução do ombro:", "mrc_ombro_D", "mrc_ombro_E")
mrc_row("Flexão do cotovelo:", "mrc_cotovelo_D", "mrc_cotovelo_E")
mrc_row("Extensão do punho:", "mrc_punho_D", "mrc_punho_E")
mrc_row("Flexão do quadril:", "mrc_quadril_D", "mrc_quadril_E")
mrc_row("Extensão do joelho:", "mrc_joelho_D", "mrc_joelho_E")
mrc_row("Dorsiflexão do tornozelo:", "mrc_tornozelo_D", "mrc_tornozelo_E")

complete, total = compute_mrc_ss(mrc_keys)

bcalc1, bcalc2, _fill = st.columns([2.2, 2.2, 10.0], vertical_alignment="center")
with bcalc1:
    if complete:
        if st.button("Calcular MRC-SS", key="btn_calc_mrcss", type="primary"):
            st.session_state["mrc_ss_total"] = total
            st.success(f"MRC-SS calculado: {total}")
            st.rerun()
    else:
        st.caption("Preencha todos os 12 campos (0–5) para habilitar o cálculo do MRC-SS.")
with bcalc2:
    if st.button("Limpar MRC-SS", key="btn_clear_mrcss"):
        st.session_state["mrc_ss_total"] = ""
        st.rerun()

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

st.caption(summary)

# =========================================================
# Conduta
# =========================================================
st.subheader("Conduta:")
_ = text_area_lines("", 4, "conduta", placeholder="")

# =========================================================
# EXPORT
# =========================================================
def build_export_text(include_all: bool) -> str:
    parts = []

    if include_all:
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
    mrc_lines = []
    mrc_map = [
        ("Abdução do ombro", "mrc_ombro_D", "mrc_ombro_E"),
        ("Flexão do cotovelo", "mrc_cotovelo_D", "mrc_cotovelo_E"),
        ("Extensão do punho", "mrc_punho_D", "mrc_punho_E"),
        ("Flexão do quadril", "mrc_quadril_D", "mrc_quadril_E"),
        ("Extensão do joelho", "mrc_joelho_D", "mrc_joelho_E"),
        ("Dorsiflexão do tornozelo", "mrc_tornozelo_D", "mrc_tornozelo_E"),
    ]
    for label, kd, ke in mrc_map:
        vd = _get(kd)
        ve = _get(ke)
        if vd or ve:
            mrc_lines.append(f"{label}: D {vd or '-'} / E {ve or '-'}")
    mrc_block = "MRC:\n" + "\n".join(mrc_lines) if mrc_lines else ""

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

    # Impressão e discussão
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

    parts.append(_section("DIAGNÓSTICO / HIPÓTESE DIAGNÓSTICA", "\n".join(dx_lines)))

    # Conduta
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
# IMPORTAR PARA O FORMULÁRIO (NOVO)
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
