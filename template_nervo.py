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


def incat_dialog():
    # Initialize defaults
    if "incat_ul" not in st.session_state:
        st.session_state["incat_ul"] = None
    if "incat_ll" not in st.session_state:
        st.session_state["incat_ll"] = None

    with st.dialog("Escala INCAT"):
        st.markdown("### Membros Superiores")

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

        st.session_state["incat_ul"] = st.radio(
            "Selecione UMA opção (MMSS)",
            options=list(ul_options.keys()),
            format_func=lambda k: ul_options[k],
            index=(list(ul_options.keys()).index(st.session_state["incat_ul"])
                   if st.session_state["incat_ul"] in ul_options else 0),
            key="incat_ul_radio",
        )

        st.markdown("---")
        st.markdown("### Marcha (Membros Inferiores)")

        ll_options = {
            0: "0 – Marcha não afetada.",
            1: "1 – Marcha afetada, mas caminha independentemente em ambientes externos.",
            2: "2 – Geralmente necessita apoio unilateral (bengala, muleta simples ou apoio de um braço) para caminhar em ambientes externos.",
            3: "3 – Geralmente necessita apoio bilateral (duas bengalas, muletas, andador ou apoio de dois braços) para caminhar em ambientes externos.",
            4: "4 – Geralmente usa cadeira de rodas para se locomover em ambientes externos, mas consegue ficar em pé e andar alguns passos com ajuda.",
            5: "5 – Restrito à cadeira de rodas, incapaz de ficar em pé ou andar, ou apenas alguns passos mesmo com ajuda.",
        }

        st.session_state["incat_ll"] = st.radio(
            "Selecione UMA opção (MMII)",
            options=list(ll_options.keys()),
            format_func=lambda k: ll_options[k],
            index=(list(ll_options.keys()).index(st.session_state["incat_ll"])
                   if st.session_state["incat_ll"] in ll_options else 0),
            key="incat_ll_radio",
        )

        total = int(st.session_state["incat_ul"]) + int(st.session_state["incat_ll"])
        st.markdown(f"**Total (UL + LL): {total}**")

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("Salvar", type="primary"):
                st.session_state["incat_total"] = total
                st.rerun()
        with c2:
            if st.button("Cancelar"):
                st.rerun()


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

t1 = st.checkbox("em uso de tratamento medicamentoso", key="trat_em_uso")
if t1:
    _ = inline_label_input("há quanto tempo", key="trat_em_uso_tempo", placeholder="Ex.: 6 meses / 2 anos")

t2 = st.checkbox("sem tratamento medicamentoso", key="trat_sem")
if t2:
    _ = inline_label_input("há quanto tempo", key="trat_sem_tempo", placeholder="Ex.: 3 meses / desde 2021")

if t1 and t2:
    st.warning("Você marcou **em uso** e **sem tratamento** ao mesmo tempo. Se quiser, mantenha apenas uma opção.")

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

estavel = st.checkbox("estável ou melhorando", key="evo_estavel")
if estavel:
    _ = inline_label_input("há quanto tempo", key="evo_estavel_tempo", placeholder="Ex.: 2 meses")

piorando = st.checkbox("piorando", key="evo_piorando")

if estavel and piorando:
    st.warning("Você marcou **estável ou melhorando** e **piorando** ao mesmo tempo. Se quiser, mantenha apenas uma opção.")

st.markdown("**Descrição da evolução:**")
descricao_evo = text_area_lines(
    label="",
    lines=5,
    key="evo_descricao_texto",
    placeholder="",
)

# INCAT selection + computed textbox
if "incat_total" not in st.session_state:
    st.session_state["incat_total"] = ""

c_incat_btn, c_incat_box, _f = st.columns([1.2, 3.0, 10.0], vertical_alignment="center")
with c_incat_btn:
    if st.button("Selecionar Escala INCAT"):
        incat_dialog()

with c_incat_box:
    st.text_input(
        "Escala INCAT (UL + LL)",
        value=str(st.session_state["incat_total"]) if st.session_state["incat_total"] != "" else "",
        key="incat_total_display",
        disabled=True,
    )
