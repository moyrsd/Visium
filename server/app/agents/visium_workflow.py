from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import uuid
from app.agents.manim_agent import coding_agent_compiled
from app.services.llm_call import llm
from app.schemas.visium_graph import State, ScriptState, Director
from app.prompts.visium_graph import director_prompt


def script_writer(state: State):
    script_llm = llm.with_structured_output(ScriptState)
    msg = script_llm.invoke(
        f"Write a script on the {state['topic']}, you are preparing slides to explain the topic properly, the slides will be static in nature but will be made with manim library "
    )
    print(msg.script)
    return {"script": msg.script}


def director(state: State):
    director_llm = llm.with_structured_output(Director)
    msg = director_llm.invoke(director_prompt(state["topic"], state["script"]))
    return {"directions": msg.directions}


def spawn_slide_workers(state: State):
    session_key = state["id"]
    sends = []
    print(state["directions"])
    for idx, direction in enumerate(state["directions"]):
        print(f"\n Running the coding agent on direction {direction}")
        sends.append(
            Send(
                "coding_agent",
                {
                    "direction": direction,
                    "rewrite": "not required",
                    "code": "",
                    "feedback": "",
                    "slide_index": idx,
                    "session_key": session_key,
                },
            )
        )
    return sends


# Main Graph
visium_workflow = StateGraph(State)
# Nodes
visium_workflow.add_node("script_writer", script_writer)
visium_workflow.add_node("director", director)
visium_workflow.add_node("coding_agent", coding_agent_compiled, output_keys="codes")
# Edges
visium_workflow.add_edge(START, "script_writer")
visium_workflow.add_edge("script_writer", "director")
visium_workflow.add_conditional_edges("director", spawn_slide_workers, ["coding_agent"])
visium_workflow.add_edge("coding_agent", END)


workflow = visium_workflow.compile()
initial_state = {
    "topic": "pythagoras theorem",
    "script": [],
    "directions": [],
    "code": "",
    "rewrite": "not required",
    "feedback": "",
    "codes": [],
    "id": str(uuid.uuid4()),
}
output = workflow.invoke(initial_state)
# print(output["script"])
# ordered = sorted(output["codes"], key=lambda x: x["index"])
# final_codes = [c["code"] for c in ordered]
# print(final_codes)
