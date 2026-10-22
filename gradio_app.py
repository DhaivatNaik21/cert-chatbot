
import gradio as gr
from answer import answer_question

def handle_query(question):
    if not question.strip():
        return "Please enter a question."
    return answer_question(question)

# with gr.Blocks() as demo:
#     gr.Markdown("# Certifications Assistant")
#     inp = gr.Textbox(label="Your question about Certifications", lines=2)
#     btn = gr.Button("Ask")
#     out = gr.Textbox(label="Answer", lines=10)

#     btn.click(handle_query, inputs=inp, outputs=out)
#     inp.submit(handle_query, inputs=inp, outputs=out)

with gr.Blocks() as demo:
    gr.Markdown("# DLGS Certifications Assistant")
    gr.Markdown(
        "Local development prototype for certification reference questions. "
        "Verify answers against the cited source documents."
    )

    inp = gr.Textbox(
        label="Certification question",
        lines=2,
    )
    btn = gr.Button("Ask")
    out = gr.Textbox(
        label="Answer",
        lines=10,
    )

    btn.click(handle_query, inputs=inp, outputs=out)
    inp.submit(handle_query, inputs=inp, outputs=out)

if __name__ == "__main__":
    demo.launch()
