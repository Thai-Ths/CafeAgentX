import gradio as gr
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict, Annotated, List, Dict
import operator
from langchain_google_genai import ChatGoogleGenerativeAI
from RAG import RAGSystem
from AG00_intake_agent import IntakeAgent 
from AG01_cafe_bot import LanscapeCafeBot
from AG02_database_agent import CoffeeDatabaseAgent
from AG03_aggregator_agent import AggregatorAgent
from config import ALLOWED_AGENTS
from pathlib import Path
from PIL import Image

base_dir = Path(__file__).parent

class AgentAssignment(TypedDict):
    agent: str          # ชื่อ agent เช่น "product_agent", "billing_agent", "support_agent"
    command: str        # คำสั่ง (str) ที่ให้ agent นั้นนำไปใช้ (plain text หรือ prompt สั้นๆ)
    result: str = None  # ผลลัพธ์ที่ agent นั้นส่งกลับ (optional, หลังจากประมวลผล)
    finish: bool = False # True if intake response

class AssignmentResponse(TypedDict):
    assignments: List[AgentAssignment]

class SupportFlowXState(TypedDict):
    user_message: Annotated[str, "readonly"]                # ต้นฉบับจาก user
    chat_history: Annotated[List[Dict[str, str]], operator.add]    # history ทั้งหมด (user/agent)
    allowed_agents: Annotated[List[str], "set"]
    assigned_agents: Annotated[AssignmentResponse, "set"]          # รายชื่อ agent ที่ถูก assign (ช่วย debug/monitor)
    final_response: Annotated[str, "set"]                   # ข้อความสุดท้ายถึง user (set/replace)
    logs: Annotated[List[str], operator.add]                # log ทุกอย่าง (append/add)

rag = RAGSystem(
        knowledge_base_path=str(base_dir / "knowledge-base"),
        collection_name="landscape_cafe",
        db_path=str(base_dir / "landscape_cafe"),
        embedding_model_name="BAAI/bge-m3"
    )

# ──────────────── AGENT ────────────────
def make_agents(api_key: str):
    # 1. สร้าง Gemini agent
    gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20", google_api_key=api_key)
    gemini_with_output = gemini.with_structured_output(AssignmentResponse)
    # 2. เตรียม RAG, database path (ปรับ config ได้)
    
    db_path = str(base_dir / "data" / "database.db")
    # 3. สร้าง node function (factory/closure pattern)
    def intake_node(state: dict) -> dict:
        intake_agent = IntakeAgent(gemini_with_output)
        return intake_agent.process(state)
    
    def landscape_cafe_bot(state: dict) -> dict:
        question = ""
        for a in state["assigned_agents"]:
            if a["agent"] == "landscape_cafe_bot":
                question = a["command"]
                break
        agent = LanscapeCafeBot(rag, gemini)
        response = agent.process(question)
        for a in state["assigned_agents"]:
            if a["agent"] == "landscape_cafe_bot":
                a["result"] = response.get("result", "")
        log = f"{response.get('logs', '')}"
        return {"logs": [log]}
    
    def coffee_db_agent(state: dict) -> dict:
        question = ""
        for a in state["assigned_agents"]:
            if a["agent"] == "coffee_db_agent":
                question = a["command"]
                break
        agent = CoffeeDatabaseAgent(db_path=db_path, llm_agent=gemini)
        response = agent.process(question)
        for a in state["assigned_agents"]:
            if a["agent"] == "coffee_db_agent":
                a["result"] = response.get("result", "")
        log = f"{response.get('logs', '')}"
        return {"logs": [log]}
    
    def aggregator_node(state: dict) -> dict:
        aggregator = AggregatorAgent(gemini)
        return aggregator.process(state)
    
    return {
        "intake_node": intake_node,
        "landscape_cafe_bot": landscape_cafe_bot,
        "coffee_db_agent": coffee_db_agent,
        "aggregator_node": aggregator_node,
    }

# ──────────────── WORKFLOW ────────────────
def intake_router(state: dict) -> List[str]:
    assignments = state.get("assigned_agents", [])
    assigned_names = [a["agent"] for a in assignments]
    if "END" in assigned_names:
        return ["finish"]
    else:
        return assigned_names

