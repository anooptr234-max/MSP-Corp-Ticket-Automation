from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from rag.prompt import get_triage_prompt


# The strict schema matching your exact 7 generation fields
class AutomatedTicketAnalysis(BaseModel):
    ticket_summary: str = Field(description="A concise narrative summary of the reported IT issue.")
    predicted_category: str = Field(
        description="The predicted ticket queue category based on historical data matching (e.g., Hardware, Access, HR Support, Miscellaneous).")
    priority: str = Field(
        description="Priority level: Low, Medium, High, or Critical based strictly on the Priority Matrix criteria.")
    root_cause: str = Field(
        description="The likely underlying reason or system trigger behind the current technical behavior.")
    recommended_resolution: str = Field(
        description="The strategic technical solution or troubleshooting path to permanently resolve the issue.")
    technician_action: List[str] = Field(
        description="Step-by-step actionable checklist tasks for the assigned Service Desk Engineer to execute.")
    estimated_resolution_time: str = Field(
        description="Estimated Time to Resolution (ETR) based on task complexity (e.g., '15 mins', '2 hours').")


def generate_ticket_triage(new_ticket_text: str, retriever, model_name="gpt-4o-mini") -> AutomatedTicketAnalysis:
    """Executes vector search and applies the Service Desk Engineer LLM reasoning chain."""
    # Retrieve Top-K Similar Historical Records
    retrieved_docs = retriever.invoke(new_ticket_text)

    # Format matches into the prompt context block
    context_str = "\n\n".join([f"--- Match {i + 1} ---\n{doc.page_content}" for i, doc in enumerate(retrieved_docs)])

    # Set up prompt template and structured LLM compiler
    prompt = get_triage_prompt()
    llm = ChatOpenAI(model=model_name, temperature=0.1)
    structured_llm = llm.with_structured_output(AutomatedTicketAnalysis)

    rag_chain = prompt | structured_llm

    # Run pipeline orchestration
    output = rag_chain.invoke({"context": context_str, "incoming_ticket": new_ticket_text})
    return output