
import gradio as gr
from answer import answer_question  # reusing function from answer.py

def handle_query(question):
    if not question.strip():
        return "Please enter a question."
    return answer_question(question, k=5)

with gr.Blocks() as demo:
    gr.Markdown("# Certifications Assistant")
    inp = gr.Textbox(label="Your question about Certifications", lines=2)
    btn = gr.Button("Ask")
    out = gr.Textbox(label="Answer", lines=10)

    btn.click(handle_query, inputs=inp, outputs=out)
    inp.submit(handle_query, inputs=inp, outputs=out)

if __name__ == "__main__":
    demo.launch()
