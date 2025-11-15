from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from app.agents.manim_agent import coding_agent_compiled
from app.prompts.visium_graph import director_prompt
from app.schemas.visium_graph_schema import Director, ScriptState, State
from app.services.audio_service import generate_voiceovers
from app.services.llm_service import llm
from app.services.logging_service import logger


def script_writer(state: State):
    script_llm = llm.with_structured_output(ScriptState)
    msg = script_llm.invoke(
        f"""Write a script on the {state["topic"]}, you are preparing slides to explain the topic properly, the slides will be static in nature but will be made with manim library. Make a flow of a educational video

        # Rules
        - In the dialouges say only what the narrator would say dont give any other comments other than dialouge. Whatever you say in dialouge will be directly converted to audio without any processing
         """
    )
    script, audio_paths = generate_voiceovers(msg.script, state["video_id"])
    logger.info(f"Generated script: {script}")
    logger.info(f"Generated audio paths: {audio_paths}")
    return {"script": script, "audio_paths": audio_paths}


def director(state: State):
    director_llm = llm.with_structured_output(Director)
    msg = director_llm.invoke(director_prompt(state["topic"], state["script"]))
    return {"directions": msg.directions}


def spawn_slide_workers(state: State):
    sends = []
    logger.info(f"\n\n{state['directions']}")
    for idx, direction in enumerate(state["directions"], start=1):
        logger.info(f"\n Running the coding agent on direction {direction}")
        sends.append(
            Send(
                "coding_agent",
                {
                    "direction": direction,
                    "rewrite": "not required",
                    "code": "",
                    "feedback": "",
                    "slide_index": idx,
                    "clip_id": f"{state['video_id']}_slide_{idx}",
                    "clip_video_id": state["video_id"],
                    "narration_text": state["script"][idx - 1].dialouge,
                    "duration": state["script"][idx - 1].duration,
                    "visuals": state["script"][idx - 1].slide_visuals,
                },
            )
        )
    return sends


# Main Graph
visium_workflow = StateGraph(State)
# Nodes
visium_workflow.add_node("script_writer", script_writer)
visium_workflow.add_node("director", director)
visium_workflow.add_node("coding_agent", coding_agent_compiled, output_keys=["clips", "video_paths", "codes"])
# Edges
visium_workflow.add_edge(START, "script_writer")
visium_workflow.add_edge("script_writer", "director")
visium_workflow.add_conditional_edges("director", spawn_slide_workers, ["coding_agent"])
visium_workflow.add_edge("coding_agent", END)


workflow = visium_workflow.compile()
