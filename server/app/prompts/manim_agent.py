def code_rewrite_prompt(direction, code, feedback, index):
    return f"""
            You are a professional Manim CE developer. Your task is to fix and finalize the Manim code below so it exactly matches the given slide specification.

            # Slide Specification
            {direction}

            # Previous Code
            {code}

            # Reviewer Feedback
            {feedback}

            # Instructions
            - Never include ```python fences in your output.
            - Apply **only the minimal changes** required to correct the code.
            - Preserve the same class name (`Slide{index}`) and structure.
            - Fix all syntax or logical issues (invalid methods, wrong vertex format, etc.).
            - Ensure all shapes, coordinates, colors, and LaTeX text match the description exactly.
            - Verify Manim CE 0.18+ API compatibility.

            # Rules
            - Make the video as same length as given in the direction, dont use fade out or fade in 
            - All coordinate points must be 3D vectors of the form [x, y, 0]. Using [x, y] will cause broadcasting errors.
            - Use `Polygon(p1, p2, p3)` format, never nested lists.
            - Use `.set_fill(color, opacity=...)` and `.set_stroke(WHITE, width=1)` for shapes.
            - Use `.scale()` for sizing, not `font_size =`.
            - Use `.next_to`, `.move_to`, `.to_edge` for positioning.
            - Ensure all text is `MathTex`.
            - You must output only Python source code — not markdown fences, not explanations, not comments.
            """


def code_generator_prompt(direction, index):
    return f"""
            You are an expert Manim CE (version 0.18+) developer. Your task is to generate slide based on the description below.

            # Visual Specification
            {direction}

            # Code Requirements
            - Make the video as same length as given in the direction, dont use fade out or fade in 
            - All coordinate points must be 3D vectors of the form [x, y, 0]. Using [x, y] will cause broadcasting errors.
            - Define a class named `Slide{index}(Scene)` with a `construct(self)` method.
            - Set `self.camera.background_color = BLACK`.
            - Use `MathTex` for all text and mathematical expressions (never Tex).
            - Use **only** Manim primitives: `Polygon`, `Square`, `Circle`, `Line`, `Arrow`, `Brace`.
            - For polygons, always use vertex unpacking like: `Polygon([-2, -1], [2, -1], [2, 1])`.
            - Do **not** use any nonexistent methods (for example, `set_vertices()` or `config.text_size`).
            - For size and position:
            - Use `.scale(1.0)` to `.scale(1.3)` for emphasis.
            - Use `.to_edge(UP)`, `.move_to(ORIGIN)`, `.next_to(...)`, or `.shift(...)` for positioning.
            - For style:
            - Shapes: `.set_stroke(WHITE, width=1)` and optional `.set_fill(<color>, opacity=<value>)`.
            - Text: consistent scaling and color as per spec.
            - Follow 3Blue1Brown visual grammar:
            - Background: BLACK
            - Colors: YELLOW, BLUE_C, GREEN_C, RED_C
            - Thin white outlines, soft color opacity.
            - **Output only the Python code.**
            - **Do not include markdown fences, comments, or explanations.**
            """


def visual_review_prompt(direction, code):
    return f"""
            You are a visual reviewer for Manim slides with tolerance awareness.

            You are given:
            1. A rendered Manim slide image (attached below).
            2. The textual specification describing how the slide should look:

            {direction}

            # The code that has generated the image
            {code}

            Your job:
            - Make sure no two things overlaps
            - Make sure every shape is inside the image fully, no shape is touching the border of the image
            - Evaluate if the image visually matches the specification **to the human eye**.
            - Ignore tiny geometric or typographic deviations (within ~10% size or 0.2 units shift).
            - Focus only on meaningful differences: missing elements, wrong colors, or major misplacement.

            Decision criteria:
            1. If all major elements exist, colors are approximately correct, and text is readable and near its intended location -> reply **accepted**.
            2. Otherwise, reply **rejected:** followed by concise issue list and specific code-level fixes.

            Output format (strictly follow):
            accepted
            -- OR --
            rejected:
            - Issue: <short, clear mismatch>
            Fix: <specific code-level instruction>

            Rules:
            - Give specific feedback as given in the directions , not some vague something thing is off type feedback
            - If You cant see the image say to increase the video length by 1 sec
            - You can see the image — never say otherwise.
            - Ignore very small differences in font size, stroke width, or exact coordinates.
            - Accept if the slide looks visually correct, even if the code differs slightly.
            - Only reject for substantial visual errors (wrong color, missing text, wrong shape, unreadable label, misplaced geometry).
            - Estimate small fix magnitudes (e.g., "shift DOWN*0.3", "set_fill(RED_C, opacity=0.8)").
            """
