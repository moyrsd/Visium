from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Send
from typing import List
import operator
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("⚠️ GEMINI_API_KEY not found in environment!")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_retries=3,
    google_api_key=api_key,
)


class Script(BaseModel):
    dialouge: str = Field(
        None, json_schema_extra="What will the narrator say at this part of the video"
    )
    visuals: str = Field(
        None,
        json_schema_extra="What will the visuals look like at this part of the video",
    )


class ScriptState(BaseModel):
    script: List[Script] = Field(
        [], json_schema_extra="Step by step explainination of the given topic"
    )


class Director(BaseModel):
    directions: List[str] = Field(
        [], json_schema_extra="Visual directions for the video in natural language"
    )


class State(TypedDict):
    topic: str
    script: List[Script]
    directions: List[str]
    code: str
    rewrite: Literal["required", "not required"] = Field(
        "not required",
        json_schema_extra="Check if rewrite of the code is required or not",
    )
    feedback: str = Field(
        None,
        json_schema_extra="If code rewrite is required what changes to make suggest so that the geometry is exactly like described",
    )


class CodingReviewState(BaseModel):
    rewrite: Literal["required", "not required"] = Field(
        "not required",
        json_schema_extra="Check if rewrite of the code is required or not",
    )
    feedback: str = Field(
        None,
        json_schema_extra="If code rewrite is required what changes to make suggest so that the geometry is exactly like described",
    )


class CodingWorkerState(BaseModel):
    topic: str
    directions: str
    direction: str
    rewrite: Literal["required", "not required"] = Field(
        "not required",
        json_schema_extra="Check if rewrite of the code is required or not",
    )
    feedback: str = Field(
        None,
        json_schema_extra="If code rewrite is required what changes to make suggest so that the geometry is exactly like described",
    )
    codes: List[str]


def script_writer(state: State):
    script_llm = llm.with_structured_output(ScriptState)
    msg = script_llm.invoke(
        f"Write a concise script like 3blue1brown explaining the topic {state['topic']}"
    )
    return {"script": msg.script}


def director(state: State):
    director_llm = llm.with_structured_output(Director)
    msg = director_llm.invoke(
        f"""You are a exceptional director, you have to give exact visual instructions for a manim coding agent in natural langguage what will actually , we are making a video on topic {state["topic"]} and here is the script {state["script"]},
         # Rules 
         - Each instructions should make sense independently,every directions will be given to separate workers unaware of other direction
         - you have to give detailed instructions on each visual action
         - Dont keep anything vague, the next person is not going to fig out 
         - The next person is dumb explain what shape, which position, what movement, what angle , from where it should originate everything
         - If you are profing something visually explain that step by step , how to go from current frame to next frame, speak every movement 
         - Search in wikipedia if required to know more about the topic and see existing ways of proofs
         """
    )
    return {"directions": msg.directions}


def code_generator(state: State):
    if state["rewrite"] == "required":
        feedback = state["feedback"]
        msg = llm.invoke(
            f"""You are an exceptional coder in manim library in python. You are making a part of the video on the topic {state["topic"]}, the directions for you are as {state["directions"]}
            this is the previous code {state["code"]} and feedback for the code {feedback}
            # Rules
            - Use $ for latex wherever necessary, before every symbol use $
            - Check if it follows the directions completly 
            - The animations should be geomtrically correct
            - Only return the code 
            - Import all the things that are required 
            """
        )

    else:
        msg = llm.invoke(
            f"""You are an exceptional coder in manim library in python. You are making a part of the video on the topic {state["topic"]}, the directions for you are as {state["directions"]}
            # Rules
            - Use $ for latex wherever necessary, before every symbol use $
            - Only return the code 
            - Import all the things that are required 
            """
        )

    return {"code": msg.content}


def code_reviewer(state: State):
    reviewer = llm.with_structured_output(CodingReviewState)
    msg = reviewer.invoke(
        f"""
        Check if the code {state["code"]} is following all the directions {state["directions"]} and if not give feedback, and how to improve 

        # Rules
        - Use $ for latex wherever necessary, before every symbol use $
        - Check for syntax mistakes
        - Check if the code is following latest syntax
        """
    )
    print(msg.feedback)
    return {"rewrite": msg.rewrite, "feedback": msg.feedback}


def route_code_review(state: State):
    if state["rewrite"] == "required":
        return "Rejected"
    else:
        return "Accepted"


def final_json_creator(state: State):
    pass


# Main Graph
visium_workflow = StateGraph(State)

# Nodes
visium_workflow.add_node("script_writer", script_writer)
visium_workflow.add_node("director", director)
visium_workflow.add_node("code_generator", code_generator)
visium_workflow.add_node("code_reviewer", code_reviewer)
visium_workflow.add_node("final_json_creator", final_json_creator)

# Edges
visium_workflow.add_edge(START, "script_writer")
visium_workflow.add_edge("script_writer", "director")
visium_workflow.add_edge("director", "code_generator")
visium_workflow.add_edge("code_generator", "code_reviewer")
visium_workflow.add_conditional_edges(
    "code_reviewer", route_code_review, {"Accepted": END, "Rejected": "code_generator"}
)


workflow = visium_workflow.compile()
initial_state = {
    "topic": "pythagoras theorem",
    "script": [],
    "directions": [],
    "code": "",
    "rewrite": "not required",
    "feedback": "",
}
output = workflow.invoke(initial_state)
print(output["code"])