def build_workflow(intake_node, landscape_cafe_bot, coffee_db_agent, aggregator_node):
    graph = StateGraph(SupportFlowXState)
    graph.add_node("intake_agent", intake_node)
    graph.add_node("landscape_cafe_bot", landscape_cafe_bot)
    graph.add_node("coffee_db_agent", coffee_db_agent)
    graph.add_node("aggregator", aggregator_node)
    graph.set_entry_point("intake_agent")

    # intake route
    graph.add_conditional_edges(
        "intake_agent",
        intake_router,
        {
            "landscape_cafe_bot": "landscape_cafe_bot",
            "coffee_db_agent": "coffee_db_agent",
            "finish": END,
        }
    )
    graph.add_edge("landscape_cafe_bot", "aggregator")
    graph.add_edge("coffee_db_agent", "aggregator")
    graph.add_edge("aggregator", END)
    return graph.compile()

# ──────────────── GRADIO UI ────────────────

def chat(user_message: str, history: list = None, api_key: str = None) -> tuple:
    try:
        if not api_key or not api_key.startswith("AI"):
            return history or [], "⚠️ Please enter a valid Gemini API Key."
        if not user_message.strip():
            return history or [], "⚠️ Please fill in the message."

        agents = make_agents(api_key=api_key)
        workflow = build_workflow(
            agents["intake_node"],
            agents["landscape_cafe_bot"],
            agents["coffee_db_agent"],
            agents["aggregator_node"]
        )
        allowed_agents = list(ALLOWED_AGENTS.keys())
        chat_history = history.copy() if history else []
        state = {
            "user_message": user_message,
            "chat_history": chat_history,
            "allowed_agents": allowed_agents,
            "assigned_agents": [],
            "final_response": "",
            "logs": []
        }
        result = workflow.invoke(state)
        bot_reply = (result.get("final_response") or "ขออภัย ฉันไม่เข้าใจคำถาม กรุณาลองใหม่อีกครั้ง")
        logs = "\n".join(result.get("logs", []))
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": bot_reply})
        # จำกัด history ไม่เกิน 20 ข้อความล่าสุด
        history = history[-20:]
        return history, logs
    except Exception as e:
        return history or [], f"❌ Internal error: {str(e)[:500]}"

def clear_chat():
    return [], ""

def create_demo():
    landscape_icon = Image.open(base_dir / "image/landscape_icon.jpg")
    landscape_cover = Image.open(base_dir / "image/landscape_cover.jpg")

    css_path = base_dir / "cafe_theme.css"
    with open(css_path, "r", encoding="utf-8") as f:
        custom_css = f.read()

    with gr.Blocks(
        title="Landscape Cafe & Eatery Chatbot",
        css=custom_css,
        theme=gr.themes.Soft()
    ) as demo:
        
        with gr.Row(elem_classes="main-container animate-fade-in"):
            with gr.Column(scale=3):
                gr.HTML("""
                    <div class="header-title">
                        ☕ Landscape Cafe & Eatery Assistant 🌿
                    </div>
                    <div style="text-align: center; margin-bottom: 20px;">
                        <p style="font-size: 1.2em; color: #666; font-weight: 500;">
                            Welcome to our cozy cafe! I'm here to help you with menu, promotions, and reservations.
                        </p>
                    </div>
                """)
            with gr.Column(scale=1):
                gr.Image(
                    landscape_cover,
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
                        lines=2,
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
                        examples=[
                            "Location and parking lots?",
                            "เวลาเปิดปิดร้าน",
                            "โปรโมชั่นประจำเดือน", 
                            "ขอรายการสินค้าที่มีพร้อมราคา",
                            "Sales this month",
                            "ตรวจสอบโต๊ะว่างขณะนี้และช่องทางติดต่อ"
                        ],
                        inputs=[msg],
                    )
            
            with gr.Column(scale=1, elem_classes="sidebar card-hover"):
                # Display landscape icon
                gr.Image(
                    landscape_icon,
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
        send_btn.click(
            fn=chat,
            inputs=[msg, chatbot, api_key_box],
            outputs=[chatbot, logbox]
        ).then(
            fn=lambda: "",
            outputs=[msg]
        )
        
        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot, logbox]
        )
        
        msg.submit(
            fn=chat,
            inputs=[msg, chatbot, api_key_box],
            outputs=[chatbot, logbox]
        ).then(
            fn=lambda: "",
            outputs=[msg]
        )

    return demo

if __name__ == "__main__":
    demo = create_demo()
    demo.launch(debug=True)
