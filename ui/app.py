import gradio as gr
from config import ui_config
from pathlib import Path

# UI function: only handles UI, not workflow logic

def create_app(chat_fn, clear_fn):
    """
    Create the Gradio UI for SupportFlowX.
    chat_fn: function to handle chat (inputs: user_message, history, api_key)
    clear_fn: function to clear chat (no inputs)
    Returns: gr.Blocks object
    """
    base_dir = Path(__file__).parent.parent
    css_path = base_dir / "ui" / "theme.css"
    with open(css_path, "r", encoding="utf-8") as f:
        custom_css = f.read()

    with gr.Blocks(
        title=ui_config.APP_TITLE,
        css=custom_css,
        theme=gr.themes.Soft()
    ) as app:
        gr.HTML(f"""
        <link rel="icon" type="image/png" href="file={ui_config.LOGO_PATH}">
        """)
        with gr.Row(elem_classes="main-container animate-fade-in"):
            with gr.Column(scale=3):
                gr.HTML(f"""
                    <div class="header-title">
                        {ui_config.WELCOME_TITLE}
                    </div>
                    <div style="text-align: center; margin-bottom: 20px;">
                        <p style="font-size: 1.2em; color: #666; font-weight: 500;">
                            {ui_config.WELCOME_MESSAGE}
                        </p>
                    </div>
                """)
            with gr.Column(scale=1):
                gr.Image(
                    ui_config.COVER_PATH,
                    height=200,
                    show_label=False,
                    container=False,
                    show_download_button=False
                )
        with gr.Row(elem_classes="main-container"):
            with gr.Column(scale=3, elem_classes="chat-container card-hover"):
                chatbot = gr.Chatbot(
                    type='messages',
                    label="💬 Chat with our Cafe Assistant",
                    height=400,
                    elem_classes="chatbot",
                    show_copy_button=True
                )
                with gr.Column(elem_classes="input-area"):
                    msg = gr.Textbox(
                        label="💭 What can I help you with today?",
                        placeholder="Ask about our menu, prices, promotions, or table availability...",
                        lines=1,
                        scale=7
                    )
                    with gr.Row():
                        send_btn = gr.Button(
                            "📤 Send Message",
                            scale=2,
                            elem_classes="send-button",
                            variant="primary"
                        )
                        clear_btn = gr.Button(
                            "🗑️ Clear Chat",
                            scale=1,
                            elem_classes="clear-button",
                            variant="secondary"
                        )
                with gr.Column(elem_classes="examples-container"):
                    gr.HTML('<div class="examples-title">💡 Quick Questions</div>')
                    gr.Examples(
                        examples=ui_config.EXAMPLES,
                        inputs=[msg],
                    )
            with gr.Column(scale=1, elem_classes="sidebar card-hover"):
                gr.Image(
                    ui_config.ICON_PATH,
                    height=120,
                    show_label=False,
                    container=False,
                    show_download_button=False
                )
                gr.HTML("""
                    <div style="text-align: center; margin-bottom: 20px;">
                        <h3 style="color: white; margin: 0;">🔐 API Configuration</h3>
                    </div>
                """)
                with gr.Column(elem_classes="api-key-container"):
                    api_key_box = gr.Textbox(
                        label="🔑 Gemini API Key",
                        placeholder="Enter your Gemini API key here...",
                        type="password",
                        info="Get your API key from https://makersuite.google.com/app/apikey",
                        lines=1
                    )
                with gr.Column(elem_classes="log-container"):
                    gr.HTML('<h4 style="color: white; margin-top: 0;">📋 System Logs</h4>')
                    logbox = gr.Textbox(
                        label="",
                        interactive=False,
                        lines=18,
                        placeholder="System logs will appear here...",
                        show_label=False
                    )
        # Event handlers
        # Both send_btn.click and msg.submit trigger chat_fn
        send_btn.click(
            fn=chat_fn,
            inputs=[msg, chatbot, api_key_box],
            outputs=[chatbot, logbox]
        ).then(
            fn=lambda: "",
            outputs=[msg]
        )
        msg.submit(
            fn=chat_fn,
            inputs=[msg, chatbot, api_key_box],
            outputs=[chatbot, logbox]
        ).then(
            fn=lambda: "",
            outputs=[msg]
        )
        clear_btn.click(
            fn=clear_fn,
            outputs=[chatbot, logbox]
        )
    return app 