def director_prompt(topic, script):
    return f""" You are preparing slides for the topic {topic}, here is the already prepared script{script}, you have elaborate the visuals numerally and textually with utmost precision

        # 3Blue1Brown Visual Grammar
        - Background: always dark (BLACK or #0B0C10)
        - Palette: YELLOW, BLUE_C, GREEN_C, RED_C only.
        - Shapes: use simple Manim primitives (Line, Polygon, Circle, Square, Tex, MathTex, Arrow, Brace).
        - Center important math objects; avoid clutter.
        - Text must be LaTeX (`MathTex`), not plain strings.
        - Font size small but readable; consistent across slides.
        - Use thin white outlines and soft opacity for clarity.
        - Never use external images or complex textures.

        # Rules 
        - Each instruction should contain all about a single slide
        - Explain which shape, text, position to be drawn in the slide exactly 
        - Dont give vague instruction be deterministic
        - Give proper instructions about the orientation and position of the shapes
        - The slides should contain as minimum text as possible
        - The slide instructions is for a coding agent to code dont give unnecessary comments
        - Just write specfic object and where it should be 
        - Follow a similar font size throught the instructions 
        - Be specific on the sizes and symbols and colors used througout the instructions
        - Make sure the instructions make sense indepentdently 
        - External images cant be used only simple shapes can be made, which is possible using library manim 

        # Example
        ["Slide 1: Title Slide, Background: BLACK, Text: MathTex(r'\\text{{Pythagoras Theorem}}, Color: YELLOW', Position: Centered, Font size: Large", "Slide 2: Right-angled triangle, Background: BLACK, Shape: Polygon, vertices=[[-2, -1], [2, -1], [2, 1]], Color: BLUE_C, Outline: White, thin, Labels: a, b, c, Position: a near side [-2, -1] to [2, -1], b near side [2, -1] to [2, 1], c near side [-2, -1] to [2, 1], Color: YELLOW, Text: MathTex('a'), Position: below side a, Text: MathTex('b'), Position: right of side b, Text: MathTex('c'), Position: near hypotenuse c, Font size: Medium"]
         """

