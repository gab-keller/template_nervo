# streamlit_app.py
import streamlit as st

st.set_page_config(
    page_title="TEMPLATE NERVO PERIFÉRICO - CONSULTA INICIAL E RETORNO",
    layout="wide",
)

# --- CSS: small controlled gutter + prevent label overflow into input ---
st.markdown(
    """
    <style>
      div[data-testid="stHorizontalBlock"]{ gap: 0.6rem !important; }
      div[data-testid="column"]{
        padding-left: 0.1rem !important;
        padding-right: 0.1rem !important;
      }
      .inline-label{
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.4 !important;
        white-space: normal !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <style>
      /* Make all subheader titles (st.subheader) red */
      h3 {
        color: #c00000 !important;  /* medical-style red */
      }

      /* Optional: slightly darker red on hover/selection consistency */
      h3 strong {
        color: #c00000 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("TEMPLATE NERVO PERIFÉRICO - CONSULTA INICIAL E RETORNO")


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


def compute_mrc_ss(mrc_keys: list[str]) -> tuple[bool, int | None]:
    """
    Returns (is_complete_and_valid, total_or_None)
    Valid only if ALL fields are filled with integers 0–5.
    """
    values = []
    for k in mrc_keys:
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


def small_mrc_box(key: str):
    return st.text_input(
        "",
        key=key,
        placeholder="0-5",
        label_visibility="collapsed",
        max_chars=1,
    )


# -----------------------------
# 1) História clínica
# -----------------------------
st.subheader("História clínica:")

idade_inicio = inline_label_input(
    "Idade ao início dos sintomas",
    key="idade_inicio_sintomas",
    placeholder="Ex.: 45",
)

historia_clinica = text_area_lines(
    label="",
    lines=10,
    key="historia_clinica_texto",
    placeholder="Descreva aqui a história clínica...",
)

# -----------------------------
# 2) Antecedentes Patológicos
# -----------------------------
st.subheader("Antecedentes Patológicos")
antecedentes = text_area_lines(
    label="",
    lines=4,
    key="antecedentes_patologicos_texto",
    placeholder="Comorbidades, cirurgias, alergias, etc...",
)

# -----------------------------
# 3) História familiar
# -----------------------------
st.subheader("História familiar")
hist_familiar = text_area_lines(
    label="",
    lines=4,
    key="historia_familiar_texto",
    placeholder="Detalhe antecedentes familiares relevantes...",
)

c0, c1, c2, _fill = st.columns([2.2, 1.4, 1.4, 10.0], vertical_alignment="center")
with c0:
    st.markdown('<div class="inline-label">Padrão de herança</div>', unsafe_allow_html=True)
with c1:
    esporadico = st.checkbox("Esporádico", key="hf_esporadico")
with c2:
    familiar = st.checkbox("Familiar", key="hf_familiar")

if esporadico and familiar:
    st.warning("Você marcou **Esporádico** e **Familiar** ao mesmo tempo. Se preferir, selecione apenas um.")

# -----------------------------
# 4) Medicações modificadoras de doença/Imunossupressores
# -----------------------------
st.subheader("Medicações modificadoras de doença/Imunossupressores")
st.markdown("**Tratamento atual:**")

tratamento_atual = st.radio(
    "",
    options=[
        "em uso de tratamento medicamentoso",
        "sem tratamento medicamentoso",
    ],
    index=None,  # no default selection
    key="tratamento_atual_radio",
)

if tratamento_atual == "em uso de tratamento medicamentoso":
    _ = inline_label_input(
        "há quanto tempo",
        key="trat_em_uso_tempo",
        placeholder="Ex.: 6 meses / 2 anos",
    )

elif tratamento_atual == "sem tratamento medicamentoso":
    _ = inline_label_input(
        "há quanto tempo",
        key="trat_sem_tempo",
        placeholder="Ex.: 3 meses / desde 2021",
    )

st.markdown("**Medicamentos de uso atual ou prévio, com data de início, data de término e motivo da suspensão**")
meds_atual_previo = text_area_lines(
    label="",
    lines=5,
    key="meds_atual_previo_texto",
    placeholder="",
)

st.markdown("**Outros medicamentos**")
outros_meds = text_area_lines(
    label="",
    lines=5,
    key="outros_meds_texto",
    placeholder="",
)

transplantado = st.checkbox("Paciente transplantado", key="paciente_transplantado")

# -----------------------------
# 5) Evolução clínica
# -----------------------------
st.subheader("Evolução clínica")

st.markdown("**Controle atual:**")

controle_atual = st.radio(
    "",
    options=[
        "estável ou melhorando",
        "piorando",
    ],
    index=None,  # nothing selected initially
    key="controle_atual_radio",
)

if controle_atual == "estável ou melhorando":
    _ = inline_label_input(
        "há quanto tempo",
        key="evo_estavel_tempo",
        placeholder="Ex.: 2 meses",
    )

st.markdown("**Descrição da evolução:**")
descricao_evo = text_area_lines(
    label="",
    lines=5,
    key="evo_descricao_texto",
    placeholder="",
)

# -----------------------------
# INCAT selector (no st.dialog) - AUTO-UPDATES DISPLAY
# -----------------------------

# state init
if "incat_open" not in st.session_state:
    st.session_state["incat_open"] = False
if "incat_ul" not in st.session_state:
    st.session_state["incat_ul"] = 0
if "incat_ll" not in st.session_state:
    st.session_state["incat_ll"] = 0
if "incat_total" not in st.session_state:
    st.session_state["incat_total"] = ""  # will store int or ""


c_incat_btn, c_incat_box, _f = st.columns([1.6, 3.0, 10.0], vertical_alignment="center")

with c_incat_btn:
    if st.button("Escala INCAT", key="btn_open_incat"):
        st.session_state["incat_open"] = True

with c_incat_box:
    # IMPORTANT: no key here, so it always reflects st.session_state["incat_total"]
    st.text_input(
        "Escala INCAT (MMSS + MMII)",
        value=str(st.session_state["incat_total"]) if st.session_state["incat_total"] != "" else "",
        disabled=True,
    )


# "Popup" (conditional panel)
if st.session_state["incat_open"]:
    st.markdown("#### Escala INCAT")

    st.markdown("**Membros Superiores**")
    ul_options = {
        0: "0 – Sem problemas nos membros superiores.",
        1: "1 – Sintomas em um ou ambos os braços, sem afetar a capacidade de realizar nenhuma das seguintes funções:\n"
           "• fechar todos os zíperes e botões\n"
           "• lavar ou pentear o cabelo\n"
           "• usar faca e garfo juntos\n"
           "• manusear moedas pequenas",
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

    # Compute total live
    ul = int(st.session_state["incat_ul"])
    ll = int(st.session_state["incat_ll"])
    total = ul + ll
    st.markdown(f"**MMSS ({ul}) + MMII ({ll}) = {total}**")

    b1, b2, _bfill = st.columns([1, 1, 10.0])
    with b1:
        if st.button("Salvar INCAT", key="btn_save_incat", type="primary"):
            st.session_state["incat_total"] = f"MMSS ({ul}) + MMII ({ll}) = {total}"
            st.session_state["incat_open"] = False
            st.rerun()

    with b2:
        if st.button("Cancelar", key="btn_cancel_incat"):
            st.session_state["incat_open"] = False
            st.rerun()

# ---- MRC-SS display (right after INCAT) ----
mrc_keys = [
    "mrc_ombro_D", "mrc_ombro_E",
    "mrc_cotovelo_D", "mrc_cotovelo_E",
    "mrc_punho_D", "mrc_punho_E",
    "mrc_quadril_D", "mrc_quadril_E",
    "mrc_joelho_D", "mrc_joelho_E",
    "mrc_tornozelo_D", "mrc_tornozelo_E",
]

if "mrc_ss_total" not in st.session_state:
    st.session_state["mrc_ss_total"] = ""   # stays blank until user calculates

inline_label_display("Escala MRC-SS", str(st.session_state["mrc_ss_total"]) if st.session_state["mrc_ss_total"] != "" else "")

st.markdown("**Outras escalas e métricas de seguimento**")
_ = text_area_lines(
    label="",
    lines=5,
    key="outras_escalas_seguimento",
    placeholder="NIS, dinamometria, tempo de marcha, TUG",
)


# -----------------------------
# 6) Exame físico neurológico
# -----------------------------
st.subheader("Exame físico neurológico")

_ = text_area_lines(
    label="",
    lines=5,
    key="exame_fisico_neuro_texto",
    placeholder="Força, tônus, reflexo, equilíbrio, sensibilidade, nervos cranianos, alterações autonômicas, cognição",
)

st.markdown("**MRC:**")  # smaller, same style as "Controle atual:"

# Header row
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

# Button appears only when all fields are complete + valid
complete, total = compute_mrc_ss(mrc_keys)

bcalc1, bcalc2, _fill = st.columns([2.2, 2.2, 10.0], vertical_alignment="center")
with bcalc1:
    if complete:
        if st.button("Calcular MRC-SS", key="btn_calc_mrcss", type="primary"):
            st.session_state["mrc_ss_total"] = total  # writes the value used by the display box above
            st.success(f"MRC-SS calculado: {total}")
            st.rerun()
    else:
        st.caption("Preencha todos os 12 campos (0–5) para habilitar o cálculo do MRC-SS.")

with bcalc2:
    if st.button("Limpar MRC-SS", key="btn_clear_mrcss"):
        st.session_state["mrc_ss_total"] = ""
        st.rerun()

# =============================
# ADD THESE SECTIONS AFTER YOUR "EXAME FÍSICO NEUROLÓGICO" SECTION
# (you can paste them at the end of the file, below the deformidades box)
# =============================

# -----------------------------
# 4) Exames complementares
# -----------------------------
st.subheader("Exames complementares")

st.markdown("**ENMG**")
_ = text_area_lines(
    label="",
    lines=3,
    key="exames_enmg",
    placeholder="Data e conclusão da ENMG",
)

st.markdown("**Líquor**")
_ = text_area_lines(
    label="",
    lines=3,
    key="exames_liquor",
    placeholder="Data e achados do líquor",
)

st.markdown("**USG nervos**")
_ = text_area_lines(
    label="",
    lines=3,
    key="exames_usg_nervos",
    placeholder="Data e achados do USG",
)

st.markdown("**Biópsia**")
_ = text_area_lines(
    label="",
    lines=3,
    key="exames_biopsia",
    placeholder="Data e achados da  biópsia de nervo, glândulas salivares, panículo adiposo, etc.",
)

st.markdown("**Demais exames**")
_ = text_area_lines(
    label="",
    lines=3,
    key="exames_demais",
    placeholder="Data e descrição dos demais exames relevantes (laboratoriais, RM, teste genético)",
)

# -----------------------------
# 5) Impressão e discussão
# -----------------------------
st.subheader("Impressão e discussão:")
_ = text_area_lines(
    label="",
    lines=4,
    key="impressao_discussao",
    placeholder="Impressão diagnóstica. Avaliação sobre o estado atual de controle ou se há progressão da doença",
)

# -----------------------------
# 6) Diagnóstico/Hipótese diagnóstica
# -----------------------------
st.subheader("Diagnóstico/Hipótese diagnóstica:")

dx_options = [
    "Neuropatia genética",
    "Neuropatia imunomediada",
    "Outras neuropatias adquiridas (nutricional, endocrinológica, infecciosa, tóxica, etc.)",
    "Outros diagnósticos (neurônio motor, junção e músculo)",
    "Diagnóstico indefinido",
]

dx_categoria = st.radio(
    "Selecione UMA opção",
    options=dx_options,
    key="radio_dx_categoria",
)

# ---- Submenu: Neuropatia genética (single choice) ----
if dx_categoria == "Neuropatia genética":
    with st.expander("Detalhar (Neuropatia genética)", expanded=True):
        gen_options = ["PMP22", "MPZ", "GJB1", "MFN2", "Outro"]
        dx_genetica_choice = st.radio(
            "Gene / causa (selecione UMA opção)",
            options=gen_options,
            key="dx_genetica_choice",
        )

        if dx_genetica_choice == "Outro":
            st.text_input(
                "Especifique:",
                key="dx_genetica_outro",
                placeholder="Ex.: SH3TC2, NEFL, TTR, etc.",
            )

# ---- Submenu: Neuropatia imunomediada (single choice) ----
if dx_categoria == "Neuropatia imunomediada":
    with st.expander("Detalhar (Neuropatia imunomediada)", expanded=True):
        imuno_options = ["CIDP", "Vasculite", "Ganglionopatia", "Neuropatia motora multifocal", "Outro"]
        dx_imuno_choice = st.radio(
            "Especifique:",
            options=imuno_options,
            key="dx_imuno_choice",
        )

        if dx_imuno_choice == "Outro":
            st.text_input(
                "Especifique",
                key="dx_imuno_outro",
                placeholder="Ex.: anti-MAG, AMAN/AMSAN, paraneoplásica, etc.",
            )

# Optional: compact auto-summary (safe)
summary = dx_categoria
if dx_categoria == "Neuropatia genética":
    choice = st.session_state.get("dx_genetica_choice", "")
    if choice == "Outro":
        extra = st.session_state.get("dx_genetica_outro", "").strip()
        if extra:
            summary += f" | Gene: {extra}"
        else:
            summary += " | Gene: outro (não especificado)"
    elif choice:
        summary += f" | Gene: {choice}"

if dx_categoria == "Neuropatia imunomediada":
    choice = st.session_state.get("dx_imuno_choice", "")
    if choice == "Outro":
        extra = st.session_state.get("dx_imuno_outro", "").strip()
        if extra:
            summary += f" | Subtipo: {extra}"
        else:
            summary += " | Subtipo:"
    elif choice:
        summary += f" | Subtipo: {choice}"

st.caption(summary)

# -----------------------------
# 7) Conduta
# -----------------------------
st.subheader("Conduta:")
_ = text_area_lines(
    label="",
    lines=4,
    key="conduta",
    placeholder="Conduta diagnóstica e terapêutica",
)
