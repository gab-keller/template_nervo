# streamlit_app.py
import streamlit as st

st.set_page_config(
    page_title="TEMPLATE NERVO PERIFÉRICO - CONSULTA INICIAL E RETORNO",
    layout="wide",
)

st.title("TEMPLATE NERVO PERIFÉRICO - CONSULTA INICIAL E RETORNO")


# Helper: approximate "N lines" of space in a text area
def text_area_lines(label: str, lines: int, key: str, placeholder: str = ""):
    height_px = max(80, int(lines * 24 + 20))
    return st.text_area(label, key=key, height=height_px, placeholder=placeholder)


# Helper: put a label and an input *immediately beside it* (minimal gap)
def inline_label_input(
    label_text: str,
    key: str,
    placeholder: str = "",
    input_width_ratio: float = 1.5,
    label_bold: bool = False,
):
    # 0px gap between columns isn't possible in Streamlit, but this gets very close.
    # Small label col + input col, with minimal markdown padding.
    col_label, col_input = st.columns(
        [1, input_width_ratio], vertical_alignment="center", gap="small"
    )
    with col_label:
        if label_bold:
            st.markdown(f"**{label_text}**")
        else:
            st.markdown(label_text)
    with col_input:
        return st.text_input(
            label="",
            key=key,
            placeholder=placeholder,
            label_visibility="collapsed",
        )


# -----------------------------
# 1) História clínica
# -----------------------------
st.subheader("História clínica:")

idade_inicio = inline_label_input(
    label_text="Idade ao início dos sintomas",
    key="idade_inicio_sintomas",
    placeholder="Ex.: 45",
    input_width_ratio=1.2,
    label_bold=False,
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

# "Padrão de herança" + two checkboxes in the same line
ph1, ph2, ph3 = st.columns([1.2, 1, 1], vertical_alignment="center", gap="small")
with ph1:
    st.markdown("Padrão de herança")
with ph2:
    esporadico = st.checkbox("Esporádico", key="hf_esporadico")
with ph3:
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
    tempo_em_uso = inline_label_input(
        label_text="há quanto tempo",
        key="trat_em_uso_tempo",
        placeholder="Ex.: 6 meses / 2 anos",
        input_width_ratio=1.6,
        label_bold=False,
    )

t2 = st.checkbox("sem tratamento medicamentoso", key="trat_sem")
if t2:
    tempo_sem = inline_label_input(
        label_text="há quanto tempo",
        key="trat_sem_tempo",
        placeholder="Ex.: 3 meses / desde 2021",
        input_width_ratio=1.6,
        label_bold=False,
    )

if t1 and t2:
    st.warning("Você marcou **em uso** e **sem tratamento** ao mesmo tempo. Se quiser, mantenha apenas uma opção.")

st.markdown("**Medicamentos de uso atual ou prévio, com data de início, data de término e motivo da suspensão**")
meds_atual_previo = text_area_lines(
    label="",
    lines=5,
    key="meds_atual_previo_texto",
    placeholder="Ex.: Rituximabe 1g D1/D15 (início 01/2024), suspensão 07/2024 por infecção...",
)

st.markdown("**Outros medicamentos**")
outros_meds = text_area_lines(
    label="",
    lines=5,
    key="outros_meds_texto",
    placeholder="Liste outros medicamentos relevantes...",
)

transplantado = st.checkbox("Paciente transplantado", key="paciente_transplantado")
