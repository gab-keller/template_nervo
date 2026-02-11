# streamlit_app.py
import streamlit as st

st.set_page_config(
    page_title="TEMPLATE NERVO PERIFÉRICO - CONSULTA INICIAL E RETORNO",
    layout="wide",
)

# --- CSS: remove the gutter/padding that creates the big gap between label and input ---
st.markdown(
    """
    <style>
      /* Reduce (almost eliminate) the gap between columns everywhere */
      div[data-testid="stHorizontalBlock"]{
        gap: 0.15rem !important;
      }

      /* Remove left/right padding inside each column */
      div[data-testid="column"]{
        padding-left: 0 !important;
        padding-right: 0 !important;
      }

      /* Make markdown text vertically centered and tightly aligned */
      .inline-label{
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.6 !important;
        white-space: nowrap !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("TEMPLATE NERVO PERIFÉRICO - CONSULTA INICIAL E RETORNO")


def text_area_lines(label: str, lines: int, key: str, placeholder: str = ""):
    height_px = max(80, int(lines * 24 + 20))
    return st.text_area(label, key=key, height=height_px, placeholder=placeholder)


def inline_label_input(
    label_text: str,
    key: str,
    placeholder: str = "",
    label_col_ratio: float = 0.55,
    input_col_ratio: float = 5.0,
):
    # Very small label column + large input column, and CSS removes the gutter/padding.
    col_label, col_input = st.columns(
        [label_col_ratio, input_col_ratio],
        vertical_alignment="center",
    )
    with col_label:
        # HTML span with nowrap so the label hugs the input
        st.markdown(
            f'<div class="inline-label">{label_text}</div>',
            unsafe_allow_html=True,
        )
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
ph1, ph2, ph3 = st.columns([0.9, 1.0, 1.0], vertical_alignment="center")
with ph1:
    st.markdown('<div class="inline-label">Padrão de herança</div>', unsafe_allow_html=True)
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
        label_col_ratio=0.45,
        input_col_ratio=5.0,
    )

t2 = st.checkbox("sem tratamento medicamentoso", key="trat_sem")
if t2:
    tempo_sem = inline_label_input(
        label_text="há quanto tempo",
        key="trat_sem_tempo",
        placeholder="Ex.: 3 meses / desde 2021",
        label_col_ratio=0.45,
        input_col_ratio=5.0,
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

with st.expander("Visualizar dados (debug)", expanded=False):
    st.json(
        {
            "idade_inicio_sintomas": idade_inicio,
            "historia_clinica": historia_clinica,
            "antecedentes_patologicos": antecedentes,
            "historia_familiar": hist_familiar,
            "padrao_heranca_esporadico": esporadico,
            "padrao_heranca_familiar": familiar,
            "trat_em_uso": t1,
            "trat_em_uso_tempo": st.session_state.get("trat_em_uso_tempo", ""),
            "trat_sem": t2,
            "trat_sem_tempo": st.session_state.get("trat_sem_tempo", ""),
            "meds_atual_previo": meds_atual_previo,
            "outros_meds": outros_meds,
            "paciente_transplantado": transplantado,
        }
    )
